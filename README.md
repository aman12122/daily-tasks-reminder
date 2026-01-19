# Daily Tasks Reminder System

This repository hosts different implementations of a nightly to-do list reminder system.

## Project Structure

### [Version A: iPhone Shortcuts Implementation](./Version%20A%20-%20iPhone%20Shortcuts/README.md)
The MVP version running entirely on iOS using Shortcuts and Twilio.
- **Status:** ✅ Complete
- **Architecture:** Client-side automation (No server required)
- **Features:** Reads Apple Notes ("Daily Tasks"), filters unchecked items, sends SMS via Twilio at 10pm.

<div align="center">
  <img src="Version A - iPhone Shortcuts/images/IMG_4562.PNG" width="200" alt="iOS SMS Result" />
</div>

### [Version B: Mac + Cloud Implementation](./Version%20B%20-%20Mac%20and%20Cloud/README.md)
A robust version syncing data from a Mac to the cloud, allowing delivery even when devices are offline.
- **Status:** ✅ Complete
- **Architecture:** Hybrid (Mac Daemon + AWS S3 + AWS Lambda)
- **Features:**
  - **Native SQLite Parsing:** Reads checklist status directly from Apple Notes database.
  - **Background Sync:** Runs hourly on the Mac.
  - **Serverless Delivery:** Sends SMS from the cloud (AWS Lambda).

<div align="center">
  <img src="Version B - Mac and Cloud/images/demo_sms_final.png" width="300" alt="Cloud SMS Result" />
</div>

## Development Progress

### Version B Milestones
| Logic | Cloud Storage | Delivery |
|:---:|:---:|:---:|
| <img src="Version B - Mac and Cloud/images/demo_terminal_run.png" width="250" /> | <img src="Version B - Mac and Cloud/images/demo_aws_s3.png" width="250" /> | <img src="Version B - Mac and Cloud/images/demo_aws_lambda.png" width="250" /> |
| *Python Script Parsing Notes* | *JSON Synced to S3* | *AWS Lambda Function* |

---
*Created by Aman*
