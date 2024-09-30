import requests
from flask import jsonify
from newspaper import Article  # Ensure this import is present
from integrations.platform_interface import PlatformIntegration
from processors.llm_processor import process_article_with_llm
from utils.article_processing import extract_urls_from_text

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

    def process_message(self, text, channel):
        print(f"Processing message: {text}")
        urls = extract_urls_from_text(text)
        if urls:
            print(f"Found URLs in message: {urls}")
            for url in urls:
                article_content = self.fetch_article(url)
                if article_content:
                    summary = process_article_with_llm(article_content)
                    print(f"Article summary: {summary}")
                    return jsonify({"summary": summary}), 200
        else:
            print("No URLs found in the message.")
        return jsonify({"status": "No URLs found"}), 200

    def process_reaction(self, event):
        reaction = event["reaction"]
        print(f"Detected reaction: {reaction}")
        
        if reaction == "newspaper":
            print("Processing reaction ':newspaper:'")
            return self.fetch_message(event["item"]["ts"], event["item"]["channel"])
        
        print(f"Reaction '{reaction}' not handled.")
        return {"status": "Reaction not handled"}, 200

    def fetch_article(self, url):
        print(f"Fetching article from URL: {url}")
        try:
            # Use Newspaper3k to extract the article content
            article = Article(url)
            article.download()
            article.parse()
            return article.text
        except Exception as e:
            print(f"Error fetching article: {e}")
            return None

    def fetch_message(self, message_id, channel):
        print(f"Fetching message with ID {message_id} from channel {channel}")
        url = "https://slack.com/api/conversations.history"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        params = {
            "channel": channel,
            "inclusive": True,  # Ensure the exact timestamp is included
            "latest": message_id,  # Use the ts of the message as 'latest'
            "limit": 1  # We are only interested in 1 message
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        # Log full response from the API
        print(f"Slack API response status code: {response.status_code}")
        response_json = response.json()
        print(f"Slack API response JSON: {response_json}")

        if response.status_code == 200 and response_json.get("ok", False):
            messages = response_json.get("messages", [])
            if messages:
                message = messages[0]
                print(f"Fetched message: {message['text']}")
                return self.process_message(message["text"], channel)
            else:
                print("No messages returned in the response.")
        else:
            print(f"Failed to fetch message. Status code: {response.status_code}")
        
        return {"status": "Failed to fetch message"}, 500

    def send_message(self, channel, message):
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
        response = requests.post(url, headers=headers, json=data)
        print(f"Message sent. Response: {response.json()}")
        return response.json()
