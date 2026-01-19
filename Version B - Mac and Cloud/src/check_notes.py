import sqlite3
import zlib
import sys
import os

# Path to Notes DB
DB_PATH = os.path.expanduser("~/Library/Group Containers/group.com.apple.notes/NoteStore.sqlite")

class ProtoReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read_varint(self):
        result = 0
        shift = 0
        while True:
            if self.pos >= len(self.data):
                # End of stream is normal in some contexts, but here it might break
                # raising exception to catch it
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
            # Skip unknown wire types? No, just fail or return None
            return None, None, None

def get_note_data(note_title):
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return None

    try:
        # Use Read-Only mode to avoid locking issues
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = conn.cursor()
    except sqlite3.OperationalError as e:
        print(f"Could not open database: {e}")
        print("Ensure Terminal has Full Disk Access in System Settings.")
        return None
    
    # Find note PK by Title
    # Schema varies by macOS version. 
    # Usually ZICCLOUDSYNCINGOBJECT has ZTITLE1 (Title) and ZNOTE data is linked.
    # We'll try a broad search.
    try:
        cursor.execute("""
            SELECT Z_PK, ZTITLE1, ZSNIPPET, ZNOTE
            FROM ZICCLOUDSYNCINGOBJECT 
            WHERE ZTITLE1 = ? AND ZMARKEDFORDELETION = 0
        """, (note_title,))
    except Exception as e:
        print(f"Query error (schema might be different): {e}")
        return None
    
    rows = cursor.fetchall()
    if not rows:
        print(f"Note '{note_title}' not found in DB.")
        conn.close()
        return None
        
    # We found the object. The Note Data might be in ZICNOTEDATA linked by ZNOTE field.
    # Or for some versions, the Object itself has data.
    # Usually: ZICCLOUDSYNCINGOBJECT (Z_PK) <-- ZICNOTEDATA (ZNOTE)
    
    target_pk = rows[0][0] # Z_PK of the note object
    
    cursor.execute("SELECT ZDATA FROM ZICNOTEDATA WHERE ZNOTE = ?", (target_pk,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row[0]:
        print("No data found for note (might be text-only or empty).")
        return None
        
    blob = row[0]
    try:
        # Apple Notes data is gzipped
        return zlib.decompress(blob, 16+zlib.MAX_WBITS)
    except:
        try:
            return zlib.decompress(blob)
        except:
            return blob

def parse_note(data):
    # This is a heuristic parser for the protobuf structure
    # Top level: Wrapper -> Field 2 -> Field 3 (NoteData)
    reader = ProtoReader(data)
    document = None
    
    # Scan top level for Field 2 (Document)
    while True:
        field, wtype, val = reader.read_field()
        if field is None: break
        if field == 2 and wtype == 2:
            document = val
            break
            
    if not document:
        # Fallback
        document = data
        
    # Inside Document, look for Field 3 (NoteData)
    reader = ProtoReader(document)
    note_data = None
    while True:
        field, wtype, val = reader.read_field()
        if field is None: break
        if field == 3 and wtype == 2:
            note_data = val
            break
            
    if not note_data:
        note_data = document

    # Inside NoteData: Field 2 is Text (String), Field 5 is AttributeRuns (Repeated)
    text = ""
    attribute_runs = []
    
    reader = ProtoReader(note_data)
    while True:
        field, wtype, val = reader.read_field()
        if field is None: break
        
        if field == 2 and wtype == 2:
            try:
                # The text field often contains a byte header, skip it?
                # Actually it is usually a length-delimited string.
                # Sometimes it has a varint prefix?
                text = val.decode('utf-8', errors='ignore')
            except:
                pass
        elif field == 5 and wtype == 2:
            attribute_runs.append(val)
            
    if not text:
        return ["Error: No text found in protobuf"]

    # Process AttributeRuns
    current_idx = 0
    checklist_items = []
    
    # Sort runs? No, they usually come in order.
    # But text might be shorter than sum of runs if we messed up decoding.
    
    for run_data in attribute_runs:
        run_reader = ProtoReader(run_data)
        length = 0
        paragraph_style = None
        
        while True:
            f, w, v = run_reader.read_field()
            if f is None: break
            if f == 1 and w == 0:
                length = v
            elif f == 2 and w == 2:
                paragraph_style = v
                
        # Check ParagraphStyle
        is_checklist = False
        is_checked = False
        
        if paragraph_style:
            ps_reader = ProtoReader(paragraph_style)
            while True:
                f, w, v = ps_reader.read_field()
                if f is None: break
                
                # Field 1 = Style Type? (103 = Checklist?)
                # Field 2 = Indent?
                # Field 4 = ?
                # Field 5 = Checklist Status (nested message)
                
                if f == 1 and w == 0 and v == 103:
                    is_checklist = True
                
                if f == 5 and w == 2:
                    # Checklist Info
                    cl_reader = ProtoReader(v)
                    while True:
                        f2, w2, v2 = cl_reader.read_field()
                        if f2 is None: break
                        # UUID is field 1 usually
                        # Status is field 2? (1 = Checked, 0 = Unchecked)
                        if f2 == 2 and w2 == 0:
                            is_checked = (v2 == 1)
        
        segment = text[current_idx : current_idx + length]
        
        # Apple uses \n for newlines.
        # Checklists are usually single lines.
        if is_checklist:
            lines = segment.split('\n')
            for line in lines:
                clean_line = line.strip()
                if clean_line:
                    # If the run covers multiple lines, they share the style.
                    # This happens if user pastes text into a checklist item?
                    # But usually each item is a paragraph.
                    status = "[x]" if is_checked else "[ ]"
                    checklist_items.append(f"{status} {clean_line}")
        
        current_idx += length
        
    return checklist_items

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 check_notes.py <Note Title>")
        sys.exit(1)
        
    title = sys.argv[1]
    items = get_note_data(title)
    
    if items is None:
        # DB access failed or note not found
        # Fallback to explaining why
        pass
    else:
        # If get_note_data returned raw bytes (it returns bytes from zlib), parse it
        # Wait, my function returns bytes, but main expects items?
        # Let's fix the main block.
        data = items
        parsed = parse_note(data)
        for p in parsed:
            print(p)
