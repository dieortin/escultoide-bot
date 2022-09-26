import pathlib

from aws_cdk import (
    aws_lambda as _lambda,
    aws_lambda_python_alpha as lambda_python_alpha,
    aws_apigateway as apigw,
    aws_secretsmanager as ssm,
    aws_iam as iam,
)
from aws_cdk.aws_logs import RetentionDays
from constructs import Construct


class API(Construct):
    """
    Construct representing the API of the EscultoideBot Telegram bot. It
    consists on an API Gateway and a Lambda function that processes requests.
    """

    def __init__(
        self,
        scope: Construct,
        id_: str,
        telegram_secret: ssm.ISecret,
        notion_secret: ssm.ISecret,
        notion_calendar_id: str,
        allowed_users: [str] = None,
    ) -> None:
        super().__init__(scope, id_)

        # Use an empty list when no allowed users exist, so we can use the join
        # function later without errors
        if not allowed_users:
            allowed_users = []

        # Main lambda function processing the updates received by the bot
        self.bot_lambda = lambda_python_alpha.PythonFunction(
            self,
            "BotLambda",
            description="Main function processing Telegram updates",
            runtime=_lambda.Runtime.PYTHON_3_9,
            entry=str(pathlib.Path(__file__).parent.joinpath("runtime").resolve()),
            index="router_lambda.py",
            handler="handler",
            environment={
                "TelegramSecretName": telegram_secret.secret_name,
                "NotionSecretName": notion_secret.secret_name,
                "NotionCalendarID": notion_calendar_id,
                "AllowedUsers": ",".join(allowed_users),
            },
            log_retention=RetentionDays.ONE_WEEK,
        )

        # The bot lambda must be able to read both API Key secrets
        telegram_secret.grant_read(grantee=self.bot_lambda)
        notion_secret.grant_read(grantee=self.bot_lambda)

        # Policy that only allows requests coming from IP ranges belonging to
        # Telegram webhooks to go through the API Gateway
        only_telegram_ip_policy = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    principals=[iam.AnyPrincipal()],
                    actions=["execute-api:Invoke"],
                    resources=["execute-api:/*/*/*"],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.DENY,
                    principals=[iam.AnyPrincipal()],
                    actions=["execute-api:Invoke"],
                    resources=["execute-api:/*/*/*"],
                    conditions={
                        "NotIpAddress": {
                            "aws:SourceIp": ["149.154.160.0/20", "91.108.4.0/22"]
                        }
                    },
                ),
            ]
        )

        # API Gateway where the Telegram webhook sends the updates, which are
        # passed to the lambda function
        self.gateway = apigw.LambdaRestApi(
            self,
            "EscultoideBotAPIGateway",
            handler=self.bot_lambda,
            proxy=False,
            policy=only_telegram_ip_policy,
            deploy_options=apigw.StageOptions(
                metrics_enabled=True,
                logging_level=apigw.MethodLoggingLevel.ERROR,
            ),
        )

        self.gateway.root.add_method(
            # We can allow only POST, as it is what the webhook uses.
            "POST",
            # The lambda integration returns 200 for every successful function run, no
            # matter the actual HTTP return code of the invocation.
            apigw.LambdaIntegration(
                self.bot_lambda,
                proxy=False,
                integration_responses=[{"statusCode": "200"}],
            ),
            method_responses=[apigw.MethodResponse(status_code="200")],
        )
