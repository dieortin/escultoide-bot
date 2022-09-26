from aws_cdk import Stack, aws_secretsmanager as _sm

from constructs import Construct

from .api.infrastructure import API
from .webhook.infrastructure import TelegramWebhook


class EscultoideBot(Stack):
    """
    Stack for the EscultoideBot Telegram bot. It has two main components:
        * A webhook that provides a way for Telegram to relay updates to this system
        * A backend that processes said updates
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        telegram_secret_name: str,
        notion_secret_name: str,
        notion_calendar_id: str,
        allowed_users: [str] = None,
        **kwargs,
    ) -> None:
        """
        Initializes an instance of the EscultoideBot stack
        :param scope: Scope where this construct is included
        :param construct_id: Unique identifier for this construct
        :param telegram_secret_name: Name of the Secrets Manager secret containing the
                                     API key for the Telegram bot
        :param notion_secret_name: Name of the Secrets Manager sescret containing the
                                   API key for the Notion integration
        :param notion_calendar_id: Identifier for the Notion database to interact with
        :param allowed_users: List of usernames that must be able to access restricted
                              bot commands
        """
        super().__init__(scope, construct_id, **kwargs)

        self.notion_calendar_id = notion_calendar_id

        # Secrets for Telegram and Notion
        self.telegram_api_key = _sm.Secret.from_secret_name_v2(
            self, id="tg_api_key", secret_name=telegram_secret_name
        )
        self.notion_api_key = _sm.Secret.from_secret_name_v2(
            self, id="notion_api_key", secret_name=notion_secret_name
        )

        self.api = API(
            self,
            "API",
            self.telegram_api_key,
            self.notion_api_key,
            self.notion_calendar_id,
            allowed_users=allowed_users,
        )

        self.webhook = TelegramWebhook(
            self, "TelegramWebhook", self.telegram_api_key, self.api.gateway.url
        )
