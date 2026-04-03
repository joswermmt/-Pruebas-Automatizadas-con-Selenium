# Tarea 4 — Inventario + Selenium (Python)

Aplicación web **Flask** con **login** y **CRUD de productos** (SQLite), más suite **Selenium** sin Selenium IDE: camino feliz, negativas y límites; **reporte HTML** (`pytest-html`) y **capturas PNG** por escenario en `reportes/capturas/`.

## Requisitos

- Python 3.10+
- Google Chrome instalado (las pruebas abren **Chrome en ventana visible** por defecto para que veas la automatización)

## Cadena de comandos que vas a usar (PowerShell)

Ejecuta esto **desde la carpeta del proyecto** `tarea4-selenium` (ajusta la ruta `cd` si hace falta).

### 1) Primera vez (entorno e dependencias)

```powershell
cd "ruta\a\tarea4-selenium"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2) Probar la app a mano (opcional)

```powershell
.\.venv\Scripts\python run_server.py
```

En el navegador: `http://127.0.0.1:5000/login` — usuario `admin`, contraseña `Itla2024!` (o la que definas con `DEMO_PASSWORD` antes de reinicializar la BD).

### 3) Ejecutar todas las pruebas Selenium + reporte HTML

**Chrome visible** (por defecto; no definas `SELENIUM_HEADLESS`):

```powershell
cd "ruta\a\tarea4-selenium"
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python -m pytest tests/ --html=reportes/reporte.html --self-contained-html -v
```

Equivalente usando el script:

```powershell
.\ejecutar_pruebas.ps1
```

**Salida esperada:** `reportes/reporte.html` y capturas en `reportes/capturas/`.

### 4) Misma cadena pero sin ventana de Chrome (headless)

Útil para CI o si no quieres ver el navegador. En la **misma sesión** de PowerShell, **antes** de `pytest`:

```powershell
$env:SELENIUM_HEADLESS = "1"
.\.venv\Scripts\python -m pytest tests/ --html=reportes/reporte.html --self-contained-html -v
```

Para volver al modo visible en otra ventana o más tarde, en PowerShell:

```powershell
Remove-Item Env:SELENIUM_HEADLESS -ErrorAction SilentlyContinue
```

## Notas

- Con el servidor manual **no** hace falta para pytest: los tests levantan un servidor Flask en un puerto libre.
- Puedes definir otra contraseña demo con la variable de entorno `DEMO_PASSWORD` antes de borrar `instance/inventario.sqlite3` o ejecutar `flask --app wsgi init-db`.

