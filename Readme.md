Intelli-Review 🤖✨
An AI-powered code review assistant built with a full-stack, event-driven microservices architecture. This tool automatically reviews GitHub pull requests, providing intelligent feedback on potential bugs, performance issues, and best practices.

Live Demo & Walkthrough
(Pro-Tip: Use a tool like LiceCap or ScreenToGif to record a short GIF of the entire workflow: enabling a repo on the dashboard, opening a PR, and seeing the comment appear. A GIF is incredibly powerful.)

Core Features
Automated AI Analysis: Leverages the OpenAI API to provide intelligent, context-aware code reviews.

Full-Stack Dashboard: A Next.js and TypeScript frontend for users to log in with GitHub and manage their repositories.

Event-Driven Backend: A containerized system of microservices (Node.js, Python) that communicate asynchronously via a RabbitMQ message queue.

Persistent Storage: Uses PostgreSQL managed via Prisma for storing user and repository data.

Secure Authentication: Built with NextAuth.js for secure GitHub OAuth integration.

Containerized & Deployable: The entire backend is orchestrated with Docker Compose for easy setup and deployment.

Tech Stack & Architecture
Frontend: Next.js, React, TypeScript, Tailwind CSS

Backend Services: Node.js (Ingestor), Python (AI Worker & Commenter)

Database: PostgreSQL with Prisma ORM

Message Broker: RabbitMQ

AI: OpenAI API

Containerization: Docker & Docker Compose

System Architecture
(This is incredibly impressive to recruiters. Take a screenshot of the architecture diagram we discussed and embed it here.)

Getting Started & Running Locally
Clone the repository:

git clone [https://github.com/your-username/intelli-review.git](https://github.com/your-username/intelli-review.git)
cd intelli-review

Configure Backend Environment:

Create a .env file inside analysis-worker/.

Create a .env file inside github-commenter/.

Add your OPENAI_API_KEY and GITHUB_TOKEN to both files.

Configure Frontend Environment:

Create a .env file inside dashboard/.

Add your GITHUB_ID, GITHUB_SECRET, NEXTAUTH_URL, NEXTAUTH_SECRET, and DATABASE_URL.

Run the Backend with Docker:

docker-compose up --build

Run the Frontend:

In a new terminal, navigate to the dashboard directory.

Install dependencies: npm install

Run the development server: npm run dev

The dashboard will be available at http://localhost:3001