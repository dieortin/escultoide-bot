#!/usr/bin/env python3
import os

import aws_cdk as cdk

from backend.component import EscultoideBot

# Secret names
TG_SECRET = "dev/EscultoideBot/TelegramAPIKey"
NOTION_SECRET = "prod/EscultoideBot/NotionAPIKey"

# ID for the Notion calendar database to access
NOTION_CALENDAR = "7e491de1361b4f7da91dff3d607b6480"

app = cdk.App()

EscultoideBot(
    app,
    construct_id="EscultoideBot",
    telegram_secret_name=TG_SECRET,
    notion_secret_name=NOTION_SECRET,
    notion_calendar_id=NOTION_CALENDAR,
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
    allowed_users=["dieortin", "alon2o"],
)

app.synth()
