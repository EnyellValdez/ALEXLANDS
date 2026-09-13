import sys
import re

pbxproj_path = r'c:\Users\Enyell\Downloads\ALESSITO_IOS\source\ALEXLANDS.xcodeproj\project.pbxproj'
with open(pbxproj_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if already added
if 'path = es.lproj/Localizable.strings' in content:
    sys.exit(0)

new_file_ref_id = '3105A1FA' # Make up a new ID
new_file_ref = f'\t\t{new_file_ref_id} /* es */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.strings; name = es; path = es.lproj/Localizable.strings; sourceTree = "<group>"; }};\n'

content = content.replace('/* End PBXFileReference section */', new_file_ref + '/* End PBXFileReference section */')

variant_group_pattern = r'(3105A1F3 /\* Localizable.strings \*/ = \{isa = PBXVariantGroup; children = \(\s*[A-F0-9]+ /\* [a-zA-Z\-]+ \*/,)'
variant_group_replacement = r'\g<1>\n\t\t\t\t' + new_file_ref_id + r' /* es */,'
content = re.sub(variant_group_pattern, variant_group_replacement, content)

with open(pbxproj_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("pbxproj updated with es.lproj")
