import os
from dotenv import load_dotenv

load_dotenv()

class TelegramSender:
    import requests
    def __init__(self, bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN"), channel_id: str = os.getenv("TELEGRAM_CHANNEL_ID")):
        """
        Initializes the TelegramSender with the bot token and channel ID.

        :param bot_token: Telegram bot token.
        :param channel_id: Telegram channel ID (e.g., '@your_channel').
        """
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send_message(self, text: str) -> bool:
        """
        Sends a plain text message to the Telegram channel.

        :param text: The message text to send.
        :return: True if the message was sent successfully, False otherwise.
        """
        payload = {
            'chat_id': self.channel_id,
            'text': text,
            'parse_mode': 'Markdown'
        }
        response = self.requests.post(self.api_url, data=payload)
        return response.status_code == 200

    def send_json_message(self, json_data: dict) -> bool:
        """
        Sends a JSON object as a formatted code block in the Telegram channel.

        :param json_data: The JSON data to send.
        :return: True if the message was sent successfully, False otherwise.
        """
        import json
        json_formatted = json.dumps(json_data, indent=4)
        message = f"```json\n{json_formatted}\n```"
        return self.send_message(message)