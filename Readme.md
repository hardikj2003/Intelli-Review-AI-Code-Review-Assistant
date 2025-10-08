Intelli-Review 🤖✨
An AI-powered code review assistant built with a full-stack, event-driven microservices architecture. This tool automatically reviews GitHub pull requests, providing intelligent feedback on potential bugs, performance issues, and best practices to accelerate the development lifecycle.

Live Demo & Walkthrough
(Pro-Tip: Use a free tool like ScreenToGif or Kap to record a short GIF of the entire workflow: enabling a repo on the dashboard, opening a PR, and seeing the AI comment appear automatically. A visual demo is incredibly powerful for recruiters.)

Core Features
Automated AI Analysis: Leverages the OpenAI API (gpt-4o-mini) to provide intelligent, context-aware code reviews.

Full-Stack Dashboard: A modern Next.js and TypeScript frontend for users to log in with their GitHub account, view their repositories, and manage the service with a single click.

Event-Driven Backend: A fully containerized system of microservices (Node.js, Python) that communicate asynchronously via a RabbitMQ message queue for high reliability.

Persistent Storage: Uses a PostgreSQL database managed via Prisma ORM to store user data, repository configurations, and session information.

Secure Authentication: Built with NextAuth.js for a secure and robust GitHub OAuth2 authentication flow.

Containerized & Deployable: The entire backend is orchestrated with Docker Compose, allowing the entire system to be launched with a single command.

Tech Stack & Architecture
Frontend: Next.js, React, TypeScript, Tailwind CSS

Backend Services: Node.js (Ingestor), Python (AI Worker & Commenter)

Database: PostgreSQL with Prisma ORM

Message Broker: RabbitMQ

AI: OpenAI API

Authentication: NextAuth.js

Containerization: Docker & Docker Compose

System Architecture
(This is a major highlight for recruiters. Take a screenshot of our architecture diagram and embed it here. It shows you can think at a system level, not just code.)

Shutterstock

Getting Started & Running Locally
Follow these steps to set up and run the project on your local machine.

1. Prerequisites
Git

Node.js (v18+)

Python (v3.9+)

Docker & Docker Compose

2. Clone the Repository
Bash

git clone https://github.com/your-username/intelli-review.git
cd intelli-review
3. Configure Backend Environment
You need to create .env files for the two Python services.

Create a file at analysis-worker/.env

Create another file at github-commenter/.env

Both files should contain the following variables:

Code snippet

# Required for both analysis-worker/.env and github-commenter/.env
OPENAI_API_KEY="sk-..."
GITHUB_TOKEN="github_pat_..."
4. Configure Frontend Environment
Create a .env file at the root of the dashboard/ directory (dashboard/.env) with the following variables:

Code snippet

# dashboard/.env

# GitHub OAuth App Credentials
GITHUB_ID="your_github_client_id"
GITHUB_SECRET="your_github_client_secret"

# NextAuth.js Configuration
NEXTAUTH_URL="http://localhost:3001"
NEXTAUTH_SECRET="generate_a_secret_key_using_openssl_rand_hex_32"

# Database Connection (to the Docker container)
DATABASE_URL="postgresql://myuser:mypassword@localhost:5432/mydatabase"

# Public URL for the Webhook Ingestor (use ngrok for local development)
WEBHOOK_INGESTOR_URL="https://your-ngrok-url.ngrok-free.app"
5. Launch the Application
The entire system is orchestrated with Docker Compose.

Run the Backend: From the root intelli-review directory, launch the containerized backend services.

Bash

docker-compose up --build
Run the Frontend: In a new terminal window, navigate to the dashboard directory.

Bash

cd dashboard
npm install
npx prisma db push  # Apply the database schema
npm run dev
Expose Your Webhook: In a third terminal window, use ngrok to expose your local ingestor service to the internet.

Bash

ngrok http 3000
(Remember to update the WEBHOOK_INGESTOR_URL in your dashboard's .env file with the URL ngrok provides.)

The dashboard will be available at http://localhost:3001, and the backend is now live and ready to receive webhooks.