# ALEXLANDS 3.0 — compilación 9

## Identidad, español y parches

- Producto, target, nombre visible y nombre interno: **ALEXLANDS**. Xcode deja de generar un producto llamado `3105.app`.
- Versión **3.0** y compilación **9**, con una sola fuente en los ajustes de compilación. `Info.plist` utiliza estos valores.
- Identificador de compilación unificado con el que ya tenía el plist de esta copia: `com.enyell.ts.app2`. No se cambió la lógica nativa de acceso; su funcionamiento debe verificarse en el dispositivo firmado.
- Español incorporado al grupo de recursos Xcode y predeterminado para nuevas preferencias. Se conserva la elección de idioma existente.
- Traducidas las 653 claves originales y añadidas 6 claves para Inicio, compilación y textos que antes estaban escritos directamente en las vistas. Las cuatro localizaciones tienen 659 claves y los mismos marcadores de formato.
- Textos visibles, registros y enlace público de atribución identifican la app como ALEXLANDS. Los avisos de autoría original permanecen en la documentación de terceros.
- Paquetes nuevos con extensión **`.enyellts`** y esquema **`enyellts://import`**. Continúa la lectura de `.3105` y enlaces antiguos.
- Los paquetes antiguos se exportan mediante una copia temporal `.enyellts` con los mismos bytes. No se renombra la biblioteca existente ni se cambia su cifrado, contraseña, identidad o llavero.

## Tamaño y trabajo innecesario

| Recurso empaquetado | Antes | Después | Ahorro |
| --- | ---: | ---: | ---: |
| Fondo | 2.826.824 bytes | 1.716.571 bytes | 1.110.253 bytes |
| Icono | 1.179.037 bytes | 1.111.084 bytes | 67.953 bytes |
| Total | 4.005.861 bytes | 2.827.655 bytes | **1.178.206 bytes (29,4 %)** |

La recompresión PNG conserva píxeles, dimensiones y metadatos de color relevantes. Este ahorro corresponde a los archivos fuente de imágenes; Xcode vuelve a procesar los recursos y puede producir una reducción distinta en el `.app`. No se afirma que el IPA final pese una cantidad concreta.

Se excluyen del target los cinco archivos del catálogo que ya estaba oculto: `PackageRepositoryModels.swift`, `PackageRepositoryStore.swift`, `RepositoryMarketplaceView.swift`, `RepositorySourcesView.swift` y `RepositoryPresentationSupport.swift`. Sus fuentes permanecen disponibles para consulta. Se retiran de Inicio las tarjetas y pantallas de catálogo anteriores, y se mueve la barra de utilidades compartida a `DesignSystem.swift`.

La app conserva Inicio, Parches y Archivos, además de importación directa, limpieza y fondos. Ya no crea el store de repositorios ni consulta al arrancar las actualizaciones del proyecto original. No se identificó un SDK de publicidad: la retirada corresponde al catálogo y sus pantallas ocultas.

Los registros se publican en lotes cada 100 ms y se limitan a 500 entradas de hasta 4.096 caracteres, para acotar memoria y actualizaciones de interfaz. La versión Release habilita optimización Swift por tamaño, eliminación de código sin uso y eliminación de símbolos no globales. Estos cambios reducen trabajo; la mejora de tiempo real necesita medición en el dispositivo.

Referencia de configuración: [ajustes de compilación de Apple](https://developer.apple.com/documentation/xcode/build-settings-reference).

## Generar el nuevo IPA con GitHub Desktop y Actions

Los cambios están en el código fuente. Firmar de nuevo el IPA anterior no incorpora estos cambios.

No necesitas un Mac propio. GitHub Actions compila en un servidor macOS con Xcode.

1. En **GitHub Desktop**, abre este repositorio, incluye todos los cambios de la app, `.github/workflows/build.yml` y `scripts/build_release.sh`, y crea el commit.
2. Pulsa **Push origin**. El flujo se inicia automáticamente al subir cambios a `main` o `master`.
3. En el repositorio de GitHub, abre **Actions → Compilar ALEXLANDS** y entra en la ejecución más reciente.
4. Cuando termine correctamente, en **Artifacts** descarga **ALEXLANDS-3.0-9**.
5. Extrae el ZIP descargado. Dentro estará `ALEXLANDS-3.0-9-unsigned.ipa`; ese archivo se firma con **GBox**.

También puedes iniciarlo desde **Actions → Compilar ALEXLANDS → Run workflow** una vez que el flujo esté disponible en la rama predeterminada. La descarga de artefactos es el mecanismo de entrega de archivos de [GitHub Actions](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts).

El resumen de la ejecución mostrará el nombre, la versión, la compilación, la inclusión del español y los tamaños medidos de la app y del IPA. Si la compilación falla, se conserva su registro como artefacto cuando esté disponible. Los IPA se guardan 14 días y los registros de error 7 días.

Actions ejecuta automáticamente:

```bash
bash scripts/build_release.sh
```

El script compila Release para dispositivos arm64 sin firma, comprueba ambos nombres, el español y la existencia del ejecutable, y genera un IPA nuevo dentro de `build/release.XXXXXX/` en el servidor. Actions publica solo el IPA de esa ejecución, sin incluir las fuentes ni los archivos intermedios. No requiere cargar un certificado en GitHub porque la firma se hace posteriormente en GBox.

## Verificación y límites

Se comprobaron estructura XML del plist, claves y marcadores de traducción, pertenencia de recursos, referencias de fuentes compiladas y conservación de los píxeles de las imágenes. Se revisó que la firma del formato de parches, datos autenticados y almacenamiento de claves mantengan compatibilidad con la versión anterior.

Esta copia se editó en Windows. Se verificaron localmente la configuración de Actions y la sintaxis del script; todavía no se ha ejecutado la compilación en GitHub ni medido el IPA final, el arranque o GBox. Antes de distribuir: completar la ejecución de Actions, comprobar nombre e idioma en la app firmada y probar importación/exportación de ambos formatos, contraseña correcta/incorrecta, aplicación/restauración, limpieza y fondos en un dispositivo de prueba.

El archivo `.github/workflows/build.yml`, que estaba eliminado en la copia inicial, se restauró y adaptó a ALEXLANDS. Se retiró `/.github/` de `.gitignore` para permitir subir futuras modificaciones del flujo desde GitHub Desktop.
