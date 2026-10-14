# Green Search

Buscador de archivos de escritorio para Windows, con interfaz HTML/CSS local y motor de búsqueda en Python.

## Ejecutar

Abre `abrir_buscador.bat`. El lanzador inicia `interfaz.py`. Si `pywebview` no está instalado, el lanzador lo instala con `pip` la primera vez. Se requiere conexión a Internet para esa instalación inicial y el runtime de Microsoft Edge WebView2 para mostrar la interfaz.

## Funciones

- Buscar archivos por palabras del nombre, comodines (`*`, `?`) y extensión.
- Añadir varios filtros de nombre y combinarlos.
- Abrir archivos o su ubicación en el Explorador.
- Copiar al portapapeles la ruta del archivo o de su carpeta.
- Exportar los resultados de una búsqueda a un XML con carpeta y nombre elegidos.
- Abrir el módulo independiente **Comparar XML** para cargar dos XML y listar los archivos nuevos.

## Comparar búsquedas

En **Buscador**, encuentra los archivos y pulsa **Exportar** para elegir dónde guardar el XML y qué nombre darle. En **Comparar XML**, carga los XML exportados por Green Search como A (anterior) y B (reciente), y pulsa **Comparar archivos**. Se listan las rutas completas presentes en B y ausentes en A.

La interfaz se carga desde HTML incluido en la aplicación; no necesita un servidor externo.

## Estructura modular

- `motor_busqueda.py`: motor independiente para recorrer carpetas y encontrar archivos. No importa ni conoce la interfaz.
- `motor_comparador.py`: motor independiente para exportar y comparar capturas XML. No importa ni conoce la interfaz.
- `interfaz.py`: interfaz de escritorio y adaptador que conecta botones y diálogos con ambos motores.
- `buscador.py`: punto de entrada compatible; delega el inicio a `interfaz.py`.

Cada módulo empieza con una guía en inglés para agentes AI que describe su responsabilidad, límites y contrato de ampliación. Los motores se pueden reutilizar directamente desde otro programa importando `SearchEngine` o `SnapshotEngine`. La interfaz depende de ambos motores; ninguno importa la interfaz ni bibliotecas de GUI.
