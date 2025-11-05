// Import the Express library, our web framework
const express = require("express");
const amqp = require("amqplib");
const { PrismaClient } = require("@prisma/client");
const crypto = require("crypto");

const app = express();
const PORT = process.env.PORT || 3000;

const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://guest:guest@rabbitmq:5672/';
const QUEUE_NAME = "pr_analysis_jobs";
const DATABASE_URL = process.env.DATABASE_URL;

if (!DATABASE_URL) {
  console.error("❌ DATABASE_URL environment variable is required");
  process.exit(1);
}

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: DATABASE_URL,
    },
  },
});

app.use(express.json());

// Helper function to verify webhook signature
function verifyWebhookSignature(payload, signature, secret) {
  if (!secret) {
    console.warn("⚠️ No webhook secret configured for this repo");
    return true; // Allow if no secret is set (for backwards compatibility)
  }
  
  const hmac = crypto.createHmac("sha256", secret);
  const digest = "sha256=" + hmac.update(JSON.stringify(payload)).digest("hex");
  
  const providedSignature = signature || "";
  return crypto.timingSafeEqual(
    Buffer.from(digest),
    Buffer.from(providedSignature)
  );
}

// Define a POST route for our webhook
app.post("/api/webhook", async (req, res) => {
  const githubSignature = req.headers["x-hub-signature-256"];
  const githubEvent = req.headers["x-github-event"];
  
  console.log(`🎉 Webhook received! Event: ${githubEvent}`);
  
  // Only process pull_request events
  if (githubEvent !== "pull_request") {
    return res.status(200).send("Event ignored (not a pull_request event).");
  }

  const payload = req.body;
  const repoFullName = payload.repository?.full_name;
  const prAction = payload.action;

  // Only process opened, synchronize, and reopened actions
  if (!["opened", "synchronize", "reopened"].includes(prAction)) {
    return res.status(200).send(`PR action '${prAction}' ignored.`);
  }

  if (!repoFullName) {
    console.error("🔴 No repository full_name in payload");
    return res.status(400).send("Invalid webhook payload: missing repository information.");
  }

  try {
    // Look up the repository in our database
    const repo = await prisma.repository.findUnique({
      where: { fullName: repoFullName },
      include: {
        user: {
          include: {
            accounts: {
              where: { provider: "github" },
            },
          },
        },
      },
    });

    if (!repo || !repo.enabled) {
      console.log(`⏭️ Repository ${repoFullName} is not enabled or not found`);
      return res.status(200).send("Repository not enabled for Intelli-Review.");
    }

    // Verify webhook signature if secret is configured
    if (repo.webhookSecret) {
      const isValid = verifyWebhookSignature(req.body, githubSignature, repo.webhookSecret);
      if (!isValid) {
        console.error("🔴 Invalid webhook signature");
        return res.status(401).send("Invalid webhook signature.");
      }
    }

    const userAccount = repo.user.accounts[0];
    if (!userAccount || !userAccount.access_token) {
      console.error(`🔴 No GitHub access token found for user ${repo.userId}`);
      return res.status(500).send("User authentication token not found.");
    }

    // Prepare the message with user context
    const enrichedMessage = {
      ...payload,
      _meta: {
        userId: repo.userId,
        userAccessToken: userAccount.access_token,
        repoId: repo.id,
      },
    };

    // Connect to RabbitMQ server
    const connection = await amqp.connect(RABBITMQ_URL);
    // Create a channel
    const channel = await connection.createChannel();

    // Assert a queue exists. If it doesn't, it will be created.
    // durable: true means the queue will survive broker restarts.
    await channel.assertQueue(QUEUE_NAME, { durable: true });

    // Send the enriched message to the queue
    channel.sendToQueue(QUEUE_NAME, Buffer.from(JSON.stringify(enrichedMessage)), { persistent: true });

    console.log(`✅ Message sent to queue '${QUEUE_NAME}' for repo ${repoFullName}`);

    // Close the channel and connection
    await channel.close();
    await connection.close();
  } catch (error) {
    console.error("🔴 Error processing webhook:", error);
    // If we can't queue the job, we should respond with an error.
    return res.status(500).send("Error processing webhook.");
  }

  // Respond to GitHub to let them know we've received the webhook.
  // If GitHub doesn't receive a 2xx response, it will consider the delivery a failure.
  res.status(202).send("Webhook accepted and queued for processing.");
});

// A simple GET route for the root URL to confirm the server is running.
app.get("/", (req, res) => {
  res.send("Intelli-Review Webhook Ingestor is alive!");
});

// Start the server and make it listen for connections on the specified port.
app.listen(PORT, () => {
  console.log(`🚀 Server is running on http://localhost:${PORT}`);
});
