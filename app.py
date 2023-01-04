#!/usr/bin/env python3
import os

import aws_cdk as cdk

from backend.component import EscultoideBot

# Secret names
TG_SECRET = "prod/EscultoideBot/TelegramAPIKey"
NOTION_SECRET = "prod/EscultoideBot/NotionAPIKey"

# ID for the Notion calendar database to access
NOTION_CALENDAR = "dff753c361c949c6b4add593b9e4e0db"

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
    allowed_users=["dieortin", "Alon2o", "Caloca", "madlmc"],
)

app.synth()
