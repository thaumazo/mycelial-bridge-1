import os

def get_platform():
    platform = os.getenv("PLATFORM", "").lower()

    if not platform:
        raise ValueError("PLATFORM is not set in the .env file. It must be either 'slack' or 'discord'.")

    if platform == "slack":
        from integrations.slack_integration import SlackIntegration
        
        # Use the new environment variable SLACK_BOT_USER_OAUTH_TOKENS
        tokens_str = os.getenv("SLACK_BOT_USER_OAUTH_TOKENS")

        if not tokens_str:
            raise ValueError(
                "SLACK_BOT_USER_OAUTH_TOKENS is not set in the .env file. "
                "Provide it in the format team1:token1,team2:token2"
            )

        # Return an instance of SlackIntegration
        return SlackIntegration()

    elif platform == "discord":
        from integrations.discord_integration import DiscordIntegration

        bot_token = os.getenv("DISCORD_BOT_TOKEN")
        if not bot_token:
            raise ValueError(
                "DISCORD_BOT_TOKEN is not set in the .env file. "
                "Set this to your Discord bot's authentication token."
            )

        return DiscordIntegration()

    else:
        raise ValueError(
            f"Unsupported platform: {platform}. Set PLATFORM to 'slack' or 'discord' in the .env file."
        )

def get_ngrok_url():
    ngrok_url = os.getenv("NGROK_URL")
    if not ngrok_url:
        print("Warning: NGROK_URL is not set in the .env file. The app will not use a public URL unless NGROK is configured.")
    return ngrok_url
