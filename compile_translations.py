"""
Simple translation compiler for Django without gettext
This creates a basic .mo file from .po file for testing
"""
import os
import struct

def compile_po_to_mo(po_file, mo_file):
    """Convert .po file to .mo file format"""
    translations = {}
    
    with open(po_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple parser for msgid/msgstr pairs
    lines = content.split('\n')
    current_msgid = None
    current_msgstr = None
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('msgid "') and not line.startswith('msgid ""'):
            current_msgid = line[7:-1]  # Remove 'msgid "' and '"'
        elif line.startswith('msgstr "') and current_msgid:
            current_msgstr = line[8:-1]  # Remove 'msgstr "' and '"'
            if current_msgstr:  # Only add non-empty translations
                translations[current_msgid] = current_msgstr
            current_msgid = None
            current_msgstr = None
    
    # Create binary .mo file
    keys = sorted(translations.keys())
    values = [translations[k] for k in keys]
    
    # MO file format: magic number + version + number of strings + offsets
    koffsets = []
    voffsets = []
    kencoded = []
    vencoded = []
    
    for k, v in zip(keys, values):
        kencoded.append(k.encode('utf-8'))
        vencoded.append(v.encode('utf-8'))
    
    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart
    for k in kencoded:
        valuestart += len(k) + 1
    
    koffsets = []
    voffsets = []
    
    offset = keystart
    for k in kencoded:
        koffsets.append((len(k), offset))
        offset += len(k) + 1
    
    offset = valuestart
    for v in vencoded:
        voffsets.append((len(v), offset))
        offset += len(v) + 1
    
    # Write MO file
    with open(mo_file, 'wb') as f:
        # Magic number for little-endian .mo files
        f.write(struct.pack('<I', 0x950412de))
        f.write(struct.pack('<I', 0))  # Version
        f.write(struct.pack('<I', len(keys)))  # Number of strings
        f.write(struct.pack('<I', 7 * 4))  # Offset of key table
        f.write(struct.pack('<I', 7 * 4 + 8 * len(keys)))  # Offset of value table
        f.write(struct.pack('<I', 0))  # Hash table size (unused)
        f.write(struct.pack('<I', 0))  # Hash table offset (unused)
        
        # Write key offsets and lengths
        for length, offset in koffsets:
            f.write(struct.pack('<I', length))
            f.write(struct.pack('<I', offset))
        
        # Write value offsets and lengths
        for length, offset in voffsets:
            f.write(struct.pack('<I', length))
            f.write(struct.pack('<I', offset))
        
        # Write keys
        for k in kencoded:
            f.write(k)
            f.write(b'\x00')
        
        # Write values
        for v in vencoded:
            f.write(v)
            f.write(b'\x00')

if __name__ == '__main__':
    po_file = 'locale/fil/LC_MESSAGES/django.po'
    mo_file = 'locale/fil/LC_MESSAGES/django.mo'
    
    if os.path.exists(po_file):
        compile_po_to_mo(po_file, mo_file)
        print(f"Compiled {po_file} to {mo_file}")
    else:
        print(f"PO file not found: {po_file}")
