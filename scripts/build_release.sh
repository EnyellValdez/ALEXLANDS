#!/bin/bash
# GitHub Actions runs this on a hosted macOS runner; no local Mac is required.
# It can also run manually on macOS with Xcode: bash scripts/build_release.sh
set -euo pipefail

project_root="$(cd "$(dirname "$0")/.." && pwd)"
output_root="$project_root/build"
mkdir -p "$output_root"
build_root="$(mktemp -d "$output_root/release.XXXXXX")"

xcodebuild \
  -project "$project_root/ALEXLANDS.xcodeproj" \
  -target "ALEXLANDS" \
  -configuration Release \
  -arch arm64 \
  -sdk iphoneos \
  CONFIGURATION_BUILD_DIR="$build_root/products" \
  OBJROOT="$build_root/objects" \
  SYMROOT="$build_root/symbols" \
  CODE_SIGNING_ALLOWED=NO \
  CODE_SIGNING_REQUIRED=NO \
  DEPLOYMENT_POSTPROCESSING=YES \
  build

app_path="$build_root/products/ALEXLANDS.app"
plist_path="$app_path/Info.plist"
display_name="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleDisplayName' "$plist_path")"
bundle_name="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleName' "$plist_path")"
version="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$plist_path")"
build_number="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' "$plist_path")"
executable="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$plist_path")"

if [[ "$display_name" != "ALEXLANDS" || "$bundle_name" != "ALEXLANDS" ]]; then
  echo "Error: el producto compilado no tiene el nombre ALEXLANDS." >&2
  exit 1
fi
if [[ ! -f "$app_path/es.lproj/Localizable.strings" ]]; then
  echo "Error: falta el idioma español en el producto compilado." >&2
  exit 1
fi
if [[ ! -s "$app_path/$executable" ]]; then
  echo "Error: falta el ejecutable de la aplicación." >&2
  exit 1
fi

mkdir -p "$build_root/Payload"
/usr/bin/ditto "$app_path" "$build_root/Payload/ALEXLANDS.app"
ipa_path="$build_root/ALEXLANDS-${version}-${build_number}-unsigned.ipa"
/usr/bin/ditto -c -k --keepParent "$build_root/Payload" "$ipa_path"

echo "IPA sin firmar: $ipa_path"
echo "Nombre: $display_name | Versión: $version | Compilación: $build_number"
echo "Tamaño de la app extraída:"
/usr/bin/du -sh "$app_path"
echo "Tamaño del IPA:"
/usr/bin/du -h "$ipa_path"

# Supply the exact result to Actions instead of uploading every previous build.
if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  printf 'ipa_path=%s\nversion=%s\nbuild_number=%s\n' \
    "$ipa_path" "$version" "$build_number" >> "$GITHUB_OUTPUT"
fi

if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
  app_bytes="$(python3 -c 'import pathlib, sys; print(sum(p.stat().st_size for p in pathlib.Path(sys.argv[1]).rglob("*") if p.is_file() and not p.is_symlink()))' "$app_path")"
  ipa_bytes="$(/usr/bin/stat -f '%z' "$ipa_path")"
  {
    printf '## ALEXLANDS %s — compilación %s\n\n' "$version" "$build_number"
    printf '| Resultado | Valor |\n| --- | --- |\n'
    printf '| Nombre de la app | %s |\n' "$display_name"
    printf '| Español | Incluido |\n'
    printf '| App extraída (suma de archivos) | %s bytes |\n' "$app_bytes"
    printf '| IPA comprimido | %s bytes |\n\n' "$ipa_bytes"
    printf 'Descarga el artefacto **ALEXLANDS-%s-%s**, extrae el ZIP y firma el archivo `.ipa` con GBox.\n' "$version" "$build_number"
  } >> "$GITHUB_STEP_SUMMARY"
fi
