from aws_cdk import core
from aws_cdk import aws_ec2 as ec2


class VpcBaselineStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:

        # extract config from kwargs before calling parent constructor
        self.config = kwargs["config"]
        del kwargs["config"]

        super().__init__(scope, id, **kwargs)

        # set the default instance tenancy
        if self.config["vpc"]["default_instance_tenancy"] == "default":
            default_instance_tenancy = ec2.DefaultInstanceTenancy.DEFAULT
        elif self.config["vpc"]["default_instance_tenancy"] == "dedicated":
            default_instance_tenancy = ec2.DefaultInstanceTenancy.DEDICATED

        # use the DEFAULT_CIDR_RANGE if nothing is specified
        if not self.config["vpc"]["cidr"]:
            self.config["vpc"]["cidr"] = ec2.Vpc.DEFAULT_CIDR_RANGE

        # start with an empty subnet configuration
        subnet_configuration = []

        # generate the subnet configuration for the given
        # settings
        subnet_classes = [
            ("dmz", "public"),
            ("app", "private"),
            ("db", "isolated"),
        ]

        for _name, _type in subnet_classes:
            if _type == "public":
                subnet_type = ec2.SubnetType.PUBLIC
            elif _type == "private":
                subnet_type = ec2.SubnetType.PRIVATE
            elif _type == "isolated":
                subnet_type = ec2.SubnetType.ISOLATED

            subnet_prop = {
                "name": self.config["subnets"]["{}_name_prefix".format(_name)],
                "cidr_mask": self.config["subnets"]["{}_prefix".format(_name)],
                "subnet_type": subnet_type,
            }

            subnet_configuration.append(ec2.SubnetConfiguration(**subnet_prop))

            # The next XX subnets are reserved for future expansion
            subnet_prop["reserved"] = True

            for i in range(self.config["subnets"]["{}_buffer".format(_name)]):
                subnet_configuration.append(
                    ec2.SubnetConfiguration(**subnet_prop)
                )

        vpc = ec2.Vpc(
            self,
            self.config["vpc"]["name"],
            cidr=self.config["vpc"]["cidr"],
            max_azs=self.config["subnets"]["max_azs"],
            subnet_configuration=subnet_configuration,
            default_instance_tenancy=default_instance_tenancy,
            enable_dns_hostnames=self.config["vpc"]["enable_dns_hostnames"],
            enable_dns_support=self.config["vpc"]["enable_dns_support"],
        )
