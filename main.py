import os
from flask import Flask, request, jsonify
from pyngrok import ngrok

app = Flask(__name__)

# Define the root route for a quick "Hello, World!" check
@app.route("/")
def hello_world():
    return "Hello, World! The Flask app is running via ngrok!"

# Route for Slack events
@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json

    # Handle Slack URL verification challenge
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    # Verify if the request is a Slack event
    if "event" in data:
        event_type = data["event"]["type"]

        # Handle new message in a channel
        if event_type == "message" and "subtype" not in data["event"]:
            user = data["event"]["user"]
            text = data["event"]["text"]
            channel = data["event"]["channel"]
            print(f"New message from {user} in channel {channel}: {text}")

            # You can send a message back to Slack here if needed
            return jsonify({"status": "Message event received"}), 200

        # Handle reaction (emoticon) added
        elif event_type == "reaction_added":
            user = data["event"]["user"]
            reaction = data["event"]["reaction"]
            item_user = data["event"]["item_user"]
            channel = data["event"]["item"]["channel"]
            print(f"User {user} added reaction :{reaction}: to a message by {item_user} in channel {channel}")

            # You can send a message back to Slack here if needed
            return jsonify({"status": "Reaction event received"}), 200

    return jsonify({"status": "Event not recognized"}), 200


if __name__ == "__main__":
    # Start an ngrok tunnel (without a custom subdomain)
    public_url = ngrok.connect(3000)
    print(f"ngrok tunnel opened at: {public_url}")

    # Run the Flask app
    app.run(port=3000)
