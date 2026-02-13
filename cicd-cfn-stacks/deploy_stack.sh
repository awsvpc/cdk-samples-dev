#!/bin/bash
set -e

STACK_NAME=$1
TEMPLATE_FILE=$2
PARAM_FILE=$3
REGION=${AWS_REGION:-us-east-1}
TAGS=$4   # e.g., "Key=Environment,Value=Prod Key=Team,Value=DevOps"

# Validate inputs
if [[ -z "$STACK_NAME" || -z "$TEMPLATE_FILE" || -z "$PARAM_FILE" ]]; then
  echo "Usage: $0 <stack_name> <template_file> <parameter_file> [tags]"
  exit 1
fi

echo "Deploying stack: $STACK_NAME"
echo "Template: $TEMPLATE_FILE"
echo "Parameters: $PARAM_FILE"
echo "Region: $REGION"
echo "Tags: $TAGS"

aws cloudformation deploy \
  --stack-name "$STACK_NAME" \
  --template-file "$TEMPLATE_FILE" \
  --parameter-overrides $(jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' "$PARAM_FILE") \
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
  ${TAGS:+--tags $TAGS} \
  --region "$REGION"

echo "Stack $STACK_NAME deployment complete."
