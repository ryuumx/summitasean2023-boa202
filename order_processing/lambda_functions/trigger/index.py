from urllib.parse import unquote_plus
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes import event_source, S3Event
from aws_lambda_powertools.utilities.typing import LambdaContext
import boto3
import json
import os

logger = Logger()

@event_source(data_class=S3Event)
def handler(event: S3Event, context: LambdaContext):
    s3_client = boto3.client("s3")
    sfn_client = boto3.client('stepfunctions')
    bucket_name = event.bucket_name
    order_items = []

    # Multiple records can be delivered in a single event
    for record in event.records:
        object_key = unquote_plus(record.s3.get_object.key)
        
        file_content = s3_client.get_object(
            Bucket=bucket_name, Key=object_key)["Body"].read()
        logger.info("===== File content read =====")
        logger.info(file_content)
        
        parsed_json = (json.loads(file_content)) 
        order_items.extend(parsed_json["data"])
    
    logger.info("===== Trigger with all items =====")
    logger.info(order_items)
    sfn_client.start_execution(
        stateMachineArn=os.environ['STEPFUNCTIONARN'],
        input=json.dumps(order_items),
    )
    
    return {"result": "ok", "statusCode": 200}