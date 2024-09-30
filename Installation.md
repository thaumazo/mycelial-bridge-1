1. Create a Slack App
Go to the Slack API dashboard and create a new app.
Select "From scratch" and give your app a name.
Choose a workspace where the app will be installed.
Under OAuth & Permissions, add the following scopes:
channels:history (to read messages)
channels:read (to view channel information)
chat:write (to send messages)
reactions:read (to read reactions/emoticons)
users:read (to read user information)
You can add other scopes as needed based on your use case.
2. Install the Slack App
Go to the "OAuth & Permissions" page and install the app to your workspace.
You’ll receive an OAuth Token. Make sure to save it securely, as you'll need it to authenticate requests.
3. Set Up Event Subscriptions
In the Slack App settings, go to "Event Subscriptions."
Enable events and add a Request URL (for local development, use something like NGROK to tunnel requests to your local machine).
Subscribe to events like:
message.channels (to capture messages sent to channels)
reaction_added (to capture reactions like emoticons)
