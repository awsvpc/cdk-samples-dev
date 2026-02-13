#!/bin/bash

ENV=$1  # dev or prod
STACK=$2

if [ "$ENV" == "dev" ]; then
    PROFILE="dev"
elif [ "$ENV" == "prod" ]; then
    PROFILE="prod"
else
    echo "Specify dev or prod"
    exit 1
fi

cdk deploy $STACK -c env=$ENV --profile $PROFILE --require-approval never
