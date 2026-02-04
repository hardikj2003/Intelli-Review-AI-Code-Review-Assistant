import pika
import json
import os
import time # Import the time library
from github import Github, Auth
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
# Get RabbitMQ URL from environment variable (fallback for local dev)
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@intelli-review-rabbitmq:5672/")
QUEUE_NAME = 'comment_jobs'
# --- End Configuration ---


def post_comment_to_pr(repo_full_name, pr_number, comment_body, github_token):
    """Posts a comment to a specific pull request on GitHub."""
    try:
        print(f"✍️ Posting comment to PR #{pr_number} in {repo_full_name}...")
        auth = Auth.Token(github_token)
        github_client = Github(auth=auth)
        repo = github_client.get_repo(repo_full_name)
        pr_as_issue = repo.get_issue(number=pr_number)
        formatted_comment = f"### 🤖 Intelli-Review Analysis\n\n---\n\n{comment_body}"
        pr_as_issue.create_comment(formatted_comment)
        print("✅ Comment posted successfully.")
        return True
    except Exception as e:
        print(f"🔴 Failed to post comment: {e}")
        return False


def process_message(channel, method, properties, body):
    """Callback function to process a message from the queue."""
    print("📥 Received a new comment job.")
    payload = json.loads(body.decode('utf-8'))
    
    repo_name = payload.get("repo_full_name")
    pr_number = payload.get("pr_number")
    feedback = payload.get("ai_feedback")
    
    # Extract user access token from metadata
    meta = payload.get("_meta", {})
    user_access_token = meta.get("userAccessToken")
    userId = meta.get("userId")

    if not all([repo_name, pr_number, feedback]):
        print("🔴 Invalid payload received. Missing required fields.")
        channel.basic_ack(delivery_tag=method.delivery_tag)
        return

    if not user_access_token:
        print("🔴 Invalid payload received. Missing user access token.")
        channel.basic_ack(delivery_tag=method.delivery_tag)
        return

    print(f"👤 Posting comment for user {userId}")
    post_comment_to_pr(repo_name, pr_number, feedback, user_access_token)
    
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    """Main function to connect to RabbitMQ and start consuming messages."""
    print("▶️ GitHub Commenter is starting...")
    connection = None
    attempts = 10
    # --- This is the new retry logic ---
    for i in range(attempts):
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            print("✅ GitHub Commenter connected to RabbitMQ.")
            break
        except pika.exceptions.AMQPConnectionError:
            print(f"🔴 RabbitMQ not ready. Retrying in 5 seconds... ({i+1}/{attempts})")
            time.sleep(5)

    if not connection:
        print("🔴 Could not connect to RabbitMQ after several attempts. Exiting.")
        return
    # --- End of retry logic ---

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_message, auto_ack=False)
    print(f"👂 Commenter is waiting for jobs on queue '{QUEUE_NAME}'. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('⏹️ Commenter is shutting down.')