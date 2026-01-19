# Learning Journey: From Scripts to Serverless

This document captures the engineering decisions, challenges, and "Aha!" moments throughout the development of the Reminder System.

## Phase 1: The "Hobbyist" Approach (Version A)
**Goal:** Just get it working on my phone.

- **Attempt:** Used iOS Shortcuts automation.
- **Challenge:** iOS Automation is fragile. It requires the phone to be unlocked to run complex scripts or read Notes reliably.
- **Lesson:** Client-side automation (on a personal device) is not reliable for "infrastructure-grade" reliability.

## Phase 2: The "Hacker" Approach (Version B)
**Goal:** Bypass the phone. Use the Mac which is more powerful.

- **The Big Problem:** Apple Notes does not have a public API.
- **The Solution:** Reverse Engineering.
    - We discovered the local SQLite database at `~/Library/Group Containers/group.com.apple.notes/NoteStore.sqlite`.
    - **Deep Dive:** The content wasn't plain text; it was Gzipped Protobuf blobs.
    - **Implementation:** Wrote a custom Python parser (`ProtoReader` class in `sync_tasks.py`) to decode the binary data, find the checkbox attribute bits, and extract the text.
- **Architecture:** Hybrid.
    - Mac (Local): Runs a cron job (`launchd`) to read DB -> Upload JSON to AWS S3.
    - Cloud (AWS): EventBridge triggers Lambda -> Reads S3 -> Sends SMS.
- **Limitation:** The Mac still needed to be turned on (or at least wake up) to sync the data. If I left my laptop at work, the system failed.

## Phase 3: The "Engineer" Approach (Version C)
**Goal:** 100% Cloud. No local dependencies.

- **Pivot:** Switched from Apple Notes (closed ecosystem) to Notion (Open API).
- **Architecture:**
    - **AWS Lambda:** The core brain.
    - **Notion API:** Acts as the database. We use the `blocks/{id}/children` endpoint to read the dashboard page directly.
    - **Environment Variables:** Moved all secrets (Notion Token, Twilio SID) to encrypted Lambda environment variables for security.
- **Outcome:**
    - No server to manage.
    - No laptop needed.
    - Costs ~$0.00 (Free Tier) until massive scale.
    - High Reliability.

## Key Takeaways
1. **Data Ownership:** Proprietary formats (like Apple Notes' internal DB) are fun to hack but bad for production systems. Open APIs (Notion) are superior for integration.
2. **State Management:** Decoupling "State" (Notion/S3) from "Logic" (Lambda) allows the system to be stateless and robust.
3. **Security:** Never hardcode API keys. Using AWS Parameter Store or Lambda Env Vars is the standard way to go.
