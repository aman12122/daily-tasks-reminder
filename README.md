# Daily Task Reminder System

## Project Overview
This repository contains the evolution of a personal productivity tool designed to send daily SMS reminders for unfinished tasks. It progressed through three versions, moving from a local mobile automation to a fully serverless cloud architecture.

## Versions

### [Version A - iPhone Shortcuts](./Version%20A%20-%20iPhone%20Shortcuts)
- **Tech:** iOS Shortcuts, JavaScript.
- **Mechanism:** Runs locally on iPhone.
- **Status:** Deprecated (Unreliable automation triggers).

### [Version B - Mac and Cloud](./Version%20B%20-%20Mac%20and%20Cloud)
- **Tech:** Python, SQLite, Reverse Engineering (Protobuf), AWS S3, AWS Lambda.
- **Mechanism:** A local Mac script hacks the Apple Notes database to extract tasks and syncs them to S3. Cloud Lambda sends the SMS.
- **Highlight:** Contains a custom Protobuf parser for Apple Notes.

### [Version C - Notion and Cloud (Current)](./Version%20C%20-%20Notion%20and%20Cloud)
- **Tech:** Notion API, AWS Lambda, Python, EventBridge.
- **Mechanism:** Fully serverless. Lambda queries Notion API directly and sends SMS via Twilio.
- **Status:** **Active & Production Ready**.

## Documentation
- [Learning Journey](Version%20C%20-%20Notion%20and%20Cloud/docs/LEARNING_JOURNEY.md): A log of engineering challenges, specifically reverse-engineering Apple Notes.
- [Technical Specs](Version%20C%20-%20Notion%20and%20Cloud/docs/SPECIFICATIONS.md): Architecture diagrams and API details.

## Author
Aman Vishwanath
