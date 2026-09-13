import os

def replace_in_file(filepath, old_str, new_str):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if old_str in content:
        content = content.replace(old_str, new_str)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Replaced in {filepath}")

base_dir = "c:/Users/Enyell/Downloads/ALESSITO_IOS/source/ALEXLANDS"

# 1. Localizable.strings replacements
for lang in ['en.lproj', 'vi.lproj', 'zh-Hans.lproj']:
    filepath = os.path.join(base_dir, lang, "Localizable.strings")
    replace_in_file(filepath, ".enyellts", ".ALEXLANDS") # Revert my previous mistake and use .ALEXLANDS

print("Done")
