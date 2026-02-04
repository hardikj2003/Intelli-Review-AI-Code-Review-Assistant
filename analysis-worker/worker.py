import pika
import json
import os
import requests
import time # Import the time library 
from openai import OpenAI
from dotenv import load_dotenv
from github import Github, Auth

# --- Configuration ---
load_dotenv()
# Get RabbitMQ URL from environment variable (fallback for local dev)
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@intelli-review-rabbitmq:5672/")
CONSUME_QUEUE = 'pr_analysis_jobs'
PUBLISH_QUEUE = 'comment_jobs'

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY: raise ValueError("OPENAI_API_KEY not found in environment")
openai_client = OpenAI(api_key=OPENAI_API_KEY)
# --- End Configuration ---


def get_pr_diff(repo_full_name, pr_number, github_token):
    """Fetches the diff of a pull request using its diff_url."""
    try:
        print(f"🔎 Fetching diff for PR #{pr_number} in repo {repo_full_name}...")
        auth = Auth.Token(github_token)
        github_client = Github(auth=auth)
        repo = github_client.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        
        response = requests.get(pr.diff_url, headers={'Authorization': f'token {github_token}'})
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"🔴 Failed to fetch PR diff: {e}")
        return None


def analyze_code_with_ai(code_diff):
    """Analyzes a code diff using OpenAI."""
    print("🤖 Asking OpenAI to analyze the code diff...")
    system_prompt = (
        "You are an expert senior software engineer doing a code review. "
        "Analyze the following code diff for potential bugs, security vulnerabilities, "
        "performance issues, and deviations from standard best practices. "
        "Provide your feedback as a concise, actionable list."
    )
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": code_diff}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"🔴 AI analysis failed: {e}")
        return "Error: Could not get analysis from OpenAI."


def process_message(channel, method, properties, body):
    """Callback function to process a message from the queue."""
    print("📥 Received a new analysis job.")
    payload = json.loads(body.decode('utf-8'))
    
    # Extract metadata (user token and info)
    meta = payload.get("_meta", {})
    user_access_token = meta.get("userAccessToken")
    userId = meta.get("userId")
    
    repo_name = payload.get("repository", {}).get("full_name")
    pr_number = payload.get("number")

    if not repo_name or not pr_number:
        print("🔴 Invalid payload: missing repository or PR number.")
        channel.basic_ack(delivery_tag=method.delivery_tag)
        return

    if not user_access_token:
        print("🔴 Invalid payload: missing user access token.")
        channel.basic_ack(delivery_tag=method.delivery_tag)
        return

    print(f"👤 Processing job for user {userId}")

    diff = get_pr_diff(repo_name, pr_number, user_access_token)
    
    if diff:
        ai_feedback = analyze_code_with_ai(diff)
        print("\n--- AI Code Review ---")
        print(ai_feedback)
        print("----------------------\n")
        
        result_payload = {
            "repo_full_name": repo_name,
            "pr_number": pr_number,
            "ai_feedback": ai_feedback,
            "_meta": meta  # Forward user metadata to commenter
        }
        
        try:
            print(f"⏩ Publishing result to queue '{PUBLISH_QUEUE}'...")
            channel.basic_publish(
                exchange='',
                routing_key=PUBLISH_QUEUE,
                body=json.dumps(result_payload),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            print("✅ Result published successfully.")
        except Exception as e:
            print(f"🔴 FAILED to publish result to queue: {e}")
    
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    """Main function to connect to RabbitMQ and start consuming messages."""
    print("▶️ AI Worker is starting...")
    connection = None
    attempts = 10
    # --- This is the new retry logic ---
    for i in range(attempts):
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            print("✅ AI Worker connected to RabbitMQ.")
            break
        except pika.exceptions.AMQPConnectionError:
            print(f"🔴 RabbitMQ not ready. Retrying in 5 seconds... ({i+1}/{attempts})")
            time.sleep(5)
    
    if not connection:
        print("🔴 Could not connect to RabbitMQ after several attempts. Exiting.")
        return
    # --- End of retry logic ---

    channel = connection.channel()
    channel.queue_declare(queue=CONSUME_QUEUE, durable=True)
    channel.queue_declare(queue=PUBLISH_QUEUE, durable=True)
    
    channel.basic_consume(queue=CONSUME_QUEUE, on_message_callback=process_message, auto_ack=False)
    print(f"👂 Worker is waiting for jobs on queue '{CONSUME_QUEUE}'. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('⏹️ Worker is shutting down.')