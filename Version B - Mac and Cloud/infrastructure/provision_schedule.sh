#!/bin/bash

SCHED_ROLE="daily-task-scheduler-role"
FUNC_ARN="arn:aws:lambda:us-east-1:244316432377:function:daily_task_notifier"
SCHEDULE_NAME="DailyTaskReminder-10PM"

echo "Provisioning EventBridge Schedule..."

# 1. Create Role for Scheduler
cat <<EOF > scheduler-trust.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "scheduler.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

aws iam create-role --role-name "$SCHED_ROLE" --assume-role-policy-document file://scheduler-trust.json || echo "Role likely exists"

# 2. Attach Policy to invoke Lambda
cat <<EOF > scheduler-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "lambda:InvokeFunction",
            "Resource": "$FUNC_ARN"
        }
    ]
}
EOF

aws iam put-role-policy --role-name "$SCHED_ROLE" --policy-name "InvokeLambda" --policy-document file://scheduler-policy.json

# 3. Create Schedule
# 10:00 PM EST daily
echo "Creating Schedule..."
aws scheduler create-schedule \
    --name "$SCHEDULE_NAME" \
    --schedule-expression "cron(0 22 * * ? *)" \
    --schedule-expression-timezone "America/New_York" \
    --target "{\"Arn\": \"$FUNC_ARN\", \"RoleArn\": \"arn:aws:iam::244316432377:role/$SCHED_ROLE\"}" \
    --flexible-time-window "{\"Mode\": \"OFF\"}"

echo "✅ Schedule Created: $SCHEDULE_NAME (10:00 PM EST)"
