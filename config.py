import os

def get_platform():
    platform = os.getenv("PLATFORM", "slack")
    
    if platform == "slack":
        from integrations.slack_integration import SlackIntegration  # Move import here to avoid circular import
        
        # Use the new environment variable SLACK_BOT_USER_OAUTH_TOKENS
        tokens_str = os.getenv("SLACK_BOT_USER_OAUTH_TOKENS")

        if not tokens_str:
            raise ValueError("Missing SLACK_BOT_USER_OAUTH_TOKENS environment variable.")
        
        # Return an instance of SlackIntegration, no need to pass individual bot tokens here
        return SlackIntegration()
    
    raise ValueError("Unsupported platform configuration")

def get_ngrok_url():
    return os.getenv("NGROK_URL")
