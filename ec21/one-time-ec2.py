class OneTimeInstanceStack(Stack):

    def __init__(self, scope, construct_id, *,
                 os_type: str,
                 volume_size: int,
                 iam_role_name: str,
                 **kwargs):

        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, "VPC", is_default=True)

        sg = ec2.SecurityGroup(
            self,
            "InstanceSG",
            vpc=vpc
        )

        if os_type == "linux":
            ami = ec2.MachineImage.latest_amazon_linux()
            user_data = ec2.UserData.for_linux()
        else:
            ami = ec2.MachineImage.latest_windows()
            user_data = ec2.UserData.for_windows()

        role = iam.Role.from_role_name(
            self,
            "ExistingRole",
            iam_role_name
        )

        instance = ec2.Instance(
            self,
            "OneTimeInstance",
            vpc=vpc,
            instance_type=ec2.InstanceType("t3.medium"),
            machine_image=ami,
            security_group=sg,
            role=role,
            user_data=user_data,
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(
                        volume_size,
                        delete_on_termination=False
                    )
                )
            ]
        )

        instance.apply_removal_policy(cdk.RemovalPolicy.RETAIN)


"""
user_data = ec2.UserData.for_windows()
user_data.add_commands(
    "powershell Install-WindowsFeature -name Web-Server"
)
"""
