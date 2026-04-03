"""
HU-01: Como usuario autenticado quiero iniciar sesión para acceder al inventario de productos.

Casos: camino feliz, negativo, límites.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.constants import TEST_PASSWORD, TEST_USER


def test_hu01_login_camino_feliz(driver, base_url):
    driver.get(base_url + "/login")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-username"]').send_keys(
        TEST_USER
    )
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-password"]').send_keys(
        TEST_PASSWORD
    )
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-login"]').click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="user-label"]'))
    )
    assert TEST_USER in driver.find_element(
        By.CSS_SELECTOR, '[data-testid="user-label"]'
    ).text


def test_hu01_login_negativa_credenciales_invalidas(driver, base_url):
    driver.get(base_url + "/login")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-username"]').send_keys(
        TEST_USER
    )
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-password"]').send_keys(
        "clave_incorrecta_123"
    )
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-login"]').click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="flash-danger"]'))
    )
    assert "incorrectos" in driver.find_element(
        By.CSS_SELECTOR, '[data-testid="flash-danger"]'
    ).text.lower()


def test_hu01_login_limite_intento_usuario_inexistente(driver, base_url):
    """Límite / borde: usuario que no existe debe rechazarse de forma controlada."""
    driver.get(base_url + "/login")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-username"]').send_keys(
        "usuario_que_no_existe_xyz"
    )
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-password"]').send_keys(
        "cualquier_clave"
    )
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-login"]').click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="flash-danger"]'))
    )
    assert driver.find_element(By.CSS_SELECTOR, '[data-testid="form-login"]')


def test_hu01_login_limite_campos_vacios_sin_html5_required(driver, base_url):
    """Prueba de límites: envío sin datos (se anula 'required' en cliente para ejercitar el flujo)."""
    driver.get(base_url + "/login")
    user_el = driver.find_element(By.CSS_SELECTOR, '[data-testid="input-username"]')
    pass_el = driver.find_element(By.CSS_SELECTOR, '[data-testid="input-password"]')
    driver.execute_script("arguments[0].removeAttribute('required')", user_el)
    driver.execute_script("arguments[0].removeAttribute('required')", pass_el)
    user_el.clear()
    pass_el.clear()
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-login"]').click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="flash-danger"]'))
    )
