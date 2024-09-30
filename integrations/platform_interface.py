from abc import ABC, abstractmethod

class PlatformIntegration(ABC):
    @abstractmethod
    def handle_event(self, data):
        """Process an incoming event from the platform."""
        pass

    @abstractmethod
    def fetch_message(self, message_id, channel):
        """Fetch a message based on message ID and channel."""
        pass

    @abstractmethod
    def send_message(self, channel, message):
        """Send a message to a channel."""
        pass
