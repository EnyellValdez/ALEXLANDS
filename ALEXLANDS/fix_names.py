import re, os

base = r"c:\Users\Enyell\Downloads\ALESSITO_IOS\source\ALEXLANDS"

replacements = [
    ("ALEXLANDS", "ALEXLANDS"),
    ("ENYELL TOOLS", "ALEXLANDS"),
]

swift_files = []
for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith('.swift') or f.endswith('.strings') or f.endswith('.plist'):
            swift_files.append(os.path.join(root, f))

changed = []
for filepath in swift_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = content
        for old, new in replacements:
            new_content = new_content.replace(old, new)
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            changed.append(filepath)
            print(f"CHANGED: {filepath}")
    except Exception as e:
        print(f"ERROR {filepath}: {e}")

print(f"\nTotal changed: {len(changed)}")
