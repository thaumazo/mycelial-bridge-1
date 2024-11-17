import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import platform-specific integrations
from config import get_platform

# Flask app for Slack
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
        # Check if we should use ngrok based on the .env variable
        use_ngrok = os.getenv("USE_NGROK", "False").lower() == "true"

        if use_ngrok:
            try:
                from pyngrok import ngrok

                # Start NGROK and get the public URL
                ngrok_tunnel = ngrok.connect(3000)

                # Extract the actual public URL from the tunnel object
                public_url = ngrok_tunnel.public_url

                # Append the /events endpoint to the NGROK URL
                full_url = f"{public_url}/events"

                # Print the URL to the console for easy copy-paste
                print(f"ngrok tunnel opened: {public_url}")
                print(f"Event Subscription URL: {full_url}")
            except ImportError:
                print("Error: pyngrok is not installed. Install it with 'pip install pyngrok'.")

        # Run the Flask app
        app.run(port=3000)

elif platform_name == "discord":
    from integrations.discord_integration import DiscordIntegration

    if __name__ == "__main__":
        # Initialize and run the Discord bot
        integration = DiscordIntegration()
        integration.run()

else:
    print(f"Unsupported platform specified: {platform_name}. Please update your .env file.")
