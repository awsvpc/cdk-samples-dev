class AuroraPostgresStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, "VpcLookup", is_default=False)

        kms_key = kms.Key.from_key_arn(
            self,
            "ExistingKms",
            "arn:aws:kms:us-east-1:123456789:key/abc-def"
        )

        sg = ec2.SecurityGroup(
            self,
            "AuroraSG",
            vpc=vpc
        )

        sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(5432)
        )

        subnet_group = rds.SubnetGroup(
            self,
            "AuroraSubnetGroup",
            vpc=vpc,
            description="Aurora subnets",
            vpc_subnets=ec2.SubnetSelection(
                subnet_group_name="Tier-data"
            )
        )

        cluster = rds.DatabaseCluster(
            self,
            "AuroraCluster",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.V15_2
            ),
            writer=rds.ClusterInstance.provisioned(
                "WriterInstance",
                instance_type=ec2.InstanceType("db.t3.large")
            ),
            vpc=vpc,
            subnet_group=subnet_group,
            security_groups=[sg],
            credentials=rds.Credentials.from_password(
                username="auroraadmin",
                password=cdk.SecretValue.unsafe_plain_text("MyPassword123")
            ),
            port=5432,
            storage_encrypted=True,
            kms_key=kms_key,
            removal_policy=RemovalPolicy.RETAIN
        )

        CfnOutput(self, "AuroraEndpoint", value=cluster.cluster_endpoint.hostname)
        CfnOutput(self, "AuroraPort", value=cluster.cluster_endpoint.port)
