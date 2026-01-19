#!/bin/bash
echo "--- AWS Configuration Helper ---"
echo "This script will help you set up your AWS credentials."
echo ""

read -p "Enter your Access Key ID (e.g., AKIA...): " access_key
read -s -p "Enter your Secret Access Key: " secret_key
echo ""
read -p "Enter your preferred Region (default: us-east-1): " region
region=${region:-us-east-1}

echo ""
echo "Configuring AWS CLI..."

aws configure set aws_access_key_id "$access_key"
aws configure set aws_secret_access_key "$secret_key"
aws configure set default.region "$region"
aws configure set default.output_format json

echo ""
echo "Verifying connection..."
identity=$(aws sts get-caller-identity 2>&1)

if [ $? -eq 0 ]; then
    echo "✅ Success! Connected as:"
    echo "$identity"
else
    echo "❌ Error: Could not connect to AWS. Please check your keys."
    echo "$identity"
fi
