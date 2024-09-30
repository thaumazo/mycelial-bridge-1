Here’s a detailed `INSTALLATION.md` file that will guide a newcomer through the process of setting up and running the application on their system. This file assumes the user is using **Conda** and will utilize the provided `environment.yml` for setting up the environment.

---

# Installation Guide

Welcome to the installation guide for this Slack-based Flask application. This guide will walk you through the steps required to set up the application on your local machine. Follow these steps carefully to get the application up and running.

---

## Prerequisites

Before you begin, ensure that the following prerequisites are met:

- **Git**: You will need Git installed to clone the repository. You can install it from [here](https://git-scm.com/downloads).
- **Conda**: This application uses Conda to manage the Python environment. Install Conda by downloading **Anaconda** or **Miniconda** from [here](https://docs.conda.io/en/latest/miniconda.html).
- **Slack Workspace**: You will need to create a Slack app in your workspace to obtain the necessary tokens and permissions.

---

## Step 1: Clone the Repository

First, clone the repository to your local machine using Git.

```bash
git clone https://github.com/your-username/repository-name.git
cd repository-name
```

---

## Step 2: Set Up the Conda Environment

The repository includes an `environment.yml` file, which specifies the dependencies needed for the application. Use this file to create the Conda environment.

Run the following command in the terminal:

```bash
conda env create -f environment.yml
```

This command will create a Conda environment named after the environment specified in the `environment.yml` file (e.g., `langchain-slack`). After the environment is created, activate it:

```bash
conda activate langchain-slack
```

---

## Step 3: Create a `.env` File

This application requires a `.env` file to store sensitive information such as API tokens and Slack group names. Create a `.env` file in the root directory of the project and add the following variables:

```plaintext
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token-here
SLACK_TRIGGER_GROUP=your-slack-trigger-group-name
SLACK_CONSUME_GROUP=your-slack-consume-group-name
```

### How to Get the Slack Bot Token:

1. Go to your Slack [API Dashboard](https://api.slack.com/apps) and create a new app or use an existing one.
2. Under the **OAuth & Permissions** section, add the following bot token scopes:
    - `channels:history`
    - `groups:history`
    - `reactions:read`
    - `chat:write`
3. Install the app to your workspace and copy the **Bot User OAuth Token** into the `SLACK_BOT_TOKEN` variable in your `.env` file.

### Slack Groups:
- Add the relevant group names for the `SLACK_TRIGGER_GROUP` and `SLACK_CONSUME_GROUP` values. These should be the exact names of the Slack user groups you're working with.

---

## Step 4: Start NGROK

This application requires NGROK to expose your local Flask server to the internet, allowing Slack to send event notifications to your app.

1. **Install NGROK**: If you don't have NGROK installed, you can download it from [here](https://ngrok.com/download).
2. **Start NGROK**: Open a new terminal window and run the following command:

```bash
ngrok http 3000
```

3. NGROK will start and provide a public forwarding URL, such as `https://<ngrok-subdomain>.ngrok.io`. Copy this URL.

---

## Step 5: Set Up Slack Event Subscriptions

1. Go back to the **Slack API Dashboard** for your app.
2. Under **Event Subscriptions**, enable events and paste the NGROK forwarding URL followed by `/slack/events`. Example:

```
https://<ngrok-subdomain>.ngrok.io/slack/events
```

3. Under **Subscribe to Bot Events**, add the following events:
   - `message.channels`
   - `message.groups`
   - `reaction_added`

4. Save the settings. Slack will send a verification request, and your app should respond with a challenge response if everything is set up correctly.

---

## Step 6: Run the Flask Application

In your terminal, make sure the Conda environment is activated, and then run the Flask app:

```bash
python main.py
```

You should see output similar to:

```plaintext
ngrok tunnel opened: https://<ngrok-subdomain>.ngrok.io
 * Running on http://127.0.0.1:3000/ (Press CTRL+C to quit)
```

Make sure to keep this terminal open as this will handle requests coming from Slack.

---

## Step 7: Test the Application

1. **Send a Message in Slack**: Post a message in a channel where the bot has been invited.
2. **Add a Reaction**: React to a message in a channel where the bot has been invited.
3. Check the Flask application logs for messages or reactions. You should see log entries confirming that the app has received the Slack events.

---

## Troubleshooting

- **NGROK URL Changes**: If you restart the Flask application or NGROK, the NGROK URL will change. Make sure to update the **Request URL** in the Slack Event Subscriptions to match the new NGROK URL.
- **Bot Not Receiving Events**: Ensure the bot is invited to the appropriate channels by typing `/invite @YourBotName` in the Slack channels you want it to monitor.
- **Scope Issues**: If the bot is not receiving events, double-check that all the required OAuth scopes are added and that the app has been reinstalled after making changes to permissions.

---

## Additional Features

This application includes logic to check if the user who posted a message or added a reaction belongs to a specific Slack group (defined in the `.env` file). You can modify the group names or extend the functionality to suit your needs.

---

## Conclusion

If everything is set up correctly, your Slack app should now be able to detect messages and reactions from the defined Slack groups and process them accordingly. Happy coding!

---

## License

This project is licensed under the MIT License.

---

NOTE: This file created via GPT-4o
