# Use an official Node.js runtime. 'alpine' is a very small version.
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json for dependency installation
# This is also cached to speed up builds.
COPY webhook-ingestor/package*.json ./

# Install app dependencies (includes Prisma)
RUN npm install

# Copy webhook-ingestor source code
COPY webhook-ingestor/ .

# Copy Prisma schema from dashboard directory (needed for Prisma Client generation)
COPY dashboard/prisma ./prisma

# Generate Prisma Client (requires @prisma/client which we installed above)
RUN npx prisma generate --schema=./prisma/schema.prisma

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Define the command to run the app
CMD ["node", "index.js"]
