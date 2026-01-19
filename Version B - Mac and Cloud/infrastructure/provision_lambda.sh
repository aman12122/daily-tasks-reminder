#!/bin/bash

ROLE_NAME="daily-task-lambda-role"
FUNC_NAME="daily_task_notifier"
BUCKET_NAME="daily-tasks-reminder-data-244316432377"
ACCOUNT_ID="244316432377"

echo "Provisioning Lambda..."

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

# 4. Attach S3 Read Policy (Inline)
cat <<EOF > lambda-s3-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

echo "Attaching S3 Policy..."
aws iam put-role-policy --role-name "$ROLE_NAME" --policy-name "S3ReadAccess" --policy-document file://lambda-s3-policy.json

# 5. Zip Code
echo "Zipping code..."
cd lambda
zip -r ../function.zip lambda_function.py
cd ..

# 6. Create Lambda Function
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
    --timeout 10 \
    --environment "Variables={S3_BUCKET=$BUCKET_NAME,S3_KEY=tasks.json,TWILIO_ACCOUNT_SID=PLACEHOLDER,TWILIO_AUTH_TOKEN=PLACEHOLDER,TO_PHONE=PLACEHOLDER,FROM_PHONE=PLACEHOLDER}"

echo "✅ Lambda Provisioning Complete."
echo "Please go to AWS Console -> Lambda -> $FUNC_NAME -> Configuration -> Environment variables"
echo "And update the TWILIO values."
