# Sistema de Gestion de Inventario TI

Un sistema basico pero eficiente para la gestion de activos, diseñado para departamento de TI.

## Caracteristicas Principales

- Dashboard en Tiempo Real: Visualizacion inmediata de metricas clave (Total de equipos, activos, en reparacion y bajas).
- Gestion Integral (CRUD): Registro, edicion y eliminacion de equipos con campos detallados (Codigo, Serie, MAC/IP, Asignacion, etc.).
- Interfaz Moderna: Construida con CustomTkinter, ofreciendo soporte nativo para Modo Claro y Modo Oscuro.
- Busqueda Dinamica: Filtro instantaneo por codigo, serie o nombre mientras escribes.
- Exportacion de Datos: Generacion de reportes completos en formato CSV.
- Base de Datos Local: Utiliza SQLite para un manejo de datos rapido sin necesidad de servidores externos.
(Proximamente poseerá tanto base de datos local como remota para escalabilidad de usuarios).

## Capturas de Pantalla

-Dashboard
![Dashboard](/images/image2.png)

-Gestion de Equipos
![Gestion de Equipos](/images/image.png)

## Tecnologias Utilizadas

- Lenguaje: Python 3.10+
- Interfaz Grafica: CustomTkinter
- Persistencia: SQLite3
- Distribucion: PyInstaller

## Instalacion (Windows)

El sistema esta diseñado para ser portable y facil de instalar mediante el script incluido.

1. Descarga la carpeta del proyecto o el ejecutable.
2. Ejecuta el archivo install.ps1 con PowerShell:
   ```powershell
   ./install.ps1
   ```
3. El script realizara lo siguiente:
   - Creara una carpeta en %APPDATA%\Inventario TI App.
   - Copiara los archivos necesarios.
   - Creara un acceso directo en tu Escritorio.

IMPORTANTE: Los datos se guardan de forma segura en tu carpeta de usuario (%APPDATA%), lo que permite actualizar el programa sin perder la base de datos.

## Desarrollo

Si deseas ejecutar el proyecto desde el codigo fuente o realizar modificaciones:

### Requisitos
- Python 3.10 o superior
- pip (gestor de paquetes)

### Pasos
1. Clona el repositorio.
2. Instala las dependencias:
   ```bash
   pip install customtkinter
   ```
3. Ejecuta la aplicacion:
   ```bash
   python main.py
   ```

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo LICENSE para mas detalles.

---
