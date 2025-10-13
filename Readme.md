
# Intelli-Review 🤖✨

An **AI-powered code review assistant** built with a full-stack, event-driven microservices architecture.  
This tool automatically reviews GitHub pull requests, providing intelligent feedback on potential bugs, performance issues, and best practices to accelerate the development lifecycle.

---

## ⚙️ Core Features

- **Automated AI Analysis:** Leverages the OpenAI API (`gpt-4o-mini`) to provide intelligent, context-aware code reviews.  
- **Full-Stack Dashboard:** Modern Next.js + TypeScript frontend for GitHub login, repo management, and enabling/disabling AI reviews.  
- **Event-Driven Backend:** Microservices (Node.js & Python) communicating asynchronously via **RabbitMQ** for high reliability.  
- **Persistent Storage:** PostgreSQL database with **Prisma ORM** to store user, repo, and configuration data.  
- **Secure Authentication:** Built with **NextAuth.js** using GitHub OAuth2.  
- **Containerized & Deployable:** Fully orchestrated via **Docker Compose**, enabling one-command deployment.  

---

## 🧠 Tech Stack & Architecture

| Layer | Technology |
|-------|-------------|
| **Frontend** | Next.js, React, TypeScript, Tailwind CSS |
| **Backend Services** | Node.js (Ingestor), Python (AI Worker & Commenter) |
| **Database** | PostgreSQL + Prisma ORM |
| **Message Broker** | RabbitMQ |
| **AI Engine** | OpenAI API |
| **Auth** | NextAuth.js |
| **Containerization** | Docker & Docker Compose |

---

## 🏗️ System Architecture

*(Insert your architecture diagram here — this is a major highlight for recruiters!)*  
It should demonstrate how the **Ingestor**, **AI Worker**, **Commenter**, and **Dashboard** interact via **RabbitMQ** and **PostgreSQL**.

---

## 🧰 Getting Started (Run Locally)

Follow these steps to set up and run Intelli-Review on your local machine.

---

### 1️⃣ Prerequisites

- [Git](https://git-scm.com/)
- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (v3.9+)
- [Docker & Docker Compose](https://www.docker.com/)

---

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/intelli-review.git
cd intelli-review
````

---

### 3️⃣ Configure Backend Environment

Create `.env` files for both Python services:

* `analysis-worker/.env`
* `github-commenter/.env`

Each should contain:

```bash
# Required for both analysis-worker/.env and github-commenter/.env
OPENAI_API_KEY="sk-..."
GITHUB_TOKEN="github_pat_..."
```

---

### 4️⃣ Configure Frontend Environment

Create a `.env` file in the `dashboard/` directory (`dashboard/.env`):

```bash
# dashboard/.env

# GitHub OAuth App Credentials
GITHUB_ID="your_github_client_id"
GITHUB_SECRET="your_github_client_secret"

# NextAuth.js Configuration
NEXTAUTH_URL="http://localhost:3001"
NEXTAUTH_SECRET="generate_a_secret_key_using_openssl_rand_hex_32"

# Database Connection
DATABASE_URL="postgresql://myuser:mypassword@localhost:5432/mydatabase"

# Webhook Ingestor (use ngrok for local testing)
WEBHOOK_INGESTOR_URL="https://your-ngrok-url.ngrok-free.app"
```

---

### 5️⃣ Launch the Application

The system is fully orchestrated with Docker Compose.

**Run the Backend:**

```bash
docker-compose up --build
```

**Run the Frontend:**

```bash
cd dashboard
npm install
npx prisma db push    # Apply Prisma schema
npm run dev
```

**Expose Your Webhook (for local testing):**

```bash
ngrok http 3000
```

> ⚠️ Update your `WEBHOOK_INGESTOR_URL` in `dashboard/.env` with the new ngrok URL.

---

### ✅ Access the App

* **Dashboard:** [http://localhost:3001](http://localhost:3001)
* **Backend Services:** Running via Docker
* **Webhook Endpoint:** Exposed via ngrok

---

## 🌐 Deployment

You can deploy the stack using any cloud provider that supports Docker (e.g., AWS ECS, Render, Railway, DigitalOcean).
Simply set environment variables in the platform dashboard and run:

```bash
docker-compose up -d
```

---

## 🧩 Future Enhancements

* Multi-language AI code review (Java, C++, Go, etc.)
* Slack & Discord PR notifications
* Real-time dashboard analytics
* AI-based code summarization

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to fork the repo and submit a PR.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using Next.js, Node.js, Python, and OpenAI**

```
```
