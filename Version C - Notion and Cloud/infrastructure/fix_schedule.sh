#!/bin/bash

SCHED_ROLE="notion-task-scheduler-role"
FUNC_ARN="arn:aws:lambda:us-east-1:244316432377:function:notion_daily_notifier"
SCHEDULE_NAME="NotionDailyTask-10PM"

echo "Retrying EventBridge Schedule..."

# Wait for IAM propagation
echo "Waiting 10s for IAM propagation..."
sleep 10

# Create Schedule
echo "Creating Schedule..."
aws scheduler create-schedule \
    --name "$SCHEDULE_NAME" \
    --schedule-expression "cron(0 22 * * ? *)" \
    --schedule-expression-timezone "America/New_York" \
    --target "{\"Arn\": \"$FUNC_ARN\", \"RoleArn\": \"arn:aws:iam::244316432377:role/$SCHED_ROLE\"}" \
    --flexible-time-window "{\"Mode\": \"OFF\"}"

echo "✅ Schedule Creation Attempted."
