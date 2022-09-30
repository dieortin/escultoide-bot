# EscultoideBot

## Introduction

This project implements a [Telegram](https://telegram.org/) bot, which interacts 
with a [Notion](https://notion.so) database through its 
[API](https://developers.notion.com/reference) to provide certain information to users.

The bot is implemented with a serverless architecture, leveraging 
[AWS](https://aws.amazon.com/) services.
Instead of having a long-running process poll the Telegram servers for updates, 
EscultoideBot configures a webhook and then processes the Telegram events on
arrival through [Lambda functions](https://aws.amazon.com/lambda/). This allows 
for seamless scaling from zero 
requests to a massive scale, without incurring in costs when the bot is not
being used.

This repository contains both the runtime code for the Lambda functions
themselves, and the CDK code that defines the infrastructure they run on.

## Running the bot

CDK deals with provisioning the infrastructure and deploying the runtime code,
so only a few steps must be taken to run this project.

### Prerequisites

* AWS account that has been [bootstrapped](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html)
* Workstation configured with your AWS credentials and region

### Steps

1. Clone or download the project folder, and change to its directory:
```
$ git clone https://github.com/dieortin/escultoide-bot
$ cd escultoide-bot
```

2. Install the required packages:
```
$ pip install -r requirements.txt
```

3. Create two secrets in [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/),
with the API keys to be used for Telegram and Notion.

4. Modify the configuration values in `app.py` to match the names for 
your secrets in AWS Secrets Manager, and the ID of your Notion database.

5. Deploy the application:
```
$ cdk deploy
```

## Architecture

The project's backend consists on two main components:

### API

This construct receives and processes updates from Telegram. It consists
on two components:

* A Lambda function that processes new Telegram updates
* An API Gateway, which receives HTTP requests from Telegram, invokes
the Lambda and responds

### Webhook

This construct manages the Telegram API configuration so that 
updates are sent to the API.

It consists on a custom resource that represents the configured
webhook for the bot in the Telegram API. It manages setting the webhook
to the URL of the API so that it can receive updates, and removing it
when the component is deleted.

This custom resource has a Lambda function that performs the required 
actions when lifecycle changes are made to it.
