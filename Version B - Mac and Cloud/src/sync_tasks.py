import sqlite3
import zlib
import sys
import os
import json
import subprocess
import datetime

# Configuration
NOTE_NAME = "Daily Tasks"
OUTPUT_FILE = "tasks.json"
DB_PATH = os.path.expanduser("~/Library/Group Containers/group.com.apple.notes/NoteStore.sqlite")
S3_BUCKET = "daily-tasks-reminder-data-244316432377"
AWS_PROFILE = "mac-agent"

class ProtoReader:
    """
    Helper class to read Protobuf-encoded data from Apple Notes.
    """
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read_varint(self):
        result = 0
        shift = 0
        while True:
            if self.pos >= len(self.data):
                raise Exception("EOF")
            b = self.data[self.pos]
            self.pos += 1
            result |= (b & 0x7f) << shift
            if not (b & 0x80):
                return result
            shift += 7

    def read_field(self):
        if self.pos >= len(self.data):
            return None, None, None
        
        try:
            key = self.read_varint()
        except:
            return None, None, None
            
        field_number = key >> 3
        wire_type = key & 0x07
        
        if wire_type == 0: # Varint
            try:
                val = self.read_varint()
            except:
                return None, None, None
            return field_number, wire_type, val
        elif wire_type == 2: # Length-delimited
            try:
                length = self.read_varint()
            except:
                return None, None, None
            if self.pos + length > len(self.data):
                return None, None, None
            val = self.data[self.pos:self.pos+length]
            self.pos += length
            return field_number, wire_type, val
        elif wire_type == 1: # 64-bit
            val = self.data[self.pos:self.pos+8]
            self.pos += 8
            return field_number, wire_type, val
        elif wire_type == 5: # 32-bit
            val = self.data[self.pos:self.pos+4]
            self.pos += 4
            return field_number, wire_type, val
        else:
            return None, None, None

def get_note_blob(note_title):
    """
    Fetches the raw gzipped protobuf blob for the note from the SQLite DB.
    """
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return None

    try:
        # Open in read-only mode to prevent locking
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = conn.cursor()
    except sqlite3.OperationalError as e:
        print(f"Error opening database: {e}")
        print("Please ensure your Terminal/Editor has 'Full Disk Access'.")
        return None
    
    try:
        # Find Note ID
        cursor.execute("""
            SELECT Z_PK 
            FROM ZICCLOUDSYNCINGOBJECT 
            WHERE ZTITLE1 = ? AND ZMARKEDFORDELETION = 0
        """, (note_title,))
        
        rows = cursor.fetchall()
        if not rows:
            print(f"Note '{note_title}' not found.")
            conn.close()
            return None
        
        note_pk = rows[0][0]
        
        # Get Data
        cursor.execute("SELECT ZDATA FROM ZICNOTEDATA WHERE ZNOTE = ?", (note_pk,))
        row = cursor.fetchone()
        conn.close()
        
        if not row or not row[0]:
            print("Note has no content data.")
            return None
            
        return row[0]
        
    except Exception as e:
        print(f"Database query error: {e}")
        return None

def extract_unchecked_items(blob):
    """
    Parses the blob and returns a list of UNCHECKED task strings.
    """
    try:
        data = zlib.decompress(blob, 16+zlib.MAX_WBITS)
    except:
        try:
            data = zlib.decompress(blob)
        except:
            data = blob

    # Traverse Protobuf structure
    reader = ProtoReader(data)
    document = None
    
    # 1. Find Document (Field 2)
    while True:
        f, w, v = reader.read_field()
        if f is None: break
        if f == 2 and w == 2:
            document = v
            break
    if not document: document = data

    # 2. Find NoteData (Field 3)
    reader = ProtoReader(document)
    note_data = None
    while True:
        f, w, v = reader.read_field()
        if f is None: break
        if f == 3 and w == 2:
            note_data = v
            break
    if not note_data: note_data = document

    # 3. Extract Text and Attributes
    text = ""
    attribute_runs = []
    
    reader = ProtoReader(note_data)
    while True:
        f, w, v = reader.read_field()
        if f is None: break
        if f == 2 and w == 2:
            try:
                text = v.decode('utf-8', errors='ignore')
            except: pass
        elif f == 5 and w == 2:
            attribute_runs.append(v)

    if not text:
        return []

    # 4. Map Attributes to Text
    unchecked_tasks = []
    
    # Apple Notes uses \n as the delimiter for paragraphs/list items.
    # We need to reconstruct the full text and find the style for each line.
    
    # First, map character indices to style info
    # We specifically care if a character belongs to a checklist and if it is checked
    char_styles = [None] * len(text)
    current_idx = 0
    
    for run in attribute_runs:
        run_reader = ProtoReader(run)
        length = 0
        style = None
        
        while True:
            f, w, v = run_reader.read_field()
            if f is None: break
            if f == 1 and w == 0:
                length = v
            elif f == 2 and w == 2:
                style = v
        
        # Parse Style
        is_checklist = False
        is_checked = False
        
        if style:
            s_reader = ProtoReader(style)
            while True:
                f, w, v = s_reader.read_field()
                if f is None: break
                if f == 1 and w == 0 and v == 103:
                    is_checklist = True
                if f == 5 and w == 2: # Checklist status
                    c_reader = ProtoReader(v)
                    while True:
                        f2, w2, v2 = c_reader.read_field()
                        if f2 is None: break
                        if f2 == 2 and w2 == 0:
                            is_checked = (v2 == 1)
                            
        # Apply to range
        end_idx = min(current_idx + length, len(text))
        for i in range(current_idx, end_idx):
            char_styles[i] = (is_checklist, is_checked)
            
        current_idx += length
        
    # Now split text into lines and check the style of the first character of each line
    # (Checklist items are paragraphs, so the style at the start usually applies to the whole line)
    start_of_line = 0
    while start_of_line < len(text):
        try:
            end_of_line = text.index('\n', start_of_line)
        except ValueError:
            end_of_line = len(text)
            
        line_content = text[start_of_line:end_of_line].strip()
        
        if line_content:
            # Check style at the start of the line
            style_info = char_styles[start_of_line] if start_of_line < len(char_styles) else (False, False)
            
            # Fallback: if style is None (no run covering it?), assume not checklist
            if style_info is None:
                style_info = (False, False)
                
            is_checklist, is_checked = style_info
            
            if is_checklist and not is_checked:
                # IMPORTANT: Apple Notes sometimes includes the hidden 'check' character (OBJ replacement)
                # or just raw text. We strip any weird invisible chars if needed, but usually strip() is enough.
                # Actually, sometimes the first char is a special object placeholder if it's an attachment, 
                # but for checklists it's usually text.
                unchecked_tasks.append(line_content)
                
        start_of_line = end_of_line + 1
                    
    return unchecked_tasks

def save_json(tasks):
    data = {
        "last_synced": datetime.datetime.now().isoformat(),
        "tasks": tasks
    }
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Successfully saved {len(tasks)} tasks to {OUTPUT_FILE}")

def upload_to_s3():
    """
    Uploads the generated tasks.json to S3 using the configured profile.
    """
    print(f"Uploading {OUTPUT_FILE} to s3://{S3_BUCKET}...")
    try:
        subprocess.run(
            ["aws", "s3", "cp", OUTPUT_FILE, f"s3://{S3_BUCKET}/{OUTPUT_FILE}", "--profile", AWS_PROFILE],
            check=True
        )
        print("Upload successful.")
    except subprocess.CalledProcessError as e:
        print(f"Upload failed: {e}")
        # Don't exit, just log error, as local save was successful

def main():
    print(f"--- Syncing '{NOTE_NAME}' (Native Checklist Mode) ---")
    
    blob = get_note_blob(NOTE_NAME)
    if not blob:
        sys.exit(1)
        
    tasks = extract_unchecked_items(blob)
    save_json(tasks)
    upload_to_s3()

if __name__ == "__main__":
    main()
