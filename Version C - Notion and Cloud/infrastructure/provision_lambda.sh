#!/bin/bash

ROLE_NAME="notion-task-lambda-role"
FUNC_NAME="notion_daily_notifier"
ACCOUNT_ID="244316432377"

echo "Provisioning Notion Lambda..."

# 1. Create Trust Policy
cat <<EOF > trust-policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# 2. Create Role
echo "Creating Role: $ROLE_NAME"
aws iam create-role --role-name "$ROLE_NAME" --assume-role-policy-document file://trust-policy.json || echo "Role likely exists"

# 3. Attach Basic Execution
aws iam attach-role-policy --role-name "$ROLE_NAME" --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# 4. Zip Code
echo "Zipping code..."
cd ../src/lambda
zip -r ../../infrastructure/function.zip lambda_function.py
cd ../../infrastructure

# 5. Create Lambda Function
# Wait a bit for role propagation
echo "Waiting for role propagation (10s)..."
sleep 10

echo "Creating Function: $FUNC_NAME"
aws lambda create-function \
    --function-name "$FUNC_NAME" \
    --zip-file fileb://function.zip \
    --handler lambda_function.lambda_handler \
    --runtime python3.9 \
    --role arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME \
    --timeout 15 \
    --environment "Variables={NOTION_TOKEN=PLACEHOLDER,NOTION_PAGE_ID=PLACEHOLDER,TWILIO_SID=PLACEHOLDER,TWILIO_TOKEN=PLACEHOLDER,TO_PHONE=PLACEHOLDER,FROM_PHONE=PLACEHOLDER}"

echo "✅ Lambda Provisioning Complete."
echo "Please go to AWS Console -> Lambda -> $FUNC_NAME -> Configuration -> Environment variables"
echo "And update the NOTION and TWILIO values."
rm trust-policy.json function.zip
