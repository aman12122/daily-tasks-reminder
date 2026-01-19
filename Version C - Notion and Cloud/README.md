# Daily Task Reminder System

A serverless automated reminder system that checks your Notion Dashboard for unfinished tasks and sends you an SMS summary every night.

![Architecture](docs/architecture.png)

## 🚀 Evolution of the Project

This project evolved through three distinct versions, each solving a specific engineering challenge:

| Version | Architecture | Key Feature | Limitation Solved |
|---------|-------------|-------------|-------------------|
| **A** | **iPhone Shortcuts** | Zero-code, runs on phone | Initial prototype |
| **B** | **Mac + Cloud** | Hybrid (Mac syncs DB -> AWS) | "Phone must be unlocked" |
| **C** | **Fully Serverless** | Notion API + AWS Lambda | "Mac must be on" |

---

## 📂 Project Structure

```
Version C - Notion and Cloud/
├── docs/                  # Documentation & Planning
│   ├── SPECIFICATIONS.md  # Technical specs
│   └── LEARNING_JOURNEY.md# Engineering log & decisions
├── infrastructure/        # Infrastructure as Code (Shell scripts)
│   ├── provision_lambda.sh
│   └── provision_schedule.sh
└── src/
    └── lambda/
        └── lambda_function.py  # Main Python logic
```

## 🛠️ Technology Stack

- **Cloud Provider:** AWS (Free Tier)
- **Compute:** AWS Lambda (Python 3.9)
- **Scheduling:** Amazon EventBridge (Cron)
- **Data Source:** Notion API
- **Notification:** Twilio SMS API

## ⚡ Quick Start (Deployment)

1. **Prerequisites:**
   - AWS CLI configured
   - Twilio Account (SID + Token)
   - Notion Integration Token

2. **Deploy Infrastructure:**
   ```bash
   cd infrastructure
   bash provision_lambda.sh
   bash provision_schedule.sh
   ```

3. **Configure Secrets:**
   Go to the AWS Lambda Console -> Configuration -> Environment Variables and set:
   - `NOTION_TOKEN`
   - `NOTION_PAGE_ID`
   - `TWILIO_SID`
   - `TWILIO_TOKEN`
   - `TO_PHONE`
   - `FROM_PHONE`

## 📝 Learning Highlights

- **Protobuf Reverse Engineering:** In Version B, we reverse-engineered the Apple Notes SQLite database (Protobuf blobs) to extract checklist status without using the Apple Notes API.
- **Serverless Architecture:** Moved from local polling (Mac `launchd`) to event-driven cloud logic (EventBridge -> Lambda) to achieve 100% uptime reliability.
