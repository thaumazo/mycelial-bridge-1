import os

def get_platform():
    platform = os.getenv("PLATFORM", "slack")
    
    if platform == "slack":
        from integrations.slack_integration import SlackIntegration  # Move import here to avoid circular import
        bot_token = os.getenv("BOT_USER_OAUTH_TOKEN")  # Use Slack's variable name
        
        if not bot_token:
            raise ValueError("Missing BOT_USER_OAUTH_TOKEN environment variable")
        
        # Ensure the bot token is valid
        return SlackIntegration(bot_token)
    
    raise ValueError("Unsupported platform configuration")

def get_ngrok_url():
    return os.getenv("NGROK_URL")
