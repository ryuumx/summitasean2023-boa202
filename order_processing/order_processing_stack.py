from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks,
    aws_s3_notifications as s3n,
    aws_sns as sns,
    aws_sns_subscriptions as sns_sub,
    aws_dynamodb as ddb,
    aws_iam as iam,
)
import os
from constructs import Construct

class OrderProcessingStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ### Order input ###
        
        bucket = s3.Bucket(self, "input_data",
            versioned=True,
            event_bridge_enabled=True
        )
        
        ### Info extraction and saving ###
        
        db_table = ddb.Table(self, "order_table",
            partition_key=ddb.Attribute(name="customer_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="timestamp", type=ddb.AttributeType.STRING)
        )
        
        put_info = sfn_tasks.DynamoPutItem(self, "put_info",
            item={
                "customer_id": sfn_tasks.DynamoAttributeValue.from_string(sfn.JsonPath.string_at("$.customer_id")),
                "timestamp": sfn_tasks.DynamoAttributeValue.from_string(sfn.JsonPath.string_at("$.timestamp")),
                "item_id": sfn_tasks.DynamoAttributeValue.from_string(sfn.JsonPath.string_at("$.item_id")),
                "quantity": sfn_tasks.DynamoAttributeValue.number_from_string(sfn.JsonPath.string_at("States.Format('{}', $.qty)")),
            },
            table=db_table,
            result_path=sfn.JsonPath.DISCARD
        )
        
        process_items = sfn.Map(self, "for_each")
        process_items.iterator(put_info)
        
        ### Verification / Confirmation ###
        
        wait = sfn.Wait(self, "wait",
            time=sfn.WaitTime.seconds_path("$.wait_time")
        )
        put_info.next(wait)
        
        powertool = lambda_.LayerVersion.from_layer_version_arn(self, 'powertool_layer',
            'arn:aws:lambda:ap-southeast-1:017000801446:layer:AWSLambdaPowertoolsPythonV2:23');
        
        validate_lambda = lambda_.Function(self, 'validate',
            code=lambda_.Code.from_asset(os.path.join(os.path.dirname(__file__), 'lambda_functions/validate')),
            handler='index.handler',
            runtime=lambda_.Runtime.PYTHON_3_7,
            layers=[powertool]
        )
        validate_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter"],
                resources=["*"]
            )
        )
        
        validate = sfn_tasks.LambdaInvoke(self, "call_validate",
            lambda_function=validate_lambda,
            result_path="$.confirmed"
        )
        wait.next(validate)
        
        ### Fulfillment ###
        
        sns_topic = sns.Topic(self, "send_fulfillment")
        
        sns_topic.add_subscription(
            sns_sub.EmailSubscription("email@demo.com")
        )
        sns_topic.add_subscription(
            sns_sub.SmsSubscription("+84000000000")
        )
        
        send_message = sfn_tasks.SnsPublish(self, "send_message",
            topic=sns_topic,
            message=sfn.TaskInput.from_text(
                sfn.JsonPath.string_at("States.Format('New order: prepare {} of {} for {}', $.qty, $.item_id, $.customer_id)")
            ),
            result_path="$.sns"
        )
        
        confirm = sfn.Choice(self, "order_confirm?") \
            .when(sfn.Condition.boolean_equals("$.confirmed.Payload.result", True), send_message) \
            .otherwise(sfn.Pass(self, "failed"))
        
        validate.next(confirm)
            
        ### Tie it all together in a step functions workflow ###
        
        workflow = sfn.StateMachine(self, "order_processing",
            definition = process_items.next(sfn.Succeed(self, "Finished"))
        )
        db_table.grant_read_write_data(workflow)
        validate_lambda.grant_invoke(workflow)
        workflow.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter"],
                resources=["*"]
            )
        )
        
        ### Triggering the workflow with S3 ###
        
        trigger_lambda = lambda_.Function(self, 'trigger',
            code=lambda_.Code.from_asset(os.path.join(os.path.dirname(__file__), 'lambda_functions/trigger')),
            handler='index.handler',
            runtime=lambda_.Runtime.PYTHON_3_7,
            layers=[powertool],
            environment={
                "STEPFUNCTIONARN": workflow.state_machine_arn,
            },
        )
        workflow.grant_start_execution(trigger_lambda)
        bucket.grant_read(trigger_lambda)
        
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED, s3n.LambdaDestination(trigger_lambda))
