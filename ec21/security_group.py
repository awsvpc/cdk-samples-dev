sg = ec2.SecurityGroup(
    self,
    "AppSecurityGroup",
    vpc=vpc,
    allow_all_outbound=True,
    description="App security group"
)

# HTTP
sg.add_ingress_rule(
    ec2.Peer.any_ipv4(),
    ec2.Port.tcp(80),
    "Allow HTTP"
)

# HTTPS
sg.add_ingress_rule(
    ec2.Peer.any_ipv4(),
    ec2.Port.tcp(443),
    "Allow HTTPS"
)

# SSH from office IP
sg.add_ingress_rule(
    ec2.Peer.ipv4("1.2.3.4/32"),
    ec2.Port.tcp(22),
    "Allow SSH from office"
)


==========

ec2.CfnSecurityGroupIngress(
    self,
    "HTTPRule",
    group_id=sg.security_group_id,
    ip_protocol="tcp",
    from_port=80,
    to_port=80,
    cidr_ip="0.0.0.0/0"
)
