import json
import urllib.request
import urllib.parse
import os
import boto3
import base64

def lambda_handler(event, context):
    print("Starting Daily Task Notifier...")
    
    s3_bucket = os.environ.get('S3_BUCKET')
    s3_key = os.environ.get('S3_KEY', 'tasks.json')
    twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
    to_phone = os.environ.get('TO_PHONE')
    from_phone = os.environ.get('FROM_PHONE')
    
    if not all([s3_bucket, twilio_sid, twilio_token, to_phone, from_phone]):
        print("Error: Missing environment variables.")
        return {"statusCode": 500, "body": "Missing configuration"}
    
    # 1. Fetch tasks from S3
    s3 = boto3.client('s3')
    try:
        print(f"Fetching {s3_key} from {s3_bucket}...")
        response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
        content = response['Body'].read().decode('utf-8')
        data = json.loads(content)
        tasks = data.get('tasks', [])
        print(f"Found {len(tasks)} tasks.")
    except Exception as e:
        print(f"Error reading S3: {e}")
        return {"statusCode": 500, "body": f"S3 Error: {str(e)}"}
        
    if not tasks:
        print("No tasks pending. Skipping SMS.")
        return {"statusCode": 200, "body": "No tasks to remind"}
        
    # 2. Format Message
    msg_body = f"📅 Daily Reminder:\nYou have {len(tasks)} unfinished tasks:\n"
    for t in tasks:
        msg_body += f"- {t}\n"
        
    # 3. Send SMS via Twilio
    print("Sending SMS via Twilio...")
    url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
    payload = urllib.parse.urlencode({
        'To': to_phone,
        'From': from_phone,
        'Body': msg_body
    }).encode('utf-8')
    
    # Basic Auth
    auth_str = f"{twilio_sid}:{twilio_token}"
    auth_b64 = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    
    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header("Authorization", f"Basic {auth_b64}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    try:
        with urllib.request.urlopen(req) as res:
            response_body = res.read().decode('utf-8')
            print(f"Twilio Success: {response_body}")
            return {"statusCode": 200, "body": "SMS Sent Successfully"}
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        print(f"Twilio Failed: {error_msg}")
        return {"statusCode": 500, "body": f"Twilio Error: {error_msg}"}
    except Exception as e:
        print(f"Network/Other Error: {e}")
        return {"statusCode": 500, "body": str(e)}
