from aws_cdk import Tags
Tags.of(instance).add("Environment", env_name)
