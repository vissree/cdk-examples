from helpers.aws.helper_decorators import handle_client_errors, validate_client_conn
from helpers.aws.helper_core import ServiceClass


class SSMServiceClass(ServiceClass):
    def __init__(self):
        super().__init__("ssm")

    @handle_client_errors
    @validate_client_conn
    def get_secret(self, path, decrypt=True):
        """
        Return the plain text value of the secret.
        Default decryption enabled by default. Use
        decrypt=False if value is not encrypted.
        """

        response = self.client.get_parameter(Name=path, WithDecryption=decrypt)
        return response.get("Parameter").get("Value")
