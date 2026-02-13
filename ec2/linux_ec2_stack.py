from aws_cdk import Stack, aws_ec2 as ec2, Fn, CfnOutput
from constructs import Construct
import os

class LinuxEc2Stack(Stack):
    def __init__(self, scope: Construct, id: str, base_stack, env_name: str, os_version="al2023", **kwargs):
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, "VPC", is_default=True)

        # Subnet & SG selection
        if env_name == "dev":
            subnet_id = "subnet-xxxx-dev"
            sg_id = base_stack.sg.security_group_id
            with open(os.path.join("userdata","dev_linux_userdata.sh"), 'r') as f:
                userdata_script = f.read()
        else:
            subnet_id = None
            sg_id = base_stack.sg.security_group_id
            userdata_script = "#!/bin/bash\necho 'default'"

        # AMI selection
        ami_id = "ami-0abc1234def567890" if os_version=="al2023" else "ami-0fedcba9876543210"

        lt = ec2.CfnLaunchTemplate(
            self,
            "LinuxLaunchTemplate",
            launch_template_name=f"{env_name}-LinuxLT",
            launch_template_data=ec2.CfnLaunchTemplate.LaunchTemplateDataProperty(
                image_id=ami_id,
                instance_type="t3.medium",
                security_group_ids=[sg_id],
                iam_instance_profile={"arn": base_stack.instance_profile.attr_arn},
                user_data=Fn.base64(userdata_script)
            )
        )

        instance = ec2.CfnInstance(
            self,
            "LinuxInstance",
            launch_template=ec2.CfnInstance.LaunchTemplateSpecificationProperty(
                launch_template_id=lt.ref,
                version=lt.attr_latest_version_number
            ),
            subnet_id=subnet_id
        )

        CfnOutput(self, "LinuxInstanceId", value=instance.ref)
