#!/bin/bash

BUCKET_NAME="daily-tasks-reminder-data-244316432377"
USER_NAME="reminder-mac-agent"
POLICY_NAME="ReminderS3UploadPolicy"

echo "Provisioning Cloud Resources..."

# 1. Create S3 Bucket
echo "Creating Bucket: $BUCKET_NAME"
if aws s3 ls "s3://$BUCKET_NAME" 2>&1 | grep -q 'NoSuchBucket'; then
    aws s3 mb "s3://$BUCKET_NAME"
else
    echo "Bucket already exists."
fi

# 2. Create IAM User
echo "Creating User: $USER_NAME"
aws iam create-user --user-name "$USER_NAME" || echo "User likely exists"

# 3. Create Policy Document
cat <<EOF > policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

# 4. Attach Policy (Inline)
echo "Attaching Policy..."
aws iam put-user-policy --user-name "$USER_NAME" --policy-name "$POLICY_NAME" --policy-document file://policy.json

# 5. Create Access Keys
echo "Creating Access Keys..."
aws iam create-access-key --user-name "$USER_NAME" --output json > new_agent_keys.json

echo "✅ Provisioning Complete."
echo "Bucket: $BUCKET_NAME"
echo "Keys saved to new_agent_keys.json"
