import os
import re
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DiscordIntegration:
    def __init__(self):
        # Load Discord bot token and trigger group
        self.bot_token = os.getenv("DISCORD_BOT_TOKEN")
        self.allowed_users = self.load_allowed_users()

        if not self.bot_token:
            raise ValueError("Missing DISCORD_BOT_TOKEN in the .env file.")

        # Initialize the bot
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True
        intents.reactions = True
        intents.message_content = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)

        # Add event handlers
        @self.bot.event
        async def on_ready():
            print(f"Bot connected as {self.bot.user}")
            print("Listening for messages and reactions...")

        @self.bot.event
        async def on_message(message):
            # Ignore messages from the bot itself
            if message.author.bot:
                return

            # Check if the user is in the allowed group
            if str(message.author.id) not in self.allowed_users:
                print(f"Unauthorized user: {message.author}. Ignoring message.")
                return

            print(f"Message received: {message.content} from {message.author}")

            # Determine the type of message and process accordingly
            if self.is_text_message(message):
                await self.process_text_message(message)
            elif self.is_image_message(message):
                await self.process_image_message(message)
            elif self.is_url_message(message):
                await self.process_url_message(message)
            else:
                print("Message type not recognized. Ignoring.")

        @self.bot.event
        async def on_reaction_add(reaction, user):
            if user.bot:
                return  # Ignore reactions from bots

            # Check if the user is in the allowed group
            if str(user.id) not in self.allowed_users:
                print(f"Unauthorized user: {user}. Ignoring reaction.")
                return

            print(f"Reaction added: {reaction.emoji} by {user}")

            # Handle the specific reaction
            if reaction.emoji == "📰":  # Newspaper emoji
                message = reaction.message
                urls = self.extract_urls_from_text(message.content)
                if urls:
                    for url in urls:
                        article_content = self.fetch_article(url)
                        if article_content:
                            summary = self.process_article_with_llm(article_content)
                            await message.channel.send(f"Article summary: {summary}")

    def load_allowed_users(self):
        """Load the Discord trigger group from the environment variable."""
        users_str = os.getenv("DISCORD_TRIGGER_GROUP")
        if not users_str:
            raise ValueError("Missing DISCORD_TRIGGER_GROUP in the .env file.")
        return users_str.split(",")

    def is_text_message(self, message):
        """Check if the message is plain text."""
        return bool(message.content.strip()) and not message.attachments and not self.contains_url(message.content)

    def is_image_message(self, message):
        """Check if the message contains an image."""
        if message.attachments:
            return any(attachment.content_type and "image" in attachment.content_type for attachment in message.attachments)
        return False

    def is_url_message(self, message):
        """Check if the message contains a URL."""
        return self.contains_url(message.content)

    def contains_url(self, text):
        """Check if the given text contains a URL."""
        url_regex = r"https?://[^\s]+"
        return re.search(url_regex, text) is not None

    async def process_text_message(self, message):
        """Process a plain text message."""
        print(f"Processing text message: {message.content}")
        await message.channel.send(f"Received text message: {message.content}")

    async def process_image_message(self, message):
        """Process a message containing an image and accompanying text."""
        print(f"Processing image message from {message.author}")

        # Process accompanying text if available
        if message.content.strip():
            print(f"Accompanying text: {message.content}")
            await message.channel.send(f"Accompanying text: {message.content}")

        # Process each attached image
        for attachment in message.attachments:
            if attachment.content_type and "image" in attachment.content_type:
                print(f"Image URL: {attachment.url}")
                await message.channel.send(f"Received image from {message.author.mention}: {attachment.url}")

    async def process_url_message(self, message):
        """Process a message containing a URL and accompanying text."""
        print(f"Processing URL message from {message.author}")

        # Process accompanying text if available
        if message.content.strip():
            print(f"Accompanying text: {message.content}")
            await message.channel.send(f"Accompanying text: {message.content}")

        # Extract and process URLs
        urls = self.extract_urls_from_text(message.content)
        if urls:
            for url in urls:
                article_content = self.fetch_article(url)
                if article_content:
                    summary = self.process_article_with_llm(article_content)
                    print(f"Article summary: {summary}")
                    await message.channel.send(f"Article summary: {summary}")
        else:
            print("No URLs found in the message.")

    def extract_urls_from_text(self, text):
        """Extract URLs from the given text."""
        url_regex = r"https?://[^\s]+"
        return re.findall(url_regex, text)

    def fetch_article(self, url):
        """Fetch article content from the URL."""
        print(f"Fetching article from URL: {url}")
        try:
            # Simulate fetching and parsing an article
            return f"Content from {url}"
        except Exception as e:
            print(f"Error fetching article: {e}")
            return None

    def process_article_with_llm(self, article_content):
        """Process article content with an LLM."""
        # Simulate LLM processing
        return f"Processed content: {article_content[:200]}..."

    def run(self):
        print("Starting Discord bot...")
        self.bot.run(self.bot_token)
