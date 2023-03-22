from urllib.parse import unquote_plus
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator
import os
import requests

logger = Logger()

INPUT = {
    "required": ["customer_id", "item_id", "qty"],
    "properties": {
        "customer_id": {
            "$id": "#/properties/customer_id",
            "type": "string",
            "title": "The ID of customer",
            "examples": ["test_customer"],
            "maxLength": 50,
        },
        "item_id": {
            "$id": "#/properties/item_id",
            "type": "string",
            "title": "The ID of item",
            "examples": ["test_item"],
            "maxLength": 50,
        },
        "qty": {
            "$id": "#/properties/qty",
            "type": "integer",
            "title": "The quantity",
            "examples": [100],
        },
    },
}

OUTPUT = {
    "required": ["result", "statusCode"],
    "properties": {
        "result": {
            "$id": "#/properties/result",
            "type": "boolean",
            "title": "The result",
            "examples": [True],
        },
        "statusCode": {
            "$id": "#/properties/statusCode",
            "type": "integer",
            "title": "The statusCode",
            "examples": [200],
            "maxLength": 3,
        },
    },
}

@validator(inbound_schema=INPUT, outbound_schema=OUTPUT)
def handler(event: dict, context: LambdaContext) -> dict:
    logger.info("===== Order info received =====")
    logger.info(event)
    
    endpoint1 = parameters.get_parameter("/mock/payment_check_endpoint")
    logger.info("===== Check if order is paid =====")
    logger.info("Endpoint: {}".format(endpoint1))
    paid_res = requests.get(endpoint1, params={"customer_id": event['customer_id']})
    if not paid_res.ok:
        logger.error("Result: Not paid")
        return {"result": False, "statusCode": 200}
    else:
        logger.info("Result: Paid")
        
    endpoint2 = parameters.get_parameter("/mock/stock_check_endpoint")
    logger.info("===== Check if order is paid =====")
    logger.info("Endpoint: {}".format(endpoint2))
    stock_res = requests.get(endpoint2, params={"item_id": event['item_id'], "quantity": event['qty']})
    if not stock_res.ok:
        logger.error("Result: Not in stock")
        return {"result": False, "statusCode": 200}
    else:
        logger.info("Result: In stock")
   
    return {"result": True, "statusCode": 200}
    