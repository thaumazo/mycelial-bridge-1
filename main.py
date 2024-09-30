import os
from flask import Flask, request, jsonify
from pyngrok import ngrok
import json

app = Flask(__name__)

# Define the root route for a quick "Hello, World!" check
@app.route("/")
def hello_world():
    return "Hello, World! The Flask app is running via ngrok!"

# Route for Slack events
@app.route("/slack/events", methods=["POST", "GET"])
def slack_events():
    print("Received request:")
    print(f"Method: {request.method}")
    
    # Log headers
    print(f"Headers: {dict(request.headers)}")
    
    try:
        # Try to parse the JSON data
        data = request.json
        if data is None:
            # Handle case where data might not be JSON
            print("Received non-JSON data:")
            print(request.data.decode("utf-8"))
        else:
            print("Received event:", data)  # Log the full incoming event data

        # Handle Slack URL verification challenge
        if "challenge" in data:
            return data["challenge"], 200, {"Content-Type": "text/plain"}

        # Verify if the request is a Slack event
        if "event" in data:
            event_type = data["event"]["type"]
            print(f"Event type: {event_type}")

            # Handle new message in a channel
            if event_type == "message" and "subtype" not in data["event"]:
                user = data["event"]["user"]
                text = data["event"]["text"]
                channel = data["event"]["channel"]
                print(f"New message from {user} in channel {channel}: {text}")

                return jsonify({"status": "Message event received"}), 200

            # Handle reaction (emoticon) added
            elif event_type == "reaction_added":
                user = data["event"]["user"]
                reaction = data["event"]["reaction"]
                item_user = data["event"]["item_user"]
                channel = data["event"]["item"]["channel"]
                print(f"User {user} added reaction :{reaction}: to a message by {item_user} in channel {channel}")

                return jsonify({"status": "Reaction event received"}), 200

        # Log if the event type is not recognized
        print(f"Unrecognized event: {data}")
        return jsonify({"status": "Event not recognized"}), 200

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"status": "Error", "message": str(e)}), 500

if __name__ == "__main__":
    # Start an ngrok tunnel (without a custom subdomain)
    public_url = ngrok.connect(3000)
    print(f"ngrok tunnel opened: {public_url} NOTE: Don't forget to add /slack/events in Slack Event Subscriptions")

    # Run the Flask app
    app.run(port=3000)
