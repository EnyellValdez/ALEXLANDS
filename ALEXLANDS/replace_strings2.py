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
    replace_in_file(filepath, ".3105", ".enyellts")

# 2. project.pbxproj replacement
pbxproj_path = "c:/Users/Enyell/Downloads/ALESSITO_IOS/source/ALEXLANDS.xcodeproj/project.pbxproj"
replace_in_file(pbxproj_path, "PRODUCT_NAME = 3105;", 'PRODUCT_NAME = "ALEXLANDS";')

# 3. SettingsView credits remove? The user said credits should be in settings, meaning they should NOT be on Home. We'll fix ContentView.swift to separate Home and Settings.
print("Done")
