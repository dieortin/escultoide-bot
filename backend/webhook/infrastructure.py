import pathlib

from aws_cdk import (
    aws_lambda as _lambda,
    aws_lambda_python_alpha as lambda_python_alpha,
    aws_secretsmanager as ssm,
    CustomResource,
)
from aws_cdk.aws_logs import RetentionDays
from aws_cdk.custom_resources import Provider

from constructs import Construct


class TelegramWebhook(Construct):
    """
    Construct representing a webhook in the Telegram service, which points
    to the URL of an API gateway.
    """

    def __init__(
        self, scope: Construct, _id: str, api_key: ssm.ISecret, gateway_url: str
    ) -> None:
        super().__init__(scope, _id)

        # Lambda that processes resource events and creates/updates/deletes
        # the webhook in the Telegram API
        self.provider_lambda = lambda_python_alpha.PythonFunction(
            self,
            "Lambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            entry=str(pathlib.Path(__file__).parent.joinpath("runtime").resolve()),
            index="webhook_lambda.py",
            handler="on_event",
            log_retention=RetentionDays.TWO_WEEKS,
        )

        # The lambda must be able to read the Telegram API key to change
        # the webhook
        api_key.grant_read(grantee=self.provider_lambda)

        self.provider = Provider(
            self,
            "Provider",
            on_event_handler=self.provider_lambda,
            log_retention=RetentionDays.TWO_WEEKS,
        )

        self.webhook = CustomResource(
            self,
            "Resource",
            service_token=self.provider.service_token,
            properties={
                "ApiGatewayURL": gateway_url,
                "TelegramSecretName": api_key.secret_name,
            },
        )
