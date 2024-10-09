import os
import requests
from flask import jsonify
from dotenv import load_dotenv
from newspaper import Article
from integrations.platform_interface import PlatformIntegration
from processors.llm_processor import process_article_with_llm
from utils.article_processing import extract_urls_from_text

# Load environment variables from .env
load_dotenv()

# A set to track processed message timestamps to prevent reprocessing
processed_messages = set()

class SlackIntegration(PlatformIntegration):
    def __init__(self):
        # Load workspace tokens from environment
        self.workspace_tokens = self.load_workspace_tokens()

    def load_workspace_tokens(self):
        """Load the Slack bot tokens from the environment variable and return them as a dictionary."""
        tokens_str = os.getenv("SLACK_BOT_USER_OAUTH_TOKENS")
        if not tokens_str:
            raise ValueError("Missing SLACK_BOT_USER_OAUTH_TOKENS in the .env file.")
        
        # Parse the tokens string and convert it into a dictionary
        tokens = {}
        for pair in tokens_str.split(","):
            team_id, token = pair.split(":")
            tokens[team_id] = token
        return tokens

    def get_token_for_workspace(self, team_id):
        """Retrieve the Slack token for a given workspace based on the team_id."""
        token = self.workspace_tokens.get(team_id)
        if not token:
            raise ValueError(f"Token for workspace {team_id} not found. Please check your .env configuration.")
        return token

    def test_auth(self, team_id):
        """Test Slack API authentication and log the result."""
        bot_token = self.get_token_for_workspace(team_id)
        url = "https://slack.com/api/auth.test"
        headers = {
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        auth_info = response.json()

        # Log the auth info to the console
        if auth_info.get("ok"):
            print(f"Authentication successful! Bot User ID: {auth_info['user_id']}, Team: {auth_info['team']}")
        else:
            print(f"Authentication failed: {auth_info.get('error')}")

    def handle_event(self, data):
        print(f"Received event data: {data}")

        # Handle Slack's URL verification event
        if data.get("type") == "url_verification":
            print("Responding to Slack verification challenge.")
            return data["challenge"], 200, {"Content-Type": "text/plain"}

        # Get team_id from the event data to determine the correct token
        team_id = data.get("team_id")
        if not team_id:
            raise ValueError("team_id not found in the event data.")

        # Test authentication for the workspace (team_id)
        self.test_auth(team_id)

        if "event" in data:
            event_type = data["event"]["type"]
            print(f"Detected event type: {event_type}")

            if event_type == "message" and "subtype" not in data["event"]:
                print(f"New message event in channel {data['event']['channel']}, but waiting for a reaction before processing.")
                return jsonify({"status": "Message event received but ignored"}), 200

            elif event_type == "reaction_added":
                print(f"Processing reaction added event for reaction {data['event']['reaction']}")
                return self.process_reaction(data["event"], team_id)

        print("Event not recognized or no 'event' field found.")
        return {"status": "Event not recognized"}, 200

    def process_message(self, text, channel, thread_ts, team_id):
        print(f"Processing message: {text}")
        urls = extract_urls_from_text(text)
        if urls:
            print(f"Found URLs in message: {urls}")
            for url in urls:
                article_content = self.fetch_article(url)
                if article_content:
                    summary = process_article_with_llm(article_content)
                    print(f"Article summary: {summary}")

                    # Send the summary as a reply in the thread
                    self.send_message(channel, summary, thread_ts, team_id)

                    return jsonify({"summary": summary}), 200
        else:
            print("No URLs found in the message.")
        return jsonify({"status": "No URLs found"}), 200

    def process_reaction(self, event, team_id):
        reaction = event["reaction"]
        message_ts = event["item"]["ts"]
        channel = event["item"]["channel"]

        print(f"Detected reaction: {reaction}")

        # Ensure that we only process the same message once by using its timestamp
        if message_ts in processed_messages:
            print(f"Message {message_ts} already processed, skipping.")
            return {"status": "Message already processed"}, 200

        if reaction == "newspaper":
            print("Processing reaction ':newspaper:'")

            # Add message timestamp to the processed_messages set to avoid reprocessing
            processed_messages.add(message_ts)

            # Ensure the bot does not respond to its own messages
            return self.fetch_message(message_ts, channel, message_ts, team_id)

        print(f"Reaction '{reaction}' not handled.")
        return {"status": "Reaction not handled"}, 200

    def fetch_article(self, url):
        print(f"Fetching article from URL: {url}")
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article.text
        except Exception as e:
            print(f"Error fetching article: {e}")
            return None

    def fetch_message(self, message_id, channel, thread_ts, team_id):
        print(f"Fetching message with ID {message_id} from channel {channel}")

        bot_token = self.get_token_for_workspace(team_id)
        formatted_ts = f"{float(message_id):.6f}"

        # Use the conversations.info API to get channel details (for both public and private)
        info_url = "https://slack.com/api/conversations.info"
        headers = {
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/json"
        }
        params = {
            "channel": channel
        }

        # Check the channel type (public or private)
        info_response = requests.get(info_url, headers=headers, params=params)
        response_json = info_response.json()

        if info_response.status_code != 200 or not response_json.get("ok", False):
            print(f"Failed to retrieve channel info: {response_json}")
            if response_json.get("error") == "channel_not_found":
                print(f"Error: Bot may not be a member of the private channel {channel}. Please invite the bot to the channel.")
            return {"status": "Failed to retrieve channel info"}, 500

        # Use conversations.history for fetching messages (works for both public and private)
        url = "https://slack.com/api/conversations.history"

        # Fetch the message history
        params = {
            "channel": channel,
            "latest": formatted_ts,  # Use the formatted timestamp
            "limit": 1,
            "inclusive": True
        }

        response = requests.get(url, headers=headers, params=params)

        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.json()}")

        # Check for successful API response
        if response.status_code == 200:
            response_json = response.json()

            # Check if the API response is okay and contains messages
            if not response_json.get("ok", False):
                print(f"Slack API error: {response_json.get('error')}")
                return {"status": "Slack API error", "error": response_json.get("error")}, 500

            messages = response_json.get("messages", [])

            if messages:
                message = messages[0]

                # Avoid recursive processing if the message is from the bot itself
                if 'bot_id' in message:
                    print("Ignoring message from the bot to prevent recursion.")
                    return {"status": "Ignored bot's own message"}, 200

                print(f"Fetched message: {message['text']}")
                return self.process_message(message["text"], channel, thread_ts, team_id)

            print(f"No messages found for message_id {formatted_ts}")
            return {"status": "No messages found"}, 404
        else:
            print(f"Failed to fetch message. Status code: {response.status_code}")
            return {"status": "Failed to fetch message"}, response.status_code

    def send_message(self, channel, message, thread_ts=None, team_id=None):
        bot_token = self.get_token_for_workspace(team_id)
        print(f"Sending message to channel {channel}: {message}")
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/json"
        }
        data = {
            "channel": channel,
            "text": message
        }

        # If thread_ts is provided, send as a threaded reply
        if thread_ts:
            data["thread_ts"] = thread_ts

        response = requests.post(url, headers=headers, json=data)
        print(f"Message sent. Response: {response.json()}")
        return response.json()
