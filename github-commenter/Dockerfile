# Use an official Python runtime as a parent image. We use 'slim' for a smaller size.
FROM python:3.11-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the requirements file into the container at /app
# We copy this first to take advantage of Docker's layer caching.
# The dependencies will only be re-installed if this file changes.
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code from the current directory into /app
COPY . .

# Define the command to run your app
CMD ["python", "commenter.py"]
