# Green Search

Buscador de archivos de escritorio para Windows, con interfaz HTML/CSS local y motor de búsqueda en Python.

## Ejecutar

Abre `abrir_buscador.bat`. Si `pywebview` no está instalado, el lanzador lo instala con `pip` la primera vez. Se requiere conexión a Internet para esa instalación inicial y el runtime de Microsoft Edge WebView2 para mostrar la interfaz.

## Funciones

- Buscar archivos por palabras del nombre, comodines (`*`, `?`) y extensión.
- Añadir varios filtros de nombre y combinarlos.
- Abrir archivos o su ubicación en el Explorador.
- Copiar al portapapeles la ruta del archivo o de su carpeta.

La interfaz se carga desde HTML incluido en la aplicación; no necesita un servidor externo.
