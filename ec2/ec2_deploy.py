from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ssm as ssm,
    aws_secretsmanager as secrets,
    CfnOutput,
    Fn,
    Duration,
)
from constructs import Construct

class WindowsEc2Stack(Stack):
    def __init__(self, scope: Construct, id: str, base_stack, env_name: str, os_version="win2022", **kwargs):
        super().__init__(scope, id, **kwargs)

        # --- VPC Lookup ---
        vpc = ec2.Vpc.from_lookup(self, "VPC", is_default=True)

        # --- Subnet & SG Selection ---
        if env_name == "dev":
            subnet_id = "subnet-xxxx-dev"
            sg_id = base_stack.sg.security_group_id
        else:
            subnet_id = None
            sg_id = base_stack.sg.security_group_id

        # --- Secrets Manager Secret ---
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

        # --- IAM Role & Instance Profile from BaseStack ---
        role_arn = base_stack.instance_role.role_arn

        # --- AMI Selection ---
        if os_version == "win2022":
            ami_id = "ami-0abcdef1234567890"  # replace with your region's AMI
        else:
            ami_id = "ami-0fedcba9876543210"

        # --- CloudFormation Init Metadata ---
        # Installs Chrome using Chocolatey
        cfn_init_config = ec2.CloudFormationInit.from_config_sets(
            config_sets={
                "default": ["InstallChrome"]
            },
            configs={
                "InstallChrome": ec2.InitConfig([
                    ec2.InitCommand.shell_command(
                        "powershell -Command \"Set-ExecutionPolicy Bypass -Scope Process -Force; "
                        "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))\""
                    ),
                    ec2.InitCommand.shell_command("choco install googlechrome -y")
                ])
            }
        )

        # --- Launch Template ---
        lt = ec2.CfnLaunchTemplate(
            self,
            "WinLaunchTemplate",
            launch_template_name=f"{env_name}-WinLT",
            launch_template_data=ec2.CfnLaunchTemplate.LaunchTemplateDataProperty(
                image_id=ami_id,
                instance_type="t3.medium",
                iam_instance_profile={"arn": base_stack.instance_profile.attr_arn},
                security_group_ids=[sg_id],
                user_data=Fn.base64(
                    f"<powershell>\n"
                    f"cfn-init.exe -v -c default -s {self.stack_name} -r WindowsInstance\n"
                    f"</powershell>"
                )
            )
        )

        # --- EC2 Instance using Launch Template ---
        instance = ec2.CfnInstance(
            self,
            "WindowsInstance",
            launch_template=ec2.CfnInstance.LaunchTemplateSpecificationProperty(
                launch_template_id=lt.ref,
                version=lt.attr_latest_version_number
            ),
            subnet_id=subnet_id
        )

        # --- Outputs ---
        CfnOutput(self, "WindowsInstanceId", value=instance.ref)
        CfnOutput(self, "SecretName", value=secret.secret_name)
