# webhook-ingestor/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy dependency files first (cache friendly)
COPY webhook-ingestor/package*.json ./
RUN npm install

# Copy application source
COPY webhook-ingestor/ .

# Copy Prisma schema from dashboard
COPY dashboard/prisma ./prisma

# Generate Prisma Client (NO DB connection needed)
RUN npx prisma generate --schema=./prisma/schema.prisma

EXPOSE 3000

# Start the app
CMD ["npm", "start"]
