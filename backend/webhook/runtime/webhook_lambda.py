import requests

import boto3

secrets_manager = boto3.client("secretsmanager")

# URLs where the set/clear webhook HTTP requests must be sent
_WEBHOOK_BASE_URL = "https://api.telegram.org/bot{}/"
WEBHOOK_CLEAR_URL = _WEBHOOK_BASE_URL + "setWebHook"
WEBHOOK_SET_URL = _WEBHOOK_BASE_URL + "setWebHook?url={}"


def on_event(event, _):
    """
    Handles lifetime events for a Telegram Webhook custom resource
    :param event: Event to be handled
    :param _: Unused
    :raises Exception if the request is invalid or if any error occurs
    """
    print(event)

    secret_name = event["ResourceProperties"]["TelegramSecretName"]
    url = event["ResourceProperties"]["ApiGatewayURL"]

    api_key = get_telegram_api_key(secret_name)

    request_type = event["RequestType"]
    if request_type == "Create":
        return on_create(secret_name, api_key, url)
    if request_type == "Update":
        return on_update(secret_name, api_key, url)
    if request_type == "Delete":
        return on_delete(secret_name, api_key, url)
    raise Exception("Invalid request type: %s" % request_type)


def on_create(secret: str, api_key: str, api_gateway_url: str):
    """
    Handles the creation of a new Webhook resource
    :param secret: Name of the secret containing the Telegram API key
    :param api_key: Telegram API key to use
    :param api_gateway_url: URL where the Telegram updates must be sent
    """
    print(f"Create webhook for url {api_gateway_url}")
    set_webhook(api_key, api_gateway_url)


def on_update(secret: str, api_key: str, api_gateway_url: str):
    """
    Handles the updating of a Webhook resource
    :param secret: Name of the secret containing the Telegram API key
    :param api_key: Telegram API key to use
    :param api_gateway_url: URL where the Telegram updates must be sent
    """
    print(f"Update webhook for url {api_gateway_url}")
    set_webhook(api_key, api_gateway_url)


def on_delete(secret: str, api_key: str, api_gateway_url: str):
    """
    Handles the deletion of a Webhook resource
    :param secret: Name of the secret containing the Telegram API key
    :param api_key: Telegram API key to use
    :param api_gateway_url: URL of the existing Webhook gateway
    """
    print(f"Remove webhook for url {api_gateway_url}")
    clear_webhook(api_key)


def get_telegram_api_key(secret_name: str) -> str:
    """
    Obtains the value of the API key from Secrets Manager
    :param secret_name: Name of the secret containing the API key
    :return: String with the plaintext API key
    """
    secret_value = secrets_manager.get_secret_value(SecretId=secret_name)
    return secret_value["SecretString"]


def set_webhook(api_key: str, gateway_url: str):
    """
    Creates a webhook for the Telegram bot with the provided API key, pointing
    to the provided url
    :param api_key: API key of the bot where the webhook must be set
    :param gateway_url: URL where the Telegram updates must be sent
    :raises Exception if any error occurs while setting the webhook
    """
    response = requests.get(WEBHOOK_SET_URL.format(api_key, gateway_url))

    # If any error ocurred during webhook creation, raise an exception so that
    # CloudFormation receives a "FAILED" response
    response.raise_for_status()


def clear_webhook(api_key: str):
    """
    Removes the existing webhook for the Telegram bot with the provided API key
    :param api_key: API key of the bot where the webhook must be removed
    :raises Exception if any error occurs while clearing the webhook
    """
    response = requests.get(WEBHOOK_CLEAR_URL.format(api_key))

    # If any error ocurred during webhook creation, raise an exception so that
    # CloudFormation receives a "FAILED" response
    response.raise_for_status()
