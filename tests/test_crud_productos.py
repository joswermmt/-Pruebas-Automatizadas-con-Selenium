"""
HU-02: Crear producto en el inventario.
HU-03: Ver listado de productos.
HU-04: Editar un producto existente.
HU-05: Eliminar un producto.

Cada historia tiene escenarios: camino feliz, negativo y/o límites según aplique.
"""

import uuid

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.constants import TEST_PASSWORD, TEST_USER


def _uniq(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def test_hu02_crear_producto_camino_feliz(logged_in_driver, base_url):
    driver = logged_in_driver
    nombre = _uniq("Producto OK")
    driver.get(base_url + "/productos/nuevo")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-nombre"]').send_keys(nombre)
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-cantidad"]').clear()
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-cantidad"]').send_keys("10")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-descripcion"]').send_keys(
        "Descripción de prueba"
    )
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-guardar-producto"]').click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="flash-success"]'))
    )
    body = driver.find_element(By.TAG_NAME, "body").text
    assert nombre in body


def test_hu02_crear_producto_negativa_nombre_vacio(logged_in_driver, base_url):
    driver = logged_in_driver
    driver.get(base_url + "/productos/nuevo")
    nombre = driver.find_element(By.CSS_SELECTOR, '[data-testid="input-nombre"]')
    driver.execute_script("arguments[0].removeAttribute('required')", nombre)
    nombre.clear()
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-guardar-producto"]').click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="flash-danger"]'))
    )
    assert "obligatorio" in driver.find_element(
        By.CSS_SELECTOR, '[data-testid="flash-danger"]'
    ).text.lower()


def test_hu02_crear_producto_limite_nombre_demasiado_largo(logged_in_driver, base_url):
    driver = logged_in_driver
    driver.get(base_url + "/productos/nuevo")
    largo = "X" * 81
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-nombre"]').send_keys(largo)
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-cantidad"]').clear()
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-cantidad"]').send_keys("1")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-guardar-producto"]').click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="flash-danger"]'))
    )
    assert "80" in driver.find_element(
        By.CSS_SELECTOR, '[data-testid="flash-danger"]'
    ).text or "superar" in driver.find_element(
        By.CSS_SELECTOR, '[data-testid="flash-danger"]'
    ).text.lower()


def test_hu02_crear_producto_limite_cantidad_fuera_de_rango(logged_in_driver, base_url):
    driver = logged_in_driver
    driver.get(base_url + "/productos/nuevo")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-nombre"]').send_keys(
        _uniq("LimiteCant")
    )
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-cantidad"]').clear()
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-cantidad"]').send_keys("100000")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-guardar-producto"]').click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="flash-danger"]'))
    )


def test_hu03_listar_productos_camino_feliz(logged_in_driver, base_url):
    driver = logged_in_driver
    nombre = _uniq("Para Ver Lista")
    driver.get(base_url + "/productos/nuevo")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-nombre"]').send_keys(nombre)
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-cantidad"]').clear()
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-cantidad"]').send_keys("3")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-guardar-producto"]').click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="flash-success"]'))
    )

    driver.get(base_url + "/productos")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tabla-productos"]'))
    )
    assert nombre in driver.find_element(By.TAG_NAME, "body").text


def test_hu03_listar_sin_sesion_redirige_a_login(driver, base_url):
    driver.get(base_url + "/productos")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="form-login"]'))
    )


def test_hu04_editar_producto_camino_feliz(logged_in_driver, base_url):
    driver = logged_in_driver
    nombre = _uniq("EditarMe")
    driver.get(base_url + "/productos/nuevo")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-nombre"]').send_keys(nombre)
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-cantidad"]').clear()
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-cantidad"]').send_keys("5")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-guardar-producto"]').click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="flash-success"]'))
    )

    driver.get(base_url + "/productos")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tabla-productos"]'))
    )
    fila = driver.find_element(
        By.XPATH, f"//td[contains(@data-testid,'celda-nombre') and contains(., '{nombre}')]/../.."
    )
    btn = fila.find_element(By.CSS_SELECTOR, '[data-testid^="btn-editar-"]')
    btn.click()

    nuevo = nombre + "_EDITADO"
    el = driver.find_element(By.CSS_SELECTOR, '[data-testid="input-nombre"]')
    el.clear()
    el.send_keys(nuevo)
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-guardar-producto"]').click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="flash-success"]'))
    )
    assert nuevo in driver.find_element(By.TAG_NAME, "body").text


def test_hu04_editar_producto_negativa_nombre_vacio(logged_in_driver, base_url):
    driver = logged_in_driver
    nombre = _uniq("EditNeg")
    driver.get(base_url + "/productos/nuevo")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-nombre"]').send_keys(nombre)
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-cantidad"]').clear()
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-cantidad"]').send_keys("1")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-guardar-producto"]').click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="flash-success"]'))
    )

    driver.get(base_url + "/productos")
    fila = driver.find_element(
        By.XPATH, f"//td[contains(@data-testid,'celda-nombre') and contains(., '{nombre}')]/../.."
    )
    fila.find_element(By.CSS_SELECTOR, '[data-testid^="btn-editar-"]').click()

    n = driver.find_element(By.CSS_SELECTOR, '[data-testid="input-nombre"]')
    driver.execute_script("arguments[0].removeAttribute('required')", n)
    n.clear()
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-guardar-producto"]').click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="flash-danger"]'))
    )


def test_hu05_eliminar_producto_camino_feliz(logged_in_driver, base_url):
    driver = logged_in_driver
    nombre = _uniq("BorrarMe")
    driver.get(base_url + "/productos/nuevo")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-nombre"]').send_keys(nombre)
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-cantidad"]').clear()
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-cantidad"]').send_keys("1")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-guardar-producto"]').click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="flash-success"]'))
    )

    driver.get(base_url + "/productos")
    fila = driver.find_element(
        By.XPATH, f"//td[contains(@data-testid,'celda-nombre') and contains(., '{nombre}')]/../.."
    )
    fila.find_element(By.CSS_SELECTOR, '[data-testid^="btn-eliminar-"]').click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="flash-success"]'))
    )
    driver.get(base_url + "/productos")
    body = driver.find_element(By.TAG_NAME, "body").text
    assert nombre not in body


def test_hu05_eliminar_negativa_id_inexistente(driver, base_url):
    """Negativa: POST a eliminar con id no existente no rompe la app (mensaje advertencia)."""
    driver.get(base_url + "/login")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-username"]').send_keys(TEST_USER)
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-password"]').send_keys(TEST_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-login"]').click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="user-label"]'))
    )

    driver.execute_script(
        """
        var f = document.createElement('form');
        f.method = 'POST';
        f.action = arguments[0];
        document.body.appendChild(f);
        f.submit();
        """,
        base_url + "/productos/999999/eliminar",
    )
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="flash-warning"]'))
    )
