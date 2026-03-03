#!/usr/bin/env python3
"""
Quote YAML description fields that contain colons.
YAML treats 'key: value' colons as mapping separators in unquoted strings.
"""
import re
import os
import glob

ARTICLES_DIR = "/home/delmar/.openclaw/agents/jenn/workspace/projects/altclaw/bughuntertools.com/src/articles"

files = glob.glob(os.path.join(ARTICLES_DIR, "*.njk"))
files = [f for f in files if not f.endswith(".backup")]

fixed = 0
for filepath in sorted(files):
    with open(filepath, 'r') as f:
        content = f.read()

    def fix_desc(m):
        prefix = m.group(1)
        value = m.group(2).strip()
        # If it already has quotes, leave it alone
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return m.group(0)
        # If it contains a colon, it needs quoting
        if ':' in value:
            # Use double quotes (escape any existing double quotes)
            escaped = value.replace('"', '\\"')
            return f'{prefix}"{escaped}"'
        return m.group(0)

    new_content = re.sub(
        r'^(description:\s*)(.+)$',
        fix_desc,
        content,
        count=1,
        flags=re.MULTILINE
    )

    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        name = os.path.basename(filepath)
        desc_line = re.search(r'^description:.+$', new_content, re.MULTILINE)
        print(f"  🔧 Quoted: {name}")
        fixed += 1

print(f"\nFixed {fixed} files with colon-containing descriptions")
