import os
import re

file_path = r"c:\Users\Enyell\Downloads\ALESSITO_IOS\source\ALEXLANDS\es.lproj\Localizable.strings"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

translations = {
    "Close": "Cerrar",
    "Done": "Hecho",
    "OK": "Aceptar",
    "Cancel": "Cancelar",
    "Delete": "Eliminar",
    "Clear search": "Limpiar búsqueda",
    "Failed": "Falló",
    "Version %@": "Versión %@",
    "Device": "Dispositivo",
    "Reboot": "Reiniciar",
    "Next": "Siguiente",
    "Back": "Atrás",
    "Finish": "Finalizar",
    "Settings": "Ajustes",
    "Language": "Idioma",
    "Versin de iOS": "Versión de iOS",
    "Exploit Status": "Estado de Exploit",
    "Support": "Soporte",
    "Unsupported": "No compatible",
    "Supported": "Compatible",
    "Compatibility": "Compatibilidad",
    "Current version": "Versión actual",
    "Verified versions": "Versiones verificadas",
    "Credits": "Créditos",
    "Social media": "Redes sociales",
    "Developer Mode": "Modo Desarrollador",
    "Features": "Funciones",
    "Cleaner": "Limpiador",
    "Wallpapers": "Fondos de pantalla",
    "Reset Collections": "Restablecer colecciones",
    "Hardware model": "Modelo de hardware",
    "For You": "Para ti",
    "More Packages": "Más paquetes",
    "Welcome to ALEXLANDS": "Bienvenido a ALEXLANDS",
    "Developed by Enyell": "Desarrollado por Enyell",
    "Open settings": "Abrir ajustes",
    "Files": "Archivos",
    "Home": "Inicio",
    "New": "Nuevo",
    "Search": "Buscar",
    "Installed": "Instalados",
    "tab.home": "Inicio",
    "tab.new": "Nuevo",
    "tab.sources": "Fuentes",
    "tab.installed": "Parches",
    "tab.files": "Archivos",
    "tab.search": "Buscar"
}

# The strings file is in the format: "key" = "value";
# We want to replace the value part.

for eng, esp in translations.items():
    # We look for lines ending in = "EnglishText";
    # Need to be careful with escaping quotes inside strings, but our keys are simple.
    pattern = r'(\s*=\s*")' + re.escape(eng) + r'(";)'
    replacement = r'\g<1>' + esp + r'\g<2>'
    content = re.sub(pattern, replacement, content)

# A few specific keys that didn't have their English string matching exactly or we just want to force:
content = re.sub(r'("tab\.home"\s*=\s*").*?(")', r'\g<1>Inicio\g<2>', content)
content = re.sub(r'("tab\.files"\s*=\s*").*?(")', r'\g<1>Archivos\g<2>', content)
content = re.sub(r'("tab\.installed"\s*=\s*").*?(")', r'\g<1>Parches\g<2>', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Translations applied!")
