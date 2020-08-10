from helpers.aws.helper_decorators import handle_client_errors
from botocore.config import Config
import boto3


class ServiceClass(object):
    @handle_client_errors
    def __init__(self, service_name):
        self.client = boto3.client(
            service_name, config=Config(retries={"max_attempts": 10})
        )
