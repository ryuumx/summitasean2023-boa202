import aws_cdk as core
import aws_cdk.assertions as assertions

from order_processing.order_processing_stack import OrderProcessingStack

# example tests. To run these tests, uncomment this file along with the example
# resource in order_processing/order_processing_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = OrderProcessingStack(app, "order-processing")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
