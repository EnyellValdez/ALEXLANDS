# ALEXLANDS — mapa del proyecto y guía para hacer cambios

Fecha: 13 de septiembre de 2026. Análisis de la copia local `ALEXLANDS source`.

> Esta es la fotografía anterior a los cambios de la compilación 9. Consulta [los cambios de ALEXLANDS](docs/CAMBIOS_ENYELL_TS.md) para la configuración, localización y módulos que ahora se compilan.

## 1. Qué contiene esta app

Es una aplicación nativa de iPhone y iPad, derivada de **3105**, con interfaz **SwiftUI**, integración con UIKit y componentes en Swift, Objective-C y C. Permite explorar contenedores de aplicaciones, gestionar archivos, crear/importar/aplicar/restaurar parches, consultar repositorios, limpiar cachés y gestionar paquetes de fondos de pantalla.

La interfaz actual está personalizada como **ALEXLANDS**, con acento cian, fondo de imagen y una portada de bienvenida. Hay funciones implementadas que están ocultas en la navegación actual.

Se inventariaron **114 archivos existentes**, sin contar los archivos internos de `.git` ni este informe. Hay **54 Swift, 10 Objective-C `.m`, 2 C y 14 cabeceras**, que suman **24.975 líneas**; además, 6 scripts Python, 4 traducciones, 3 JSON de recursos, 8 imágenes, 8 documentos Markdown, 1 plist, 1 proyecto Xcode y 3 archivos sin extensión convencional.

**Alcance:** revisión estática de estructura, declaraciones, configuración y flujos principales, con un inventario individual de todos los archivos. No equivale a una auditoría exhaustiva de cada ruta de ejecución. No se compiló ni ejecutó la app: este entorno es Windows y no dispone del entorno iOS de Xcode. Los rangos de compatibilidad citados describen lo que acepta el código local; no son certificaciones de funcionamiento en dispositivos.

## 2. Por dónde empezar según el cambio

Las rutas de esta guía son relativas a la raíz del proyecto. El inventario final incluye enlaces a cada archivo.

| Quiero cambiar… | Archivos principales | Consideración |
| --- | --- | --- |
| Colores, tamaños, bordes y componentes comunes | `ALEXLANDS/views/DesignSystem.swift` | El acento está en `AppTheme.accent`. Algunas vistas mantienen estilos propios. |
| Fondo de pantalla de la interfaz | `ALEXLANDS/Assets.xcassets/AppBackground.imageset/FONDO.PNG`, `ContentView.swift` y vistas que usan `Image("AppBackground")` | El archivo de la raíz es una copia; la app consume el catálogo de recursos. |
| Icono de la aplicación | `ALEXLANDS/Assets.xcassets/AppIcon.appiconset/` | El recurso empaquetado es `AppIcon-1024.png`. Cambiar solo `LOGO.PNG` no actualiza el icono. |
| Bienvenida y contenido de Inicio | `ALEXLANDS/views/RepositoryHomeView.swift` | El `body` actual muestra dos textos y el logo, no el catálogo de paquetes. |
| Pestañas visibles y orden | `ALEXLANDS/helpers/AppTabNavigationState.swift`, `ALEXLANDS/ContentView.swift` | Cambiar `FeatureVisibility.isVisible`; revisar también rutas y selección guardada. |
| Idioma español y textos | `ALEXLANDS/es.lproj/Localizable.strings`, `helpers/Localization.swift`, `ALEXLANDS.xcodeproj/project.pbxproj` | Hay un problema de inclusión del español en Xcode, explicado más abajo. |
| Pantalla inicial de configuración | `ALEXLANDS/views/OnboardingView.swift`, `ALEXLANDS/App.swift` | `OnboardingStore` decide cuándo reaparece. |
| Ajustes, enlaces y créditos visibles | `ALEXLANDS/views/SettingsView.swift`, `helpers/DisplayIdentityAttribution.swift` | Existe además un enlace de atribución codificado en `DisplayIdentity.m`. |
| Nombre, versión y número de compilación | `ALEXLANDS/Info.plist`, `ALEXLANDS.xcodeproj/project.pbxproj` | Actualmente contienen valores contradictorios. |
| Servidor de actualizaciones | `ALEXLANDS/helpers/Utils.swift` | `AppUpdateChecker` sigue consultando las releases del proyecto original. |
| Fuentes de paquetes y catálogo | `helpers/PackageRepositoryModels.swift`, `helpers/PackageRepositoryStore.swift` y vistas `Repository*` | El catálogo predeterminado también apunta al proyecto original. |
| Lista de aplicaciones y contenedores | `views/AppDataBrowserView.swift`, `helpers/ContainerStore.swift` | La vista depende de la resolución de nombres y acceso a contenedores. |
| Acciones del explorador de archivos | `views/FileBrowserView.swift`, `helpers/FileManagerService.swift` | Copiar/mover usa también `FileOperationCoordinator`. |
| Crear o editar parches | `views/PatchProjectEditorView.swift`, `helpers/PatchDraftService.swift`, `helpers/PatchWorkspaceService.swift` | Separar edición del proyecto de su aplicación al dispositivo. |
| Importar/exportar y contraseñas | `helpers/PatchPackageCodec.swift`, `PatchProjectStore.swift`, `PatchKeyStore.swift`, `Info.plist` | El formato real sigue siendo `.3105`. |
| Aplicar, restaurar o restablecer un parche | `helpers/DevicePatchService.swift`, `helpers/PatchTransaction.swift` | Conservar diarios, copias y detección de modificaciones posteriores. |
| Limpieza | `views/CleanerView.swift`, `helpers/LimitedCleanerService.swift`, `CleanerCatalog.swift` | El alcance implementado se limita a `Library/Caches` y `tmp`. |
| Fondos `.tendies` | `views/WallpaperLabView.swift`, `helpers/WallpaperLabService.swift`, `WallpaperInstaller.swift` | No confundir estos fondos del sistema con el fondo visual de ALEXLANDS. |
| Compatibilidad por versión de iOS | `helpers/SupportPolicy.swift`, `helpers/KernelExploit.swift` | Cambiar una lista de versiones no demuestra que el acceso nativo funcione. |

## 3. Arquitectura y recorrido de los datos

```text
App.swift
  ├─ AppState: soporte y estado de acceso al dispositivo
  ├─ OnboardingView / OnboardingStore: configuración inicial
  ├─ PatchDraftCoordinator: borradores e importación por URL
  ├─ FileOperationCoordinator: selección para copiar/mover
  ├─ PatchProjectStore: estado observable de la biblioteca
  ├─ PackageRepositoryStore: fuentes, catálogo y descargas
  └─ ContentView
       ├─ Inicio → RepositoryHomeView
       ├─ Parches/Instalados → PatchProjectsView
       ├─ Archivos → AppDataBrowserView → FileBrowserView
       ├─ Nuevos → RepositoryNewView [oculta]
       ├─ Fuentes → RepositorySourcesView [oculta]
       └─ Buscar → RepositorySearchView [oculta]

Vistas → coordinadores/stores → servicios y validadores → archivos / red / puentes nativos
```

### Arranque y navegación

`ALEXLANDSApp` crea cinco objetos compartidos e inyecta idioma y configuración regional. Fuerza el modo oscuro. Presenta onboarding cuando corresponde; al terminar o al volver a primer plano se comprueba el soporte. El inicio normal puede lanzar automáticamente el componente de acceso nativo. Las URL entrantes pasan al coordinador de importación y seleccionan Instalados.

`ContentView` utiliza `TabView` en ancho compacto y `NavigationSplitView` en ancho regular. Hay seis secciones declaradas, pero `FeatureVisibility.isVisible` permite únicamente **Inicio, Instalados/Parches y Archivos**. El valor de modo desarrollador se guarda, pero no modifica esa decisión en la implementación actual.

### Archivos y contenedores

`AppDataBrowserView` presenta aplicaciones. `ContainerStore` combina descubrimiento por APIs, metadatos y exploración del sistema de archivos; `ContainerBrowserLogic` combina resultados y aplica políticas de identidad y presentación. `FileBrowserView` ofrece navegación, búsqueda, selección múltiple, previsualización, importación y operaciones. `FileManagerService` ejecuta operaciones y resuelve conflictos; los ZIP tienen implementaciones propias.

### Parches

```text
Archivo/carpeta elegida → PatchDraftService → editor → PatchProjectStore
  → PatchPackageCodec → PatchProjectLibrary
  ↔ PatchWorkspaceService → Documents/Patches

Aplicar → sincronizar workspace → DevicePatchService → PatchTransaction
  → resolver contenedores → respaldar originales → escribir → registrar resultado

Restaurar → inspeccionar cambios posteriores → recuperar originales
  → retirar archivos nuevos y directorios creados cuando corresponda
```

Los destinos se expresan mediante identificadores de aplicaciones y rutas relativas. El formato de paquete tiene firma `3105PATCH`, esquema actual **3** y lectura de esquemas anteriores. Emplea AES-GCM, SHA-256 y derivación PBKDF2 para contraseñas. `PatchKeyStore` usa Keychain. Los parches privados tienen reglas adicionales para inspección y materialización del workspace. Un paquete sin contraseña contiene su clave pública de contenido en el sobre; no debe interpretarse como contenido secreto.

### Repositorios

Los modelos describen manifiestos JSON con paquetes, versiones, autor, imágenes, descargas y rangos de sistema. Hay validación de URL HTTPS, límites de manifiesto y comprobación de integridad. El store persiste fuentes, actualiza catálogos y descarga paquetes, que después ingresan a la biblioteca de parches o fondos. La interfaz visible actual deja fuera las pestañas dedicadas a estas funciones.

### Limpieza y fondos

La limpieza mide y elimina contenido desechable de cada contenedor admitido. Los fondos `.tendies` pasan por preparación, extracción ZIP, validación de estructura, instalación y registro de recibos. `WallpaperInstaller` implementa restauración y restablecimiento de descriptores. `PatchProjectsView` integra contenido instalado de ambos tipos y presenta el limpiador como hoja; no todas las vistas existentes son pestañas independientes.

## 4. Hallazgos que conviene resolver antes de ampliar la app

Estos puntos distinguen hechos observados de consecuencias que requieren comprobación al compilar o ejecutar.

### 4.1 Español registrado pero fuera del grupo de recursos — confirmado

En `Localization.swift` existe `case spanish = "es"`. En `project.pbxproj` existe la referencia `3105A1FA` al archivo español, pero el grupo `Localizable.strings` (`3105A120`) solo incluye `en`, `vi` y `zh-Hans`. Por tanto, esa referencia suelta no incorpora el español a la variante que se empaqueta. Revisar la pertenencia de la localización en Xcode y comprobar el producto generado.

Además, cada idioma contiene **653 claves únicas**, sin duplicadas y con las mismas claves. **602 valores del español son idénticos al inglés**. Algunos nombres y símbolos pueden coincidir legítimamente; aun así, aparecen mensajes completos en inglés, por ejemplo `update.title`, `patch.error.wrong_password` y numerosos textos de onboarding. La traducción es parcial. Los marcadores `%@`, `%lld`, etc. deben conservarse al traducir.

### 4.2 Identidad y versión de compilación contradictorias — confirmado

| Propiedad | Info.plist | Configuración Debug y Release |
| --- | --- | --- |
| Identificador | `com.enyell.ts.app2` | `com.apple.mobile.MobileHouseArrest` |
| Nombre visible | `ALEXLANDS` | `INFOPLIST_KEY_CFBundleDisplayName = 3105` |
| Versión | `3.0` | `MARKETING_VERSION = 3.0` |
| Compilación | `7` | `CURRENT_PROJECT_VERSION = 8` |

El proyecto utiliza un plist de entrada junto con generación habilitada. Se deben unificar las fuentes y examinar el `Info.plist` del `.app` resultante para saber exactamente qué se entrega. El README original relaciona el identificador MobileHouseArrest con el acceso MHA; no conviene tratarlo como un cambio puramente cosmético.

### 4.3 Los textos de extensión no coinciden con el formato — confirmado

Varias traducciones muestran **`.ALEXLANDS`**, mientras que `Info.plist`, el almacenamiento de `PatchProjectLibrary`, el importador y el formato siguen usando **`.3105`**. Esto puede inducir al usuario a renombrar paquetes incorrectamente. Si solo se cambia la marca visible, mantener el formato técnico coherente. Si se decide un formato nuevo, preparar compatibilidad con paquetes antiguos y actualizar todas las rutas de importación/exportación, no solo los textos.

### 4.4 Actualizaciones y catálogo aún pertenecen al proyecto original — confirmado

`AppUpdateChecker` en `Utils.swift` consulta `api.github.com/repos/YangJiiii/3105/releases/latest`. `PackageRepositoryDefaults` apunta a `raw.githubusercontent.com/YangJiiii/3105-repo/main/sources.json`. Son valores leídos del código, sin comprobación remota de disponibilidad. Cambiar enlaces visibles en Ajustes no cambia estos servicios. La numeración local 3.0 también debe ser coherente con las versiones del canal que se elija.

### 4.5 La portada muestra estado fijo — confirmado

`RepositoryHomeView.body` muestra «El sistema en línea está activo.» como un literal, sin ligarlo a conexión, resultado de una petición o estado real de acceso. Si se quiere un indicador funcional, enlazarlo a un estado observado. Los dos textos de bienvenida están escritos directamente en español y no pasan por `language.text`.

La misma vista conserva propiedades de tarjetas y catálogo que su `body` actual no utiliza. `RepositoryMarketplaceView.swift` contiene vistas `Legacy*`, pero también componentes compartidos que siguen referenciados: no se debe eliminar el archivo entero suponiendo que todo quedó obsoleto.

### 4.6 Arranque automático frente a documentación manual — confirmado

El README describe activación manual del componente kernel en iOS 17–18. `AppState.detectSupport()` llama actualmente a `maybeAutoRunKernelExploit()`. La lógica guarda un intento por sesión y evita reintentar tras fallo. Documentación y producto deben acordar qué comportamiento se quiere.

### 4.7 Scripts antiguos apuntan a otra carpeta — confirmado

Los seis `.py` contienen rutas fijas bajo `C:/Users/Enyell/Downloads/ALESSITO_IOS/source`, diferentes de esta copia del Escritorio. Son herramientas de modificación masiva, no componentes que ejecute la app. No se ejecutaron durante este análisis.

`fix_pbx.py` busca un identificador de grupo distinto del actual y termina si encuentra la referencia española, aunque esta no esté conectada al grupo. Eso explica por qué volver a ejecutarlo no garantiza corregir la localización. Los scripts de sustitución de extensiones tampoco migran el formato real.

### 4.8 Créditos y atribución en varias capas — confirmado

Hay créditos en documentación, Ajustes y una hoja accesible mediante pulsación prolongada de **5 segundos** (`DisplayIdentityAttribution.swift`). `DisplayIdentity.m` decodifica una URL de atribución y genera un token derivado del identificador. `Utils.swift` referencia ese token. Los comentarios del archivo no equivalen a una comprobación completa de integridad: el uso observado en Swift incluye calcular y descartar el valor. Para modificar la presentación, revisar las dependencias reales y los avisos de terceros.

`AntiDetection.m` redefine `fork()` para que falle en el propio proceso; su presencia no demuestra invisibilidad frente a otras aplicaciones ni una protección general contra detección.

### 4.9 Compilación mínima no equivale a soporte operativo — confirmado

El objetivo de despliegue es iOS **16.0**, pero `ExploitSupportPolicy` acepta 17.0–17.7.x, 18.0–18.7.1, 26.0–26.6.1 y cuatro builds concretas de 27.0.0. La app puede tener requisitos de instalación distintos de los de acceso al dispositivo. No se verificó aquí el funcionamiento de ninguno de esos rangos.

### 4.10 Estado del repositorio y verificación pendiente

No hay suite de pruebas ni destino de tests en los archivos revisados. `.gitignore` excluye `/Tests/` y `/.github/`. Al iniciar este análisis Git ya mostraba **`.github/workflows/build.yml` eliminado**; el archivo no existe en la copia y su contenido no fue analizado ni recuperado. No se encontró `AGENTS.md` en el árbol del proyecto. El inventario omite `.git`, que contiene metadatos de control de versiones.

## 5. Datos que se guardan y contratos que conviene conservar

| Datos | Ubicación / responsable |
| --- | --- |
| Idioma, onboarding y preferencias | `UserDefaults` / `AppStorage`, en `Localization`, `OnboardingStore`, vistas y navegación. |
| Fuentes e índice de resolución de paquetes | `UserDefaults`: `repository.sources.v1` y `repository.package_resolutions.v1`. |
| Paquetes de parches | Application Support / `PatchProjects`, administrado por `PatchProjectLibrary`. |
| Copias de parches y diarios | `PatchProjects/Backups`, con diarios `journal.plist`. |
| Árbol editable de parches | Documents / `Patches`, administrado por `PatchWorkspaceService`. |
| Marcas de autor y procedencia | Directorios `.AuthorCopies` y `.Origins` de la biblioteca. |
| Claves de paquetes | Keychain, mediante `PatchKeyStore`. |
| Fondos preparados | Application Support / `WallpaperLab/Packages`. |
| Copias y recibos de fondos | Application Support / `WallpaperLab/Backups`; recibos `receipt.plist`. |
| Copias de previsualización | Directorio temporal `3105-Preview`. |
| Logs de sesión | `AppLog.shared.entries`, en memoria; captura de stdout/stderr hacia la interfaz. |

Conservar o migrar explícitamente: extensión `.3105`, esquema `threeoneosfive`, UTI `com.yangjiii.3105.patch-package`, versiones de paquete, claves de preferencias y formatos de recibos. Los cambios de nombre de producto no deben alterar accidentalmente estos contratos.

## 6. Secuencia práctica para modificarla

1. **Estabilizar configuración:** resolver español, nombre/identificador/compilación, textos de extensión y canal de actualización.
2. **Definir la interfaz deseada:** decidir las pestañas visibles, el contenido de Inicio, colores y fondo. Empezar por `DesignSystem`, `RepositoryHomeView` y `FeatureVisibility`.
3. **Editar funciones por módulo:** mantener la lógica de archivos y parches en servicios; evitar incorporarla a una vista de presentación.
4. **Verificar en Xcode:** compilación Debug y Release, recursos incluidos, plist final y presentación en iPhone/iPad. Al añadir archivos, incorporarlos al proyecto: no usa un grupo de fuentes automáticamente sincronizado.
5. **Verificar cambios funcionales:** importación/exportación, contraseña correcta e incorrecta, selección de archivos, conflictos de nombres, aplicación/restauración y persistencia después de reiniciar.

Para cambios visuales, revisar idiomas, tamaños de texto y contraste sobre el fondo. Para parches, probar restauración tanto de archivos originales como de archivos nuevos y cambios posteriores. Para ZIP, comprobar archivos inválidos, rutas que salgan del destino, enlaces y falta de espacio. Para funcionalidades del dispositivo, una vista en simulador no sustituye una prueba física.

Hay argumentos de simulador como `--simulate-access`, `--simulate-files-tab`, `--simulate-settings`, `--simulate-repository` y otros específicos. La política actual de pestañas puede volver a seleccionar Inicio aunque un argumento pida una sección oculta. No se ejecutaron estas rutas durante la revisión.

## 7. Inventario de todos los archivos

El inventario siguiente es una fotografía de los 114 archivos existentes antes de crear este documento. Cada entrada indica su función y su tamaño; en archivos de código añade símbolos principales para facilitar la búsqueda. Las líneas y símbolos son orientativos para navegar, no una declaración de cobertura de pruebas. En imágenes se verificaron dimensiones y referencias; no se realizó evaluación visual de su contenido.


### Raíz y documentación

#### [.gitattributes](<.gitattributes>)

Reglas de finales de línea y tratamiento de archivos de texto/binarios en Git.

- Tamaño: 186 bytes; 15 líneas.

#### [.gitignore](<.gitignore>)

Exclusiones de compilaciones, firma, archivos locales, Tests y .github; revisar si se incorpora automatización o pruebas.

- Tamaño: 475 bytes; 44 líneas.

#### [CHANGELOG.md](<CHANGELOG.md>)

Historial de cambios de 3105 hasta 1.0.1; no describe toda la personalización actual 3.0.

- Tamaño: 3.130 bytes; 65 líneas.

#### [docs/images/app-icon.png](<docs/images/app-icon.png>)

Icono usado en la documentación; recurso de presentación del repositorio, distinto del icono compilado.

- Tamaño: 192.332 bytes; 512 × 512 px.

#### [docs/images/cleaner.png](<docs/images/cleaner.png>)

Captura documental del limpiador; no es una pantalla ejecutable ni prueba del estado actual de la interfaz.

- Tamaño: 186.136 bytes; 1206 × 2622 px.

#### [docs/images/home.png](<docs/images/home.png>)

Captura documental de Inicio original; no representa necesariamente la portada personalizada actual.

- Tamaño: 246.717 bytes; 1206 × 2622 px.

#### [docs/images/patches.png](<docs/images/patches.png>)

Captura documental de parches de la versión original.

- Tamaño: 163.118 bytes; 1206 × 2622 px.

#### [docs/PATCH_GUIDE.md](<docs/PATCH_GUIDE.md>)

Guía en inglés del workspace, creación, aplicación/restauración, importación/exportación y contraseñas de parches.

- Tamaño: 3.967 bytes; 68 líneas.

#### [docs/PATCH_GUIDE.vi.md](<docs/PATCH_GUIDE.vi.md>)

Versión vietnamita de la guía de workspace y parches.

- Tamaño: 4.773 bytes; 68 líneas.

#### [docs/releases/1.0.1.md](<docs/releases/1.0.1.md>)

Notas de lanzamiento en vietnamita de la versión original 1.0.1.

- Tamaño: 2.211 bytes; 31 líneas.

#### [docs/REPOSITORY_GUIDE.vi.md](<docs/REPOSITORY_GUIDE.vi.md>)

Especificación en vietnamita del catálogo y manifiesto JSON de repositorios, ejemplos y validaciones.

- Tamaño: 7.181 bytes; 160 líneas.

#### [FONDO.PNG](<FONDO.PNG>)

Imagen de fondo; la copia en AppBackground.imageset es la que referencia el catálogo. Ambas tienen los mismos bytes.

- Tamaño: 2.826.824 bytes; 853 × 1844 px.

#### [LICENSE](<LICENSE>)

Texto de la licencia GNU GPL versión 3 incluido en el repositorio.

- Tamaño: 35.149 bytes; 674 líneas.

#### [LOGO.PNG](<LOGO.PNG>)

Imagen de trabajo en la raíz; no es el archivo referenciado por el catálogo AppIcon.

- Tamaño: 2.761.295 bytes; 1254 × 1254 px.

#### [README.md](<README.md>)

Presentación en inglés, instalación, compatibilidad y créditos originales; contiene diferencias con el código actual.

- Tamaño: 7.072 bytes; 117 líneas.

#### [README.vi.md](<README.vi.md>)

Presentación original en vietnamita; también necesita alinearse con ALEXLANDS.

- Tamaño: 5.138 bytes; 77 líneas.

#### [THIRD_PARTY_NOTICES.md](<THIRD_PARTY_NOTICES.md>)

Avisos y atribuciones de componentes externos incorporados o usados como base.

- Tamaño: 1.494 bytes; 15 líneas.

### Proyecto Xcode

#### [ALEXLANDS.xcodeproj/project.pbxproj](<ALEXLANDS.xcodeproj/project.pbxproj>)

Proyecto Xcode: fuentes compiladas, recursos, grupos, target, firma y configuraciones Debug/Release. Contiene las discrepancias de identidad y la referencia española sin conectar.

- Tamaño: 36.675 bytes; 669 líneas.

### Entrada, configuración y scripts

#### [ALEXLANDS/App.swift](<ALEXLANDS/App.swift>)

Entrada @main, creación de estado compartido, onboarding, idioma, modo oscuro, actualizaciones, importación por URL y AppState con activación automática de acceso.

- Tamaño: 7.759 bytes; 205 líneas.
- Símbolos para localizar: `ALEXLANDSApp`, `AppState`.

#### [ALEXLANDS/ContentView.swift](<ALEXLANDS/ContentView.swift>)

Composición de navegación compacta y amplia, selección de secciones, ajustes/logs y presentación global de importaciones y alertas.

- Tamaño: 8.716 bytes; 249 líneas.
- Símbolos para localizar: `ContentView`, `CompactTabLabel`.

#### [ALEXLANDS/fix_backgrounds.py](<ALEXLANDS/fix_backgrounds.py>)

Script antiguo que sustituye el body de Inicio y añade fondos en algunas vistas mediante reemplazos de texto; apunta a otra carpeta.

- Tamaño: 3.839 bytes; 84 líneas.

#### [ALEXLANDS/fix_names.py](<ALEXLANDS/fix_names.py>)

Script antiguo de sustitución global de ALEXLANDS por ALEXLANDS en Swift/strings/plist de otra ubicación.

- Tamaño: 977 bytes; 32 líneas.

#### [ALEXLANDS/fix_pbx.py](<ALEXLANDS/fix_pbx.py>)

Intento de incorporar español al proyecto mediante sustitución de texto; su grupo objetivo no coincide con el actual y su salida temprana deja la referencia sin conectar.

- Tamaño: 1.073 bytes; 24 líneas.

#### [ALEXLANDS/Info.plist](<ALEXLANDS/Info.plist>)

Metadatos de la app, nombre, identificador, versión, tipos de documento, esquema URL, permisos y orientaciones.

- Tamaño: 3.557 bytes; 104 líneas.

#### [ALEXLANDS/replace_strings2.py](<ALEXLANDS/replace_strings2.py>)

Script antiguo que sustituye textos .3105 por .enyellts en tres idiomas y cambia PRODUCT_NAME; no migra el formato de paquetes.

- Tamaño: 1.046 bytes; 24 líneas.

#### [ALEXLANDS/replace_strings3.py](<ALEXLANDS/replace_strings3.py>)

Script antiguo que vuelve a cambiar .enyellts por .ALEXLANDS en textos de tres idiomas; origen de parte de la inconsistencia visible.

- Tamaño: 702 bytes; 19 líneas.

#### [ALEXLANDS/ALEXLANDS-Bridging-Header.h](<ALEXLANDS/ALEXLANDS-Bridging-Header.h>)

Expone a Swift las cabeceras de acceso nativo, contenedores, iconos y atribución. Mantenerlo coherente al mover o retirar componentes.

- Tamaño: 232 bytes; 7 líneas.

#### [ALEXLANDS/translate_es.py](<ALEXLANDS/translate_es.py>)

Script de traducción parcial por sustituciones sobre el archivo español de otra ubicación; no traduce todo el catálogo.

- Tamaño: 2.602 bytes; 77 líneas.

### Interfaz — views

#### [ALEXLANDS/views/AppDataBrowserView.swift](<ALEXLANDS/views/AppDataBrowserView.swift>)

Lista de aplicaciones y contenedores, búsqueda, estados de carga/acceso y entrada al explorador; incluye BrowserAppIcon.

- Tamaño: 17.406 bytes; 440 líneas.
- Símbolos para localizar: `AppDataBrowserView`, `AppBrowserOverlayState`, `BrowserAppIcon`.

#### [ALEXLANDS/views/CleanerView.swift](<ALEXLANDS/views/CleanerView.swift>)

Interfaz de escaneo, ordenación, selección y confirmación para eliminar datos desechables por app.

- Tamaño: 23.625 bytes; 635 líneas.
- Símbolos para localizar: `CleanerView`, `CleanerAppRecord`, `CleanerAlert`.

#### [ALEXLANDS/views/DesignSystem.swift](<ALEXLANDS/views/DesignSystem.swift>)

Tema cian, medidas comunes, borde de tarjetas, iconos de filas, buscador y componente AppLogo.

- Tamaño: 4.006 bytes; 121 líneas.
- Símbolos para localizar: `AppTheme`, `AppCardBorder`, `AppRowIcon`, `AppSearchField`, `AppLogo`.

#### [ALEXLANDS/views/FileBrowserView.swift](<ALEXLANDS/views/FileBrowserView.swift>)

Explorador de archivos: navegación, selección múltiple, importación, copiar/mover/pegar, conflictos, ZIP, borradores y previsualización Quick Look. Incluye el selector de documentos UIKit.

- Tamaño: 68.829 bytes; 1.836 líneas.
- Símbolos para localizar: `FileBrowserView`, `FileBrowserOverlayState`, `FileDocumentPicker`, `FileEntryRow`, `FileReplacementNotice`, `FileNamePromptAction`, `FileNamePrompt`.

#### [ALEXLANDS/views/FilesTabControls.swift](<ALEXLANDS/views/FilesTabControls.swift>)

Botón de barra y tira visual para las pestañas internas del explorador.

- Tamaño: 4.483 bytes; 131 líneas.
- Símbolos para localizar: `FilesTabToolbarButton`, `FilesTabStrip`.

#### [ALEXLANDS/views/FilesTabSwitcherView.swift](<ALEXLANDS/views/FilesTabSwitcherView.swift>)

Selector de sesiones/pestañas internas de Archivos; distinto de las pestañas principales de la app.

- Tamaño: 4.962 bytes; 132 líneas.
- Símbolos para localizar: `FilesTabSwitcherView`.

#### [ALEXLANDS/views/FolderPatchSelectionView.swift](<ALEXLANDS/views/FolderPatchSelectionView.swift>)

Selector de contenido de carpetas para preparar reglas de un parche.

- Tamaño: 6.746 bytes; 171 líneas.
- Símbolos para localizar: `FolderPatchSelectionView`.

#### [ALEXLANDS/views/LogView.swift](<ALEXLANDS/views/LogView.swift>)

Visualización de mensajes de AppLog y controles de la consola de la app.

- Tamaño: 4.983 bytes; 106 líneas.
- Símbolos para localizar: `LogView`.

#### [ALEXLANDS/views/OnboardingView.swift](<ALEXLANDS/views/OnboardingView.swift>)

Asistente inicial y OnboardingStore; decide repetición por versión y huella de la instalación.

- Tamaño: 20.172 bytes; 492 líneas.
- Símbolos para localizar: `OnboardingStep`, `OnboardingNavigationDirection`, `OnboardingView`, `OnboardingStore`.

#### [ALEXLANDS/views/PatchProjectEditorView.swift](<ALEXLANDS/views/PatchProjectEditorView.swift>)

Formulario de edición de proyecto y de reglas de destino; gestiona datos que luego recibe el store.

- Tamaño: 19.640 bytes; 456 líneas.
- Símbolos para localizar: `PatchProjectEditorView`, `PatchRuleEditorContext`, `PatchRuleEditorView`.

#### [ALEXLANDS/views/PatchProjectsView.swift](<ALEXLANDS/views/PatchProjectsView.swift>)

Pantalla de biblioteca e instalación, importación/creación de parches, integración de fondos, detalles y acciones de aplicar/restaurar; presenta también el limpiador.

- Tamaño: 49.249 bytes; 1.222 líneas.
- Símbolos para localizar: `PatchPackagePickerPolicy`, `WallpaperPackagePickerPolicy`, `PatchProjectsView`, `WallpaperImportFeedback`, `PatchProjectRow`, `InstalledContentKind`, `InstalledContentKindBadge`.

#### [ALEXLANDS/views/RepositoryHomeView.swift](<ALEXLANDS/views/RepositoryHomeView.swift>)

Portada actual de bienvenida; también contiene RepositoryNewView, RepositorySearchView y componentes de tarjetas del catálogo. Parte del contenido anterior de Inicio está desconectada del body.

- Tamaño: 21.155 bytes; 577 líneas.
- Símbolos para localizar: `RepositoryHomeView`, `RepositoryNewView`, `RepositorySearchView`, `RepositoryFeaturedCard`, `RepositoryCardButtonStyle`, `RepositoryNewPackageRow`.

#### [ALEXLANDS/views/RepositoryMarketplaceView.swift](<ALEXLANDS/views/RepositoryMarketplaceView.swift>)

Vistas Legacy de exploración/fuentes y componentes compartidos: detalle de paquete, filas, imágenes, alta de fuente, barra de utilidades y presentaciones del store.

- Tamaño: 39.299 bytes; 1.125 líneas.
- Símbolos para localizar: `LegacyRepositoryExploreView`, `LegacyRepositorySourcesView`, `RepositoryPackageDetailView`, `RepositoryPackageRow`, `RepositoryPackageIcon`, `RepositoryRemoteImage`, `RepositoryScreenshotPreview`.

#### [ALEXLANDS/views/RepositorySourcesView.swift](<ALEXLANDS/views/RepositorySourcesView.swift>)

Pantalla de fuentes, estado de actualización, detalle de fuente, etiquetas y listas de paquetes por etiqueta. La sección está oculta por FeatureVisibility.

- Tamaño: 14.309 bytes; 413 líneas.
- Símbolos para localizar: `RepositorySourcesView`, `RepositorySourceRow`, `RepositorySourceStatus`, `RepositorySourceDetailView`, `RepositoryTagRow`, `RepositoryTagPackagesView`.

#### [ALEXLANDS/views/SettingsView.swift](<ALEXLANDS/views/SettingsView.swift>)

Preferencias, idioma, información del dispositivo, funciones, soporte y enlaces/créditos.

- Tamaño: 10.687 bytes; 239 líneas.
- Símbolos para localizar: `SettingsView`.

#### [ALEXLANDS/views/WallpaperLabView.swift](<ALEXLANDS/views/WallpaperLabView.swift>)

Biblioteca, detalles, instalación y restablecimiento de paquetes de fondo; incluye vistas reutilizadas para contenido instalado y ajustes.

- Tamaño: 33.487 bytes; 875 líneas.
- Símbolos para localizar: `WallpaperPickerPolicy`, `WallpaperLabView`, `WallpaperPackageDetailView`, `InstalledWallpaperPackageDetailView`, `InstalledWallpaperAlert`, `WallpaperResetSettingsView`, `WallpaperResetAlert`.

### Lógica y servicios — helpers

#### [ALEXLANDS/helpers/AntiDetection.m](<ALEXLANDS/helpers/AntiDetection.m>)

Redefine fork para fallar con EAGAIN dentro del propio proceso; no equivale a evitar detección en todo el dispositivo.

- Tamaño: 523 bytes; 20 líneas.

#### [ALEXLANDS/helpers/AppIconHelper.h](<ALEXLANDS/helpers/AppIconHelper.h>)

Declaraciones Objective-C para iconos e información de aplicaciones disponibles a Swift.

- Tamaño: 780 bytes; 20 líneas.

#### [ALEXLANDS/helpers/AppIconHelper.m](<ALEXLANDS/helpers/AppIconHelper.m>)

Obtención de iconos, nombres, metadatos y aplicaciones mediante APIs dinámicas; adapta variantes de iconos y resultados.

- Tamaño: 15.045 bytes; 355 líneas.

#### [ALEXLANDS/helpers/AppTabNavigationState.swift](<ALEXLANDS/helpers/AppTabNavigationState.swift>)

Secciones, visibilidad de funciones, selección y sesiones independientes de navegación de archivos. Solo Inicio, Instalados y Archivos son visibles actualmente.

- Tamaño: 5.119 bytes; 183 líneas.
- Símbolos para localizar: `AppSection`, `WallpaperFeatureSupportPolicy`, `OneShotPresentationGate`, `FeatureVisibility`, `AppTabNavigationState`, `FileBrowserDestination`, `FilesTabState`.

#### [ALEXLANDS/helpers/CleanerCatalog.swift](<ALEXLANDS/helpers/CleanerCatalog.swift>)

Modelos auxiliares, orden de limpieza, selección de resultados visibles y combinación de aplicaciones que se escanean.

- Tamaño: 2.894 bytes; 89 líneas.
- Símbolos para localizar: `CleanerResolvedApplication`, `CleanerCatalogRecord`, `CleanerSortOrder`, `CleanerCatalog`.

#### [ALEXLANDS/helpers/ContainerBrowserLogic.swift](<ALEXLANDS/helpers/ContainerBrowserLogic.swift>)

Políticas puras de rutas, mezcla de descubrimientos, candidatos a bundle ID, extracción de identificadores y nombres de presentación.

- Tamaño: 10.288 bytes; 302 líneas.
- Símbolos para localizar: `ContainerDiscoveryMerger`, `ContainerAccessPolicy`, `ContainerBundleCandidateResolver`, `LaunchServicesCandidateExtractor`, `MHAIdentifierCatalog`, `AppDataCatalogMerger`, `ContainerPresentationPolicy`.

#### [ALEXLANDS/helpers/ContainerIdentityResolver.swift](<ALEXLANDS/helpers/ContainerIdentityResolver.swift>)

Resuelve identidad desde metadatos y acceso temporal, con resultados explícitos para errores y nombre de reserva.

- Tamaño: 1.974 bytes; 60 líneas.
- Símbolos para localizar: `ContainerMetadata`, `ContainerResolution`, `ContainerIdentityResolver`.

#### [ALEXLANDS/helpers/ContainerStore.swift](<ALEXLANDS/helpers/ContainerStore.swift>)

Modelos InstalledApp/FileEntry; descubre apps y contenedores, resuelve rutas e identidades, solicita acceso y lista/lee archivos.

- Tamaño: 32.314 bytes; 758 líneas.
- Símbolos para localizar: `InstalledApp`, `FileEntry`, `ContainerStore`.

#### [ALEXLANDS/helpers/DevicePatchService.swift](<ALEXLANDS/helpers/DevicePatchService.swift>)

Adaptador del dispositivo para aplicar/restaurar/restablecer parches; conecta resolución de contenedores y transacciones.

- Tamaño: 3.769 bytes; 97 líneas.
- Símbolos para localizar: `DevicePatchService`.

#### [ALEXLANDS/helpers/DisplayIdentity.h](<ALEXLANDS/helpers/DisplayIdentity.h>)

Interfaz de la URL de atribución y del token de identidad que usa Swift.

- Tamaño: 292 bytes; 6 líneas.

#### [ALEXLANDS/helpers/DisplayIdentity.m](<ALEXLANDS/helpers/DisplayIdentity.m>)

Decodifica una URL de atribución y calcula un token SHA-256 derivado; está referenciado por Utils y la interfaz de atribución.

- Tamaño: 2.128 bytes; 47 líneas.

#### [ALEXLANDS/helpers/DisplayIdentityAttribution.swift](<ALEXLANDS/helpers/DisplayIdentityAttribution.swift>)

Reconocedor de pulsación prolongada a nivel de ventana, integración SwiftUI y hoja de atribución con enlace y compartir.

- Tamaño: 7.235 bytes; 169 líneas.
- Símbolos para localizar: `WindowLongPressView`, `DisplayIdentityAttributionModifier`, `DisplayAttributionSheet`.

#### [ALEXLANDS/helpers/FileBrowserMetadata.swift](<ALEXLANDS/helpers/FileBrowserMetadata.swift>)

Opciones y política de ordenación de archivos; escaneo de tamaños y cantidad de elementos de directorios.

- Tamaño: 5.168 bytes; 147 líneas.
- Símbolos para localizar: `FileBrowserSortOrder`, `FileBrowserSortPolicy`, `FileBrowserDirectorySummary`, `FileBrowserMetadataScanner`.

#### [ALEXLANDS/helpers/FileManagerService.swift](<ALEXLANDS/helpers/FileManagerService.swift>)

Operaciones de archivos, sesiones de importación, políticas de conflicto, copiar/mover, creación, borrado, archivado y extracción.

- Tamaño: 26.828 bytes; 763 líneas.
- Símbolos para localizar: `FileManagerOperationError`, `FileTransferMode`, `FileConflictPolicy`, `FileTransferDisposition`, `FileTransferResult`, `FileArchiveResult`, `FileImportDisposition`.

#### [ALEXLANDS/helpers/FileOperationCoordinator.swift](<ALEXLANDS/helpers/FileOperationCoordinator.swift>)

Estado compartido de selección para copiar/mover y avance de una sesión de transferencia con conflictos.

- Tamaño: 2.188 bytes; 80 líneas.
- Símbolos para localizar: `FileOperationPayload`, `FileTransferSession`, `FileOperationCoordinator`.

#### [ALEXLANDS/helpers/FileReplacementService.swift](<ALEXLANDS/helpers/FileReplacementService.swift>)

Política del selector de reemplazo, validación de origen/destino y sustitución de archivos; rechaza carpetas/enlaces según sus reglas.

- Tamaño: 6.283 bytes; 181 líneas.
- Símbolos para localizar: `ReplacementPickerPolicy`, `FileReplacementSelection`, `FileReplacementRequest`, `FileReplacementError`, `FileReplacementResult`, `FileReplacementService`.

#### [ALEXLANDS/helpers/KernelExploit.swift](<ALEXLANDS/helpers/KernelExploit.swift>)

Adaptador Swift del componente kernel y escape de sandbox, comprobación de acceso y comportamiento especial de simulador/versiones.

- Tamaño: 3.010 bytes; 76 líneas.
- Símbolos para localizar: `KernelExploit`.

#### [ALEXLANDS/helpers/LimitedCleanerService.swift](<ALEXLANDS/helpers/LimitedCleanerService.swift>)

Medición y limpieza limitada a Library/Caches y tmp dentro de un contenedor validado; usa descriptores y evita seguir enlaces.

- Tamaño: 8.897 bytes; 263 líneas.
- Símbolos para localizar: `LimitedCleanerUsage`, `LimitedCleanerResult`, `LimitedCleanerError`, `LimitedCleanerService`, `ScanSummary`, `RemovalSummary`.

#### [ALEXLANDS/helpers/Localization.swift](<ALEXLANDS/helpers/Localization.swift>)

Idiomas en/es/vi/zh-Hans, almacenamiento de la selección, resolución de bundles y formateo de mensajes localizados.

- Tamaño: 2.069 bytes; 67 líneas.
- Símbolos para localizar: `AppLanguage`, `AppLanguageEnvironmentKey`.

#### [ALEXLANDS/helpers/MG.swift](<ALEXLANDS/helpers/MG.swift>)

Comprobación de acceso de lectura/escritura a una ruta con apertura sin seguir enlaces; pese al nombre, no contiene un editor completo MobileGestalt.

- Tamaño: 393 bytes; 13 líneas.

#### [ALEXLANDS/helpers/PackageRepositoryModels.swift](<ALEXLANDS/helpers/PackageRepositoryModels.swift>)

Modelos JSON de fuentes/paquetes/catálogos, validación de URL y límites, compatibilidad, ordenación, etiquetas, hashes y URL del catálogo predeterminado.

- Tamaño: 28.514 bytes; 851 líneas.
- Símbolos para localizar: `PackageRepositoryError`, `PackageRepositoryDocument`, `PackageRepositoryCatalogDocument`, `PackageRepositoryPackageDocument`, `RepositoryPackageKind`, `PackageOSRange`, `PackageRepository`.

#### [ALEXLANDS/helpers/PackageRepositoryStore.swift](<ALEXLANDS/helpers/PackageRepositoryStore.swift>)

Estado observable de fuentes y descargas; persistencia, sincronización del catálogo, errores e integración de paquetes descargados.

- Tamaño: 24.508 bytes; 641 líneas.
- Símbolos para localizar: `RepositoryStoreAlert`, `PackageRepositoryStore`, `PackageRepositoryRedirectDelegate`, `PackageRepositoryNetworkClient`.

#### [ALEXLANDS/helpers/PatchDraftCoordinator.swift](<ALEXLANDS/helpers/PatchDraftCoordinator.swift>)

Estado compartido para presentar borradores e importaciones; interpreta archivos/URL remotas y el esquema threeoneosfive.

- Tamaño: 2.040 bytes; 76 líneas.
- Símbolos para localizar: `PatchDraftRequest`, `PatchImportSource`, `PatchImportRoute`, `PatchImportRequest`, `PatchDraftCoordinator`.

#### [ALEXLANDS/helpers/PatchDraftService.swift](<ALEXLANDS/helpers/PatchDraftService.swift>)

Convierte selecciones de archivos/carpetas en candidatos y borradores con identificadores de aplicación y rutas relativas.

- Tamaño: 10.193 bytes; 272 líneas.
- Símbolos para localizar: `PatchProjectDraft`, `PatchDraftCandidate`, `PatchDraftService`.

#### [ALEXLANDS/helpers/PatchKeyStore.swift](<ALEXLANDS/helpers/PatchKeyStore.swift>)

Guarda, carga y elimina claves de contenido de paquetes en Keychain.

- Tamaño: 2.899 bytes; 72 líneas.
- Símbolos para localizar: `PatchKeyStore`.

#### [ALEXLANDS/helpers/PatchPackageCodec.swift](<ALEXLANDS/helpers/PatchPackageCodec.swift>)

Formato .3105, sobre y payload, lectura de versiones 1–3, validación, cifrado AES-GCM, hashes y derivación de contraseña.

- Tamaño: 19.902 bytes; 496 líneas.
- Símbolos para localizar: `PatchPackageCodec`.

#### [ALEXLANDS/helpers/PatchProjectLibrary.swift](<ALEXLANDS/helpers/PatchProjectLibrary.swift>)

Biblioteca persistente de paquetes, copias de autor, procedencia, importación, eliminación y sincronización con workspace.

- Tamaño: 15.504 bytes; 411 líneas.
- Símbolos para localizar: `PatchLibraryItem`, `PatchPasswordRequest`, `PatchProjectLibrary`.

#### [ALEXLANDS/helpers/PatchProjectModels.swift](<ALEXLANDS/helpers/PatchProjectModels.swift>)

Proyectos, reglas, directorios, metadatos de paquete, errores, límites y validadores de identificadores/rutas. Define políticas de acceso a proyectos privados.

- Tamaño: 11.921 bytes; 345 líneas.
- Símbolos para localizar: `PatchRule`, `PatchDirectory`, `PatchProject`, `PatchProjectAccessPolicy`, `PatchPackageSummary`, `PatchPackageOrigin`, `EncodedPatchPackage`.

#### [ALEXLANDS/helpers/PatchProjectStore.swift](<ALEXLANDS/helpers/PatchProjectStore.swift>)

Estado de UI de la biblioteca; crea/edita/importa/desbloquea/elimina proyectos y presenta errores y solicitudes de contraseña.

- Tamaño: 15.735 bytes; 444 líneas.
- Símbolos para localizar: `PatchStoreAlert`, `PatchProjectStore`.

#### [ALEXLANDS/helpers/PatchTransaction.swift](<ALEXLANDS/helpers/PatchTransaction.swift>)

Motor de aplicación y recuperación: diarios, respaldos, hashes, registro de archivos/directorios, inspección de cambios y restauración/restablecimiento.

- Tamaño: 39.750 bytes; 993 líneas.
- Símbolos para localizar: `PatchTransactionReceipt`, `PatchTargetChangeKind`, `PatchTargetChange`, `PatchRestoreInspection`, `PatchTransaction`.

#### [ALEXLANDS/helpers/PatchWorkspaceService.swift](<ALEXLANDS/helpers/PatchWorkspaceService.swift>)

Crea y mantiene el árbol editable en Documents/Patches, materializa proyectos y obtiene snapshots para aplicar/exportar.

- Tamaño: 16.049 bytes; 404 líneas.
- Símbolos para localizar: `PatchWorkspaceService`.

#### [ALEXLANDS/helpers/RepositoryPresentationSupport.swift](<ALEXLANDS/helpers/RepositoryPresentationSupport.swift>)

Formato de tiempos de descarga, dimensiones de previsualización y carga/caché de imágenes remotas con actor y observable de UI.

- Tamaño: 7.865 bytes; 247 líneas.
- Símbolos para localizar: `RepositoryDownloadDurationFormatter`, `RepositoryPreviewSize`, `RepositoryPreviewLayout`, `RepositoryImagePipelineError`, `RepositoryImageRedirectDelegate`, `RepositoryImagePipeline`, `RepositoryImageLoader`.

#### [ALEXLANDS/helpers/SBX.swift](<ALEXLANDS/helpers/SBX.swift>)

Envoltorios dinámicos para emitir y consumir extensiones de sandbox; integración con APIs nativas del sistema.

- Tamaño: 1.028 bytes; 22 líneas.

#### [ALEXLANDS/helpers/SecureZIPArchive.swift](<ALEXLANDS/helpers/SecureZIPArchive.swift>)

Extracción validada usada para paquetes de fondos, con control de entradas/rutas/tamaños; llama al extractor C mediante símbolo externo.

- Tamaño: 12.790 bytes; 316 líneas.
- Símbolos para localizar: `SecureZIPExtraction`, `SecureZIPArchive`, `Entry`.

#### [ALEXLANDS/helpers/SupportPolicy.swift](<ALEXLANDS/helpers/SupportPolicy.swift>)

Lista y reglas de versiones/builds que la app considera admitidas; fuente principal para mensajes y habilitación de acceso.

- Tamaño: 1.507 bytes; 50 líneas.
- Símbolos para localizar: `ExploitSupportPolicy`.

#### [ALEXLANDS/helpers/Utils.swift](<ALEXLANDS/helpers/Utils.swift>)

Logs, captura stdout/stderr, datos de dispositivo/versión, ExploitStatus, rutas auxiliares y comprobador de actualizaciones de GitHub.

- Tamaño: 7.909 bytes; 210 líneas.
- Símbolos para localizar: `AppLog`, `AppInfo`, `ExploitStatus`, `AppPaths`, `AppUpdateChecker`.

#### [ALEXLANDS/helpers/WallpaperInstaller.swift](<ALEXLANDS/helpers/WallpaperInstaller.swift>)

Instala descriptores, genera recibos, conserva copias, restaura y restablece contenido; incluye identidad y reescritura de descriptores.

- Tamaño: 24.565 bytes; 612 líneas.
- Símbolos para localizar: `WallpaperInstalledDescriptor`, `WallpaperInstallStatus`, `WallpaperInstallReceipt`, `WallpaperInstaller`, `WallpaperDescriptorIdentity`, `WallpaperDescriptorRewriter`.

#### [ALEXLANDS/helpers/WallpaperLabModels.swift](<ALEXLANDS/helpers/WallpaperLabModels.swift>)

Errores, límites de paquetes, modelos PosterBoard, inspección .tendies y validación de rutas/estructura de descriptores.

- Tamaño: 16.274 bytes; 399 líneas.
- Símbolos para localizar: `WallpaperLabError`, `WallpaperLabLimits`, `WallpaperPosterLayout`, `WallpaperDescriptorSource`, `TendiesPayload`, `WallpaperLayoutScanner`, `TendiesPackageInspector`.

#### [ALEXLANDS/helpers/WallpaperLabService.swift](<ALEXLANDS/helpers/WallpaperLabService.swift>)

Pruebas de acceso, adaptación al dispositivo, importación/preparación/listado/eliminación de paquetes y rutas de almacenamiento.

- Tamaño: 16.514 bytes; 417 líneas.
- Símbolos para localizar: `WallpaperAccessReport`, `WallpaperAccessProbe`, `WallpaperDeviceAccessService`, `WallpaperStagedPackage`, `WallpaperPackageStore`, `PackageMetadata`.

#### [ALEXLANDS/helpers/ZIPArchiveExtractor.swift](<ALEXLANDS/helpers/ZIPArchiveExtractor.swift>)

Extracción ZIP del explorador de archivos con validación, área temporal y resolución del destino; comparte la rutina C de extracción por entrada.

- Tamaño: 14.514 bytes; 352 líneas.
- Símbolos para localizar: `ZIPArchiveExtractorError`, `ZIPArchiveExtractionResult`, `ZIPArchiveExtractor`.

#### [ALEXLANDS/helpers/ZIPArchiveWriter.swift](<ALEXLANDS/helpers/ZIPArchiveWriter.swift>)

Crea ZIP sin compresión, por bloques, con CRC y validación de entradas; no asumir que reduce el tamaño del contenido.

- Tamaño: 14.221 bytes; 370 líneas.
- Símbolos para localizar: `ZIPArchiveWriterError`, `ZIPArchiveWriteResult`, `ZIPArchiveWriter`.

### Puentes de contenedores y ZIP — exploit

#### [ALEXLANDS/exploit/bad_query.c](<ALEXLANDS/exploit/bad_query.c>)

Implementación de consultas dinámicas a ContainerManager, adquisición/liberación de acceso y enumeración de rutas. Componente de bajo nivel.

- Tamaño: 7.196 bytes; 173 líneas.

#### [ALEXLANDS/exploit/bad_query.h](<ALEXLANDS/exploit/bad_query.h>)

Contrato C para solicitar acceso, listar y liberar acceso a rutas mediante el componente de consultas de contenedores.

- Tamaño: 286 bytes; 12 líneas.

#### [ALEXLANDS/exploit/mcm_bridge.h](<ALEXLANDS/exploit/mcm_bridge.h>)

Interfaz Objective-C para enumerar, resolver y activar contenedores MobileContainerManager.

- Tamaño: 701 bytes; 30 líneas.

#### [ALEXLANDS/exploit/mcm_bridge.m](<ALEXLANDS/exploit/mcm_bridge.m>)

Carga dinámica de APIs MCM y adaptación de objetos/resultados para la capa Swift de contenedores.

- Tamaño: 12.935 bytes; 332 líneas.

#### [ALEXLANDS/exploit/wallpaper_zip.c](<ALEXLANDS/exploit/wallpaper_zip.c>)

Rutina C de extracción de entradas ZIP y comprobación de tamaño/CRC, usada por los dos extractores Swift; dependencia zlib.

- Tamaño: 5.000 bytes; 150 líneas.

#### [ALEXLANDS/exploit/wallpaper_zip.h](<ALEXLANDS/exploit/wallpaper_zip.h>)

Declaración de extracción de una entrada ZIP con offsets, tamaños, método y CRC esperado.

- Tamaño: 323 bytes; 16 líneas.

### Componentes kernel — kexploit

#### [ALEXLANDS/kexploit/kexploit_opa334.h](<ALEXLANDS/kexploit/kexploit_opa334.h>)

Declaraciones de entrada del componente kernel y primitivas iniciales de acceso.

- Tamaño: 1.180 bytes; 18 líneas.

#### [ALEXLANDS/kexploit/kexploit_opa334.m](<ALEXLANDS/kexploit/kexploit_opa334.m>)

Implementación nativa del componente de acceso kernel; depende de offsets, hardware y utilidades. No es necesario tocarla para cambiar la interfaz.

- Tamaño: 38.886 bytes; 1.028 líneas.

#### [ALEXLANDS/kexploit/krw.h](<ALEXLANDS/kexploit/krw.h>)

Declaraciones y macros para primitivas de lectura/escritura y tratamiento de punteros kernel.

- Tamaño: 1.065 bytes; 37 líneas.

#### [ALEXLANDS/kexploit/krw.m](<ALEXLANDS/kexploit/krw.m>)

Implementación de primitivas de lectura/escritura utilizadas por los módulos de acceso de bajo nivel.

- Tamaño: 5.213 bytes; 192 líneas.

#### [ALEXLANDS/kexploit/kutils.h](<ALEXLANDS/kexploit/kutils.h>)

Declaraciones de utilidades para procesos, tareas, hilos, credenciales y objetos kernel.

- Tamaño: 1.101 bytes; 30 líneas.

#### [ALEXLANDS/kexploit/kutils.m](<ALEXLANDS/kexploit/kutils.m>)

Implementación de las utilidades compartidas de objetos/procesos del componente kernel.

- Tamaño: 6.661 bytes; 232 líneas.

#### [ALEXLANDS/kexploit/machine_info.h](<ALEXLANDS/kexploit/machine_info.h>)

Constantes e identificadores de familias de CPU utilizados por la selección de configuración nativa.

- Tamaño: 1.598 bytes; 55 líneas.

#### [ALEXLANDS/kexploit/offsets.h](<ALEXLANDS/kexploit/offsets.h>)

Declaraciones de offsets y parámetros compartidos de estructuras del sistema.

- Tamaño: 3.502 bytes; 92 líneas.

#### [ALEXLANDS/kexploit/offsets.m](<ALEXLANDS/kexploit/offsets.m>)

Selección e inicialización de offsets según sistema/hardware; tablas y condiciones propias del componente nativo.

- Tamaño: 49.641 bytes; 976 líneas.

#### [ALEXLANDS/kexploit/sandbox_escape.h](<ALEXLANDS/kexploit/sandbox_escape.h>)

Declaraciones de comprobación de acceso, escape de sandbox y elevación de credenciales.

- Tamaño: 205 bytes; 10 líneas.

#### [ALEXLANDS/kexploit/sandbox_escape.m](<ALEXLANDS/kexploit/sandbox_escape.m>)

Implementación nativa de cambios de acceso y verificación correspondiente; requiere validación física si se modifica.

- Tamaño: 8.801 bytes; 273 líneas.

#### [ALEXLANDS/kexploit/vnode.h](<ALEXLANDS/kexploit/vnode.h>)

Declaraciones de búsqueda y redirección/restauración de objetos vnode de archivos y carpetas.

- Tamaño: 729 bytes; 18 líneas.

#### [ALEXLANDS/kexploit/vnode.m](<ALEXLANDS/kexploit/vnode.m>)

Implementación de utilidades vnode utilizadas por el acceso a archivos de bajo nivel.

- Tamaño: 5.175 bytes; 158 líneas.

#### [ALEXLANDS/kexploit/xpaci.h](<ALEXLANDS/kexploit/xpaci.h>)

Auxiliar de tratamiento de punteros con instrucciones ARM/PAC; dependencia de arquitectura del módulo nativo.

- Tamaño: 339 bytes; 15 líneas.

### Traducciones

#### [ALEXLANDS/en.lproj/Localizable.strings](<ALEXLANDS/en.lproj/Localizable.strings>)

Catálogo de interfaz para en: 653 claves únicas. Editar valores conservando claves y marcadores de formato.

- Tamaño: 41.034 bytes; 669 líneas.

#### [ALEXLANDS/es.lproj/Localizable.strings](<ALEXLANDS/es.lproj/Localizable.strings>)

Catálogo de interfaz para es: 653 claves únicas. Editar valores conservando claves y marcadores de formato. Traducción parcial: 602 valores coinciden con el inglés; falta enlazar esta variante al grupo de recursos Xcode.

- Tamaño: 41.154 bytes; 670 líneas.

#### [ALEXLANDS/vi.lproj/Localizable.strings](<ALEXLANDS/vi.lproj/Localizable.strings>)

Catálogo de interfaz para vi: 653 claves únicas. Editar valores conservando claves y marcadores de formato.

- Tamaño: 46.691 bytes; 669 líneas.

#### [ALEXLANDS/zh-Hans.lproj/Localizable.strings](<ALEXLANDS/zh-Hans.lproj/Localizable.strings>)

Catálogo de interfaz para zh-Hans: 653 claves únicas. Editar valores conservando claves y marcadores de formato.

- Tamaño: 40.379 bytes; 669 líneas.

### Recursos gráficos

#### [ALEXLANDS/Assets.xcassets/AppBackground.imageset/Contents.json](<ALEXLANDS/Assets.xcassets/AppBackground.imageset/Contents.json>)

Declara FONDO.PNG como imagen universal accesible desde SwiftUI como AppBackground.

- Tamaño: 156 bytes; 12 líneas.

#### [ALEXLANDS/Assets.xcassets/AppBackground.imageset/FONDO.PNG](<ALEXLANDS/Assets.xcassets/AppBackground.imageset/FONDO.PNG>)

Imagen de fondo; la copia en AppBackground.imageset es la que referencia el catálogo. Ambas tienen los mismos bytes.

- Tamaño: 2.826.824 bytes; 853 × 1844 px.

#### [ALEXLANDS/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png](<ALEXLANDS/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png>)

Icono iOS de 1024 × 1024 referenciado por el catálogo AppIcon y compilado como recurso de la app.

- Tamaño: 1.179.037 bytes; 1024 × 1024 px.

#### [ALEXLANDS/Assets.xcassets/AppIcon.appiconset/Contents.json](<ALEXLANDS/Assets.xcassets/AppIcon.appiconset/Contents.json>)

Declara AppIcon-1024.png como icono universal iOS de 1024 × 1024.

- Tamaño: 216 bytes; 14 líneas.

#### [ALEXLANDS/Assets.xcassets/Contents.json](<ALEXLANDS/Assets.xcassets/Contents.json>)

Metadatos del catálogo de recursos de Xcode.

- Tamaño: 63 bytes; 6 líneas.

## 8. Comprobaciones realizadas para este informe

- Enumeración de todos los archivos existentes fuera de `.git` y cotejo de las 114 entradas del inventario.
- Revisión de arranque, navegación, estado observable, servicios principales, puentes y configuración de compilación.
- Comparación de claves y valores de las cuatro localizaciones: 653 claves únicas por idioma, sin faltantes ni adicionales respecto al inglés.
- Verificación de referencias del español y pertenencia al grupo de recursos Xcode.
- Lectura de los seis scripts sin ejecutarlos; detección de rutas antiguas y sustituciones inconsistentes.
- Comprobación de dimensiones PNG y coincidencia exacta de las dos copias del fondo.
- Revisión del estado inicial de Git: eliminación previa del workflow; no se modificó código de la aplicación.

Pendiente para validar una versión modificada: compilación con Xcode, inspección del producto generado y pruebas de interfaz/dispositivo. Este informe sirve como mapa de edición y lista inicial de problemas; no afirma que la app esté libre de errores.
