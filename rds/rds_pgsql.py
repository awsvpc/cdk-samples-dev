class PostgresRdsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # 1️⃣ Lookup Existing VPC
        vpc = ec2.Vpc.from_lookup(
            self,
            "ExistingVpc",
            is_default=False
        )

        # 2️⃣ Lookup Private Subnets by Tag Tier=data
        subnets = ec2.Subnet.from_subnet_attributes(
            self,
            "SubnetAz1",
            subnet_id="subnet-az1-id",  # replace
            availability_zone="us-east-1a"
        )

        subnet2 = ec2.Subnet.from_subnet_attributes(
            self,
            "SubnetAz2",
            subnet_id="subnet-az2-id",  # replace
            availability_zone="us-east-1b"
        )

        subnet_group = rds.SubnetGroup(
            self,
            "RdsSubnetGroup",
            vpc=vpc,
            description="Private data subnets",
            vpc_subnets=ec2.SubnetSelection(
                subnets=[subnets, subnet2]
            )
        )

        # 3️⃣ Security Group
        sg = ec2.SecurityGroup(
            self,
            "RdsSecurityGroup",
            vpc=vpc,
            description="Allow Postgres access"
        )

        sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(5432),
            "Allow Postgres"
        )

        # 4️⃣ Existing KMS Key
        kms_key = kms.Key.from_key_arn(
            self,
            "ExistingKmsKey",
            "arn:aws:kms:us-east-1:123456789:key/abc-def"
        )

        # 5️⃣ Monitoring Role
        monitoring_role = iam.Role(
            self,
            "RdsMonitoringRole",
            assumed_by=iam.ServicePrincipal("monitoring.rds.amazonaws.com")
        )

        monitoring_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AmazonRDSEnhancedMonitoringRole"
            )
        )

        # 6️⃣ Parameter Group
        param_group = rds.ParameterGroup(
            self,
            "PostgresParamGroup",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.V15
            ),
            parameters={
                "log_min_duration_statement": "1000"
            }
        )

        # 7️⃣ Option Group (for standard RDS)
        option_group = rds.OptionGroup(
            self,
            "PostgresOptionGroup",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.V15
            ),
            configurations=[]
        )

        # 8️⃣ Create RDS Instance
        db = rds.DatabaseInstance(
            self,
            "PostgresInstance",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.V15
            ),
            instance_type=ec2.InstanceType("db.t3.large"),
            vpc=vpc,
            subnet_group=subnet_group,
            security_groups=[sg],
            credentials=rds.Credentials.from_password(
                username="dbadmin",
                password=cdk.SecretValue.unsafe_plain_text("MyPassword123")
            ),
            port=5432,
            multi_az=False,
            storage_encrypted=True,
            kms_key=kms_key,
            monitoring_interval=cdk.Duration.seconds(60),
            monitoring_role=monitoring_role,
            parameter_group=param_group,
            option_group=option_group,
            removal_policy=RemovalPolicy.RETAIN
        )

        CfnOutput(self, "PostgresEndpoint", value=db.db_instance_endpoint_address)
        CfnOutput(self, "PostgresPort", value=db.db_instance_endpoint_port)
