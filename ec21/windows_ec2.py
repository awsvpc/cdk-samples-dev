from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    CfnInit,
    Fn
)
from constructs import Construct
import os
import yaml

class WindowsEc2Stack(Stack):
    def __init__(self, scope: Construct, id: str, base_stack: BaseStack, env_name: str, os_version: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, "VPC", is_default=True)

        # Per-env subnet selection
        if env_name == "dev":
            subnet_id = "subnet-xxxx-dev"
            sg_id = base_stack.sg.security_group_id
            # Load userdata from YAML
            with open(os.path.join("userdata","dev_windows_userdata.yml"), 'r') as f:
                userdata_yaml = yaml.safe_load(f)
            userdata_script = userdata_yaml.get("userdata", "")
        else:
            subnet_id = None
            sg_id = base_stack.sg.security_group_id
            userdata_script = "<default userdata>"

        # AMI selection
        if os_version == "win2022":
            ami_id = "ami-0abcdef1234567890"
        else:
            ami_id = "ami-0fedcba9876543210"

        lt = ec2.CfnLaunchTemplate(
            self,
            "WinLaunchTemplate",
            launch_template_name=f"{env_name}-WinLT",
            launch_template_data=ec2.CfnLaunchTemplate.LaunchTemplateDataProperty(
                image_id=ami_id,
                instance_type="t3.medium",
                security_group_ids=[sg_id],
                user_data=Fn.base64(userdata_script),
                iam_instance_profile={"arn": base_stack.instance_profile.attr_arn}
            )
        )

        # EC2 instance using Launch Template
        instance = ec2.CfnInstance(
            self,
            "WindowsInstance",
            launch_template=ec2.CfnInstance.LaunchTemplateSpecificationProperty(
                launch_template_id=lt.ref,
                version=lt.attr_latest_version_number
            ),
            subnet_id=subnet_id
        )
