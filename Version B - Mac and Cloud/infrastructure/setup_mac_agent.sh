#!/bin/bash

PLIST_NAME="com.aman.dailytasks.plist"
DEST_DIR="$HOME/Library/LaunchAgents"
PYTHON_PATH="/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
SCRIPT_PATH="/Users/aman/Desktop/Reminder System/Version B - Mac and Cloud/src/sync_tasks.py"

echo "Setting up Mac Agent..."

# Create Plist
cat <<EOF > "$PLIST_NAME"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aman.dailytasks</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$SCRIPT_PATH</string>
    </array>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>StandardOutPath</key>
    <string>/tmp/com.aman.dailytasks.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/com.aman.dailytasks.err</string>
</dict>
</plist>
EOF

# Move to LaunchAgents
mv "$PLIST_NAME" "$DEST_DIR/"

# Load Agent
# Unload first just in case
launchctl unload "$DEST_DIR/$PLIST_NAME" 2>/dev/null
launchctl load "$DEST_DIR/$PLIST_NAME"

echo "✅ Mac Agent Installed and Loaded."
echo "Logs are at /tmp/com.aman.dailytasks.out"
