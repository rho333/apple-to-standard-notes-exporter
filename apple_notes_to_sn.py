import sys, sqlite3
import uuid as py_uuid
import hashlib
import html2text
import json
from datetime import datetime

#/Users/richardho/Library/Containers/com.apple.Notes/Data/Library/Notes/NotesV7.storedata

''' Represents a note within the Apple Notes database.

    Converts properties to Pythonic equivalents on instantiation, for easier translation
    to other note formats, and processing.
'''
class Note:
    def __init__(self, uuid_plist, createdDT, editedDT, title, body, folder):
        self.uuid = self._uuid_from_note(uuid_plist)
        self.created = self._datetime_from_timestamp(createdDT)
        self.edited = self._datetime_from_timestamp(editedDT)
        self.title = title
        self._body = body
        self._body_processed = False
        self.folder = folder

    def _uuid_from_note(self, uuid_plist_data):
        if uuid_plist_data is None:
            return str(py_uuid.uuid4())
        uuidh = hashlib.sha256(uuid_plist_data).hexdigest()
        uuid_format = "%s-%s-%s-%s-%s"
        uuid = uuid_format % (uuidh[0:8], uuidh[8:12], uuidh[12:16], uuidh[16:20], uuidh[20:32])
        return uuid
    
    def _datetime_from_timestamp(self, aapl_ts):
        adjustment_constant = 978307200 # (2001,1,1) - (1970,1,1) in seconds.
        return datetime.fromtimestamp(adjustment_constant + aapl_ts)
    
    @property
    def body(self):
        if not self._body_processed:
            self._body_processed = True
            self._body = html2text.html2text(self._body)
        return self._body

''' Generate a Python dictionary representing a valid Standard Notes export.
    The following properties will be included in the export:
      * Note title
      * Note body (HTML)
      * Creation date
      * Last edited date
    Every imported note will also be tagged with an "apple_import" tag within Standard Notes.
    
    @params list of Note objects
    @returns dict
'''
def generate_sn_export(notes):
    import_tag = {'uuid': str(py_uuid.uuid4()),
                  'content_type': 'Tag',
                  'created_at': datetime.now().isoformat(sep='T', timespec='milliseconds').strip('Z') + 'Z',
                  'updated_at': datetime.now().isoformat(sep='T', timespec='milliseconds').strip('Z') + 'Z',
                  'content': {'title': 'apple_import', 'references': [], 'appData': {}}
    }
    
    items = []
    
    for n in notes:
        items.append({'uuid': n.uuid,
                      'content_type': 'Note',
                      'created_at': n.created.isoformat(sep='T', timespec='milliseconds').strip('Z') + 'Z',
                      'updated_at': n.edited.isoformat(sep='T', timespec='milliseconds').strip('Z') + 'Z',
                      'content': {'title': n.title,
                                    'text': n.body,
                                    'references': [{'uuid': import_tag['uuid'],
                                                      'content_type': 'Tag',
                                                    }],
                                    'appData': {}
                      }
        })
        
        import_tag['content']['references'].append({'uuid': n.uuid, 'content_type': 'Note'})
    
    items.append(import_tag)
        
    return {'items': items}

''' Loads a complete set of notes from Apple's Notes database (including iCloud Notes).
    
    @params None
    @returns List of Note objects
'''
def load_notes(target_db):
    try:
        conn = sqlite3.connect(target_db)
    except:
        print("Failed to load database file - please check your path")

    cursor = conn.cursor()

    results = cursor.execute('SELECT Z_PK, ZDATECREATED, ZDATEEDITED, ZBODY, ZFOLDER, ZTITLE, ZUNIVERSALLYUNIQUEID FROM ZNOTE')
    note_metadata = results.fetchall()

    results = cursor.execute('SELECT Z_PK, ZHTMLSTRING FROM ZNOTEBODY')
    note_content = results.fetchall()
    
    note_body_ids = {}
    for (id, content) in note_content:
        note_body_ids[id] = content

    loaded_notes = []
    for z_pk, createddate, editeddate, body_id, folder, title, uuid_data in note_metadata:
        loaded_notes.append(Note(uuid_data, createddate, editeddate, title, note_body_ids[body_id], folder))

    return loaded_notes

if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        target_db = args[1]
    else:
        target_db = input("Please enter DB file path: ")
    notes = load_notes(target_db)
    sn_export_data = json.dumps(generate_sn_export(notes))
    
    outfile = open('Standard_Notes-apple_notes_export.txt', 'w')
    outfile.write(sn_export_data)
    outfile.close()
