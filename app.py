import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config import get_platform

app = Flask(__name__)

# Get the platform specified in the .env file
platform_name = os.getenv("PLATFORM", "").lower()

if platform_name == "slack":
    try:
        # Create an instance of the Slack integration
        platform = get_platform()
        print(f"Platform initialized successfully: {platform.__class__.__name__}")
    except ValueError as e:
        print(f"Error initializing platform: {e}")
        platform = None

    # Define the root route for a quick "Hello, World!" check
    @app.route("/")
    def hello_world():
        if platform:
            return f"Hello, World! The Flask app is running with {platform.__class__.__name__}!"
        else:
            return "Hello, World! Platform configuration error. Check logs for details."

    # Route for platform-specific events
    @app.route("/events", methods=["POST"])
    def events():
        if not platform:
            return jsonify({"error": "Platform not configured correctly."}), 500

        data = request.json
        if data is None:
            return jsonify({"error": "Invalid data format"}), 400

        # Delegate to the platform-specific handler
        response = platform.handle_event(data)
        return response

    if __name__ == "__main__":
        app.run(port=3000)

elif platform_name == "discord":
    from integrations.discord_integration import DiscordIntegration

    if __name__ == "__main__":
        # Initialize and run the Discord bot
        integration = DiscordIntegration()
        integration.run()
else:
    print(f"Unsupported platform specified: {platform_name}. Please update your .env file.")
