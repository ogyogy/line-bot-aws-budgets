import os
import json
import boto3


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

    # Lambdaで設定した環境変数の取得
    ACCOUNT_ID = os.environ['ACCOUNT_ID']
    BUDGET_NAME = os.environ['BUDGET_NAME']

    client = boto3.client('budgets')
    response = client.describe_budget(
        AccountId=ACCOUNT_ID,
        BudgetName=BUDGET_NAME
    )

    limit = float(response['Budget']['BudgetLimit']['Amount'])
    actual = float(response['Budget']['CalculatedSpend']
                   ['ActualSpend']['Amount'])
    forecasted = float(
        response['Budget']['CalculatedSpend']['ForecastedSpend']['Amount'])

    status = 'unknown'
    if actual >= limit:
        status = 'bad'
    elif forecasted >= limit:
        status = 'not good'
    else:
        status = 'good'

    text = '{}: limit = {:.2f}, actual = {:.2f}, forecasted = {:.2f}'.format(
        status, limit, actual, forecasted
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": text,
        }),
    }
