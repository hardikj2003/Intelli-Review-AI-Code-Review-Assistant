// Import the Express library, our web framework
const express = require("express");
const amqp = require("amqplib");

const app = express();
const PORT = process.env.PORT || 3000;
// Use the service name 'rabbitmq' as the hostname
const RABBITMQ_URL = 'amqp://guest:guest@rabbitmq:5672/';
const QUEUE_NAME = "pr_analysis_jobs";

app.use(express.json());

// Define a POST route for our webhook
app.post("/api/webhook", async (req, res) => {
  console.log("🎉 Webhook received!");
  console.log("Payload:", JSON.stringify(req.body, null, 2));

  try {
    // Connect to RabbitMQ server
    const connection = await amqp.connect(RABBITMQ_URL);
    // Create a channel
    const channel = await connection.createChannel();

    // Assert a queue exists. If it doesn't, it will be created.
    // durable: true means the queue will survive broker restarts.
    await channel.assertQueue(QUEUE_NAME, { durable: true });

    // Prepare the message. We send the request body as a stringified JSON.
    const message = JSON.stringify(req.body);

    // Send the message to the queue.
    // We use a Buffer because it's the standard way to send data.
    channel.sendToQueue(QUEUE_NAME, Buffer.from(message), { persistent: true });

    console.log(`✅ Message sent to queue '${QUEUE_NAME}'`);

    // Close the channel and connection
    await channel.close();
    await connection.close();
  } catch (error) {
    console.error("🔴 Error sending message to RabbitMQ:", error);
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
