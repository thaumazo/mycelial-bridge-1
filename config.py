import os
from integrations.slack_integration import SlackIntegration

def get_platform():
    platform_name = os.getenv("PLATFORM_NAME", "slack").lower()

    if platform_name == "zulip":
        try:
            from integrations.zulip_integration import ZulipIntegration
            return ZulipIntegration(
                api_key=os.getenv("ZULIP_API_KEY"),
                email=os.getenv("ZULIP_EMAIL"),
                server_url=os.getenv("ZULIP_SERVER_URL")
            )
        except ModuleNotFoundError:
            print("Zulip integration module not found. Make sure to implement it.")
            raise
    elif platform_name == "mattermost":
        # Future Mattermost integration
        pass
    else:
        return SlackIntegration(
            bot_token=os.getenv("BOT_USER_OAUTH_TOKEN")
        )

def get_ngrok_url():
    from pyngrok import ngrok
    ngrok_url = ngrok.connect(3000)
    return ngrok_url
