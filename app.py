import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from integrations.slack_integration import SlackIntegration
from config import get_platform

app = Flask(__name__)

# Create an instance of the platform integration (Slack for now)
platform = get_platform()

# Define the root route for a quick "Hello, World!" check
@app.route("/")
def hello_world():
    return "Hello, World! The Flask app is running!"

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
    # Check if we should use ngrok based on the .env variable
    use_ngrok = os.getenv("USE_NGROK", "False").lower() == "true"

    if use_ngrok:
        from pyngrok import ngrok

        # Start NGROK and get the public URL
        ngrok_tunnel = ngrok.connect(3000)

        # Extract the actual public URL from the tunnel object
        public_url = ngrok_tunnel.public_url

        # Append the /events endpoint to the NGROK URL
        full_url = f"{public_url}/events"

        # Print the URL to the console for easy copy-paste
        print(f"ngrok tunnel opened: {public_url}")
        print(f"Slack Event Subscription URL: {full_url}")

    # Run the Flask app
    app.run(port=3000)
