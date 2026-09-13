import os
import re

base_dir = r"c:\Users\Enyell\Downloads\ALESSITO_IOS\source\ALEXLANDS"

# 1. Update RepositoryHomeView.swift
home_view_path = os.path.join(base_dir, "views", "RepositoryHomeView.swift")
with open(home_view_path, 'r', encoding='utf-8') as f:
    home_content = f.read()

# Replace the body of RepositoryHomeView to be completely empty of packages and just have the background
new_home_body = """    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    Spacer().frame(height: 100)
                    AppLogo()
                    Text("Bienvenido a ALEXLANDS")
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundStyle(.white)
                    Text("El sistema en línea está activo.")
                        .font(.subheadline)
                        .foregroundStyle(.white.opacity(0.8))
                }
                .frame(maxWidth: .infinity)
            }
            .scrollContentBackground(.hidden)
            .background(
                Image("AppBackground")
                    .resizable()
                    .scaledToFill()
                    .ignoresSafeArea()
            )
            .navigationTitle("ALEXLANDS")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                AppUtilityToolbar(
                    language: language,
                    onOpenSettings: onOpenSettings,
                    onOpenLogs: onOpenLogs
                )
            }
        }
    }"""

# Use regex to replace the old `var body: some View { ... }` (up to `private var emptyContent`)
home_content = re.sub(r'var body: some View \{.*?\n    \}\n\n    private var emptyContent:', new_home_body + '\n\n    private var emptyContent:', home_content, flags=re.DOTALL)
with open(home_view_path, 'w', encoding='utf-8') as f:
    f.write(home_content)


# 2. Update PatchProjectsView.swift (add background to List)
patch_view_path = os.path.join(base_dir, "views", "PatchProjectsView.swift")
with open(patch_view_path, 'r', encoding='utf-8') as f:
    patch_content = f.read()

patch_replacement = """                List {
                    if !hasLocalContent && (store.isBusy || isImportingWallpapers) {"""
new_patch_replacement = """                List {
                    if !hasLocalContent && (store.isBusy || isImportingWallpapers) {"""
if ".scrollContentBackground(.hidden)" not in patch_content:
    patch_content = patch_content.replace(
        "                .listStyle(.insetGrouped)",
        "                .listStyle(.insetGrouped)\n                .scrollContentBackground(.hidden)\n                .background(\n                    Image(\"AppBackground\")\n                        .resizable()\n                        .scaledToFill()\n                        .ignoresSafeArea()\n                )"
    )
with open(patch_view_path, 'w', encoding='utf-8') as f:
    f.write(patch_content)


# 3. Update AppDataBrowserView.swift (Files tab)
files_view_path = os.path.join(base_dir, "views", "AppDataBrowserView.swift")
with open(files_view_path, 'r', encoding='utf-8') as f:
    files_content = f.read()

if ".scrollContentBackground(.hidden)" not in files_content:
    files_content = files_content.replace(
        "                .listStyle(.insetGrouped)",
        "                .listStyle(.insetGrouped)\n                .scrollContentBackground(.hidden)\n                .background(\n                    Image(\"AppBackground\")\n                        .resizable()\n                        .scaledToFill()\n                        .ignoresSafeArea()\n                )"
    )
with open(files_view_path, 'w', encoding='utf-8') as f:
    f.write(files_content)

print("Backgrounds fixed!")
