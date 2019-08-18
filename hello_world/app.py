import logging
import os
import json
import boto3
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    logger.info(event)

    # Lambdaで設定した環境変数の取得(Messaging API)
    CHANNEL_ACCESS_TOKEN = os.environ['CHANNEL_ACCESS_TOKEN']

    # Lambdaで設定した環境変数の取得(AWS Budgets)
    ACCOUNT_ID = os.environ['ACCOUNT_ID']
    BUDGET_NAME = os.environ['BUDGET_NAME']

    # 予算の情報の取得
    client = boto3.client('budgets')
    response = client.describe_budget(
        AccountId=ACCOUNT_ID,
        BudgetName=BUDGET_NAME
    )

    logger.info(response)

    # 予算、現行、予測の取得
    limit = float(response['Budget']['BudgetLimit']['Amount'])
    actual = float(response['Budget']['CalculatedSpend']
                   ['ActualSpend']['Amount'])
    forecasted = float(
        response['Budget']['CalculatedSpend']['ForecastedSpend']['Amount'])

    # 応答メッセージを設定
    status = 'unknown' + chr(0x2753)
    if actual >= limit:
        status = 'bad' + chr(0x1F631)
    elif forecasted >= limit:
        status = 'not good' + chr(0x1F613)
    else:
        status = 'good' + chr(0x1F604)
    text = 'status = {}\nlimit = {:.2f}$\nactual = {:.2f}$\nforecasted = {:.2f}$'.format(
        status, limit, actual, forecasted
    )

    logger.info(text)

    # Messaging APIに送信するHTTPリクエストを実行
    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    try:
        line_bot_api.reply_message(
            json.loads(event['body'])['events'][0]['replyToken'],
            TextSendMessage(text=text)
        )
    except LineBotApiError as e:
        # error handle
        logger.exception(e)

    return {
        "statusCode": 200,
        # "body": json.dumps({
        #     "message": text,
        # }),
    }
