from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_secretsmanager as secrets,
    Fn,
    CfnOutput
)
from constructs import Construct
import os
import yaml

class WindowsEc2Stack(Stack):
    def __init__(self, scope: Construct, id: str, base_stack, env_name: str, os_version="win2022", **kwargs):
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, "VPC", is_default=True)

        # --- Subnet & SG selection ---
        if env_name == "dev":
            subnet_id = "subnet-xxxx-dev"
            sg_id = base_stack.sg.security_group_id
            with open(os.path.join("userdata","dev_windows_userdata.yml"), 'r') as f:
                userdata_yaml = yaml.safe_load(f)
            userdata_script = userdata_yaml.get("userdata", "")
        else:
            subnet_id = None
            sg_id = base_stack.sg.security_group_id
            userdata_script = "<default userdata>"

        # --- Secrets Manager ---
        secret = secrets.Secret(
            self,
            "WindowsSecret",
            secret_name=f"{env_name}-ec2-secret",
            generate_secret_string=secrets.SecretStringGenerator(
                secret_string_template='{"username":"AdminUser"}',
                generate_string_key="password",
                exclude_punctuation=True
            )
        )

        # AMI selection
        if os_version == "win2022":
            ami_id = "ami-0abcdef1234567890"
        else:
            ami_id = "ami-0fedcba9876543210"

        # Launch Template with cfn-init
        lt = ec2.CfnLaunchTemplate(
            self,
            "WinLaunchTemplate",
            launch_template_name=f"{env_name}-WinLT",
            launch_template_data=ec2.CfnLaunchTemplate.LaunchTemplateDataProperty(
                image_id=ami_id,
                instance_type="t3.medium",
                iam_instance_profile={"arn": base_stack.instance_profile.attr_arn},
                security_group_ids=[sg_id],
                user_data=Fn.base64(userdata_script)
            )
        )

        # EC2 Instance
        instance = ec2.CfnInstance(
            self,
            "WindowsInstance",
            launch_template=ec2.CfnInstance.LaunchTemplateSpecificationProperty(
                launch_template_id=lt.ref,
                version=lt.attr_latest_version_number
            ),
            subnet_id=subnet_id
        )

        CfnOutput(self, "WindowsInstanceId", value=instance.ref)
        CfnOutput(self, "WindowsSecretName", value=secret.secret_name)
