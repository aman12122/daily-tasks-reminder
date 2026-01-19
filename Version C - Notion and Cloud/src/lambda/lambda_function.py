import json
import urllib.request
import urllib.error
import urllib.parse
import os
import base64

# Configuration
NOTION_VERSION = "2022-06-28"
NOTION_API_BASE = "https://api.notion.com/v1"

def get_env_var(name):
    val = os.environ.get(name)
    if not val:
        print(f"Error: Missing environment variable {name}")
    return val

def fetch_notion_tasks(token, page_id):
    """
    Fetches 'to_do' blocks from the specified Notion page.
    """
    print(f"Fetching blocks from Notion Page {page_id}...")
    
    url = f"{NOTION_API_BASE}/blocks/{page_id}/children?page_size=100"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            results = data.get('results', [])
            print(f"Retrieved {len(results)} blocks.")
            
            tasks = []
            for block in results:
                if block.get('type') == 'to_do':
                    to_do = block['to_do']
                    is_checked = to_do.get('checked', False)
                    
                    # Extract text content
                    rich_text = to_do.get('rich_text', [])
                    text_content = "".join([t.get('text', {}).get('content', '') for t in rich_text])
                    
                    if text_content and not is_checked:
                        tasks.append(text_content)
            
            return tasks
            
    except urllib.error.HTTPError as e:
        print(f"Notion API Error: {e.code} - {e.read().decode('utf-8')}")
        raise e
    except Exception as e:
        print(f"Error fetching Notion data: {str(e)}")
        raise e

def send_sms(tasks, config):
    """
    Sends SMS via Twilio.
    """
    if not tasks:
        print("No tasks to send.")
        return "No tasks"
        
    msg_body = f"📅 Daily Reminder:\nYou have {len(tasks)} unfinished tasks on Notion:\n"
    for t in tasks:
        msg_body += f"- {t}\n"
        
    print("Sending SMS via Twilio...")
    url = f"https://api.twilio.com/2010-04-01/Accounts/{config['sid']}/Messages.json"
    payload = urllib.parse.urlencode({
        'To': config['to_phone'],
        'From': config['from_phone'],
        'Body': msg_body
    }).encode('utf-8')
    
    # Basic Auth
    auth_str = f"{config['sid']}:{config['token']}"
    auth_b64 = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    
    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header("Authorization", f"Basic {auth_b64}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    try:
        with urllib.request.urlopen(req) as res:
            response_body = res.read().decode('utf-8')
            print("SMS Sent successfully.")
            return response_body
    except urllib.error.HTTPError as e:
        print(f"Twilio Failed: {e.read().decode('utf-8')}")
        raise e

def lambda_handler(event, context):
    print("--- Starting Notion Daily Task Notifier ---")
    
    # 1. Load Config
    notion_token = get_env_var('NOTION_TOKEN')
    notion_page_id = get_env_var('NOTION_PAGE_ID')
    
    twilio_config = {
        'sid': get_env_var('TWILIO_SID'),
        'token': get_env_var('TWILIO_TOKEN'),
        'to_phone': get_env_var('TO_PHONE'),
        'from_phone': get_env_var('FROM_PHONE')
    }
    
    if not notion_token or not notion_page_id or not all(twilio_config.values()):
        return {"statusCode": 500, "body": "Missing configuration"}
    
    # 2. Fetch Tasks
    try:
        tasks = fetch_notion_tasks(notion_token, notion_page_id)
        print(f"Found {len(tasks)} unchecked tasks.")
    except Exception as e:
        return {"statusCode": 500, "body": f"Notion Error: {str(e)}"}
        
    if not tasks:
        return {"statusCode": 200, "body": "No unfinished tasks!"}
        
    # 3. Send SMS
    try:
        send_sms(tasks, twilio_config)
        return {"statusCode": 200, "body": "SMS sent successfully"}
    except Exception as e:
        return {"statusCode": 500, "body": f"Twilio Error: {str(e)}"}
