import os
import requests
from flask import jsonify
from dotenv import load_dotenv
from discord import Webhook, RequestsWebhookAdapter
from integrations.platform_interface import PlatformIntegration

# Load environment variables from .env
load_dotenv()

class DiscordIntegration(PlatformIntegration):
    def __init__(self):
        # Load Discord bot token and trigger group from the environment
        self.bot_token = os.getenv("DISCORD_BOT_TOKEN")
        if not self.bot_token:
            raise ValueError("Missing DISCORD_BOT_TOKEN in the .env file.")
        
        self.allowed_users = self.load_allowed_users()

    def load_allowed_users(self):
        """Load the Discord trigger group from the environment variable."""
        users_str = os.getenv("DISCORD_TRIGGER_GROUP")
        if not users_str:
            raise ValueError("Missing DISCORD_TRIGGER_GROUP in the .env file.")
        
        # Convert the string to a list of allowed user IDs
        return users_str.split(",")

    def handle_event(self, data):
        print(f"Received event data: {data}")

        # Extract user ID from the event data
        user_id = data.get("user_id")
        if not user_id:
            print("No user ID found in the event data.")
            return jsonify({"status": "No user ID found in the event data"}), 400

        # Check if the user is allowed to trigger workflows
        if user_id not in self.allowed_users:
            print(f"Unauthorized user: {user_id}. Access denied.")
            return jsonify({"status": "Access denied: unauthorized user"}), 403

        # Extract event type (e.g., message, reaction) and process it
        event_type = data.get("type")
        if event_type == "message_create":
            return self.process_message(data)
        elif event_type == "reaction_add":
            return self.process_reaction(data)
        
        print("Event not recognized.")
        return {"status": "Event not recognized"}, 200

    def process_message(self, data):
        """Process a Discord message event."""
        print(f"Processing message: {data['content']}")
        message_content = data.get("content")
        channel_id = data.get("channel_id")
        
        if not message_content or not channel_id:
            return jsonify({"status": "Invalid message data"}), 400

        # Process message content (you can add logic similar to Slack here)
        # For example, checking for URLs, fetching article content, etc.
        urls = self.extract_urls_from_text(message_content)
        if urls:
            for url in urls:
                article_content = self.fetch_article(url)
                if article_content:
                    # Here you could process the article with an LLM or other logic
                    summary = self.process_article_with_llm(article_content)
                    print(f"Article summary: {summary}")
                    self.send_message(channel_id, summary)

        return jsonify({"status": "Message processed"}), 200

    def process_reaction(self, data):
        """Process a Discord reaction event."""
        print(f"Processing reaction: {data['emoji']['name']}")
        emoji = data['emoji']['name']
        channel_id = data['channel_id']
        message_id = data['message_id']

        if emoji == "newspaper":
            print("Processing reaction ':newspaper:'")
            self.fetch_message(message_id, channel_id)
            return jsonify({"status": "Reaction processed"}), 200
        
        print(f"Reaction '{emoji}' not handled.")
        return jsonify({"status": "Reaction not handled"}), 200

    def fetch_message(self, message_id, channel_id):
        """Fetch a message from Discord."""
        url = f"https://discord.com/api/channels/{channel_id}/messages/{message_id}"
        headers = {
            "Authorization": f"Bot {self.bot_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            message = response.json()
            print(f"Fetched message: {message['content']}")
            return message
        else:
            print(f"Failed to fetch message. Status code: {response.status_code}")
            return None

    def send_message(self, channel_id, content):
        """Send a message to a Discord channel."""
        url = f"https://discord.com/api/channels/{channel_id}/messages"
        headers = {
            "Authorization": f"Bot {self.bot_token}",
            "Content-Type": "application/json"
        }
        data = {
            "content": content
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("Message sent successfully")
        else:
            print(f"Failed to send message. Status code: {response.status_code}")
        return response.json()

    def extract_urls_from_text(self, text):
        """Extract URLs from message text (implement this as needed)."""
        # Logic to extract URLs from the text
        return []

    def fetch_article(self, url):
        """Fetch article content from a URL (similar to Slack implementation)."""
        print(f"Fetching article from URL: {url}")
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article.text
        except Exception as e:
            print(f"Error fetching article: {e}")
            return None

    def process_article_with_llm(self, article_content):
        """Process an article using an LLM (you can integrate your LLM logic here)."""
        # Logic to process article with an LLM or similar (could be OpenAI, GPT-4, etc.)
        return f"Processed article content: {article_content[:200]}..."
