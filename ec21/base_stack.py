from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    RemovalPolicy
)
from constructs import Construct

class BaseStack(Stack):
    def __init__(self, scope: Construct, id: str, env_name: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # IAM Role with trust policy
        role = iam.Role(
            self,
            "InstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            role_name=f"{env_name}-EC2Role"
        )

        # Inline Policy
        role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject","s3:PutObject"],
                resources=["*"]
            )
        )

        # Instance Profile
        profile = iam.CfnInstanceProfile(
            self,
            "InstanceProfile",
            roles=[role.role_name],
            instance_profile_name=f"{env_name}-EC2Profile"
        )

        # Security Group
        sg = ec2.SecurityGroup(
            self,
            "InstanceSG",
            vpc=ec2.Vpc.from_lookup(self, "VPC", is_default=True),
            allow_all_outbound=True,
            security_group_name=f"{env_name}-SG"
        )
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(3389), "RDP access")
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "SSH access")

        # SSM Parameter
        param = ssm.StringParameter(
            self,
            "BaseParam",
            string_value="HelloWorld",
            parameter_name=f"/{env_name}/base_param",
            removal_policy=RemovalPolicy.RETAIN
        )

        # Expose references
        self.instance_role = role
        self.instance_profile = profile
        self.sg = sg
        self.param = param
