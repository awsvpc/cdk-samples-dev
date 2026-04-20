<pre>
Pre-requisites: 
AWS CDK installed globally:
   npm install -g aws-cdk
Docker installed (optional but useful for container builds).
Setting Up the Project
To begin, create a new directory for your CDK project and initialize it with TypeScript:

mkdir ecs-fargate
cd ecs-fargate
cdk init app --language typescript
npm install aws-cdk-lib constructs
npm install @aws-cdk/aws-ec2 @aws-cdk/aws-ecs @aws-cdk/aws-ecr @aws-cdk/aws-ecs-patterns @aws-cdk/aws-iam @aws-cdk/aws-elasticloadbalancingv2 @aws-cdk/aws-certificatemanager @aws-cdk/aws-secretsmanager
  
===========================
  
To Deploy: 

  # Synthesize the CloudFormation template to review it
cdk synth

# Show what will change
cdk diff

# Deploy the stack
cdk deploy EcsProduction --parameters imageTag=v1.2.3

# Deploy all stacks at once
cdk deploy --all

  

</pre>
