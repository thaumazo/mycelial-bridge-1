import requests
from flask import jsonify
from newspaper import Article
from integrations.platform_interface import PlatformIntegration
from processors.llm_processor import process_article_with_llm
from utils.article_processing import extract_urls_from_text

# A set to track processed message timestamps to prevent reprocessing
processed_messages = set()

class SlackIntegration(PlatformIntegration):
    def __init__(self, bot_token):
        self.bot_token = bot_token

    def handle_event(self, data):
        print(f"Received event data: {data}")

        if "challenge" in data:
            print("Responding to Slack verification challenge.")
            return data["challenge"], 200, {"Content-Type": "text/plain"}

        if "event" in data:
            event_type = data["event"]["type"]
            print(f"Detected event type: {event_type}")

            # Handle the message event, but ignore subtypes (like message_changed or message_deleted)
            if event_type == "message" and "subtype" not in data["event"]:
                print(f"New message event in channel {data['event']['channel']}, but waiting for a reaction before processing.")
                return jsonify({"status": "Message event received but ignored"}), 200

            # Handle the reaction added event
            elif event_type == "reaction_added":
                print(f"Processing reaction added event for reaction {data['event']['reaction']}")
                return self.process_reaction(data["event"])

        print("Event not recognized or no 'event' field found.")
        return {"status": "Event not recognized"}, 200

    def process_message(self, text, channel, thread_ts):
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
                    self.send_message(channel, summary, thread_ts)

                    return jsonify({"summary": summary}), 200
        else:
            print("No URLs found in the message.")
        return jsonify({"status": "No URLs found"}), 200

    def process_reaction(self, event):
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
            return self.fetch_message(message_ts, channel, message_ts)

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

    def fetch_message(self, message_id, channel, thread_ts):
        print(f"Fetching message with ID {message_id} from channel {channel}")
        url = "https://slack.com/api/conversations.history"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        params = {
            "channel": channel,
            "latest": message_id,
            "limit": 1,
            "inclusive": True
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            messages = response.json().get("messages", [])
            if messages:
                message = messages[0]

                # Check if the message is from the bot itself, using the bot_id or user field
                if 'bot_id' in message:
                    print("Ignoring message from the bot to prevent recursion.")
                    return {"status": "Ignored bot's own message"}, 200

                print(f"Fetched message: {message['text']}")
                return self.process_message(message["text"], channel, thread_ts)
        
        print(f"Failed to fetch message. Status code: {response.status_code}")
        return {"status": "Failed to fetch message"}, 500    

    def send_message(self, channel, message, thread_ts=None):
        print(f"Sending message to channel {channel}: {message}")
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
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
