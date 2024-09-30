import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pyngrok import ngrok
from integrations.slack_integration import SlackIntegration  # Example for Slack
from config import get_platform, get_ngrok_url

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Create an instance of the platform integration (can be Slack, Zulip, etc.)
platform = get_platform()

# Define the root route for a quick "Hello, World!" check
@app.route("/")
def hello_world():
    return "Hello, World! The Flask app is running via ngrok!"

# Route for platform-specific events
@app.route("/events", methods=["POST"])
def events():
    data = request.json
    if data is None:
        return jsonify({"error": "Invalid data format"}), 400

    # Delegate to the platform-specific handler
    response = platform.handle_event(data)
    return response

if __name__ == "__main__":
    # Start NGROK and get the public URL
    public_url = get_ngrok_url()
    print(f"ngrok tunnel opened: {public_url} NOTE: Don't forget to add /events in your platform Event Subscriptions")

    # Run the Flask app
    app.run(port=3000)
