import os
import threading
import time
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from app import create_app

from tests.constants import TEST_PASSWORD, TEST_USER

REPORT_ROOT = Path(__file__).resolve().parent.parent / "reportes"
SCREENSHOT_DIR = REPORT_ROOT / "capturas"


def _free_port():
    import socket

    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    _, port = s.getsockname()
    s.close()
    return port


@pytest.fixture(scope="session")
def live_server():
    """Servidor Flask real para Selenium (misma sesión de pruebas)."""
    instance = Path(__file__).resolve().parent.parent / "instance_test"
    instance.mkdir(parents=True, exist_ok=True)
    db_path = instance / "selenium_test.sqlite3"
    if db_path.exists():
        db_path.unlink()

    test_config = {
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "DATABASE": str(db_path),
    }
    app = create_app(test_config)

    port = _free_port()

    def run():
        app.run(host="127.0.0.1", port=port, use_reloader=False, threaded=True)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    deadline = time.time() + 15
    import urllib.request

    base = f"http://127.0.0.1:{port}"
    while time.time() < deadline:
        try:
            urllib.request.urlopen(base + "/login", timeout=0.5)
            break
        except OSError:
            time.sleep(0.2)
    else:
        pytest.fail("No se pudo iniciar el servidor de prueba.")

    yield base


@pytest.fixture
def base_url(live_server):
    return live_server


def _selenium_headless() -> bool:
    return os.environ.get("SELENIUM_HEADLESS", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


@pytest.fixture
def driver(request, base_url):
    """Chrome con captura al final de cada prueba. Ventana visible por defecto.

    Sin ventana (headless): define `SELENIUM_HEADLESS=1` antes de ejecutar pytest.
    """
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    options = webdriver.ChromeOptions()
    if _selenium_headless():
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1400,900")

    drv = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options,
    )
    drv.implicitly_wait(5)
    drv.set_window_size(1400, 900)

    yield drv

    safe_name = request.node.name.replace("[", "_").replace("]", "_")
    shot = SCREENSHOT_DIR / f"{safe_name}.png"
    try:
        drv.save_screenshot(str(shot))
    except Exception:
        pass
    drv.quit()


def login_ok(driver, base_url):
    driver.get(base_url + "/login")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-username"]').clear()
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-username"]').send_keys(
        TEST_USER
    )
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-password"]').clear()
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-password"]').send_keys(
        TEST_PASSWORD
    )
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-login"]').click()
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="user-label"], [data-testid="lista-title"]')
        )
    )


@pytest.fixture
def logged_in_driver(driver, base_url):
    login_ok(driver, base_url)
    return driver
