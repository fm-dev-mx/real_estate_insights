import pytest
from unittest.mock import MagicMock, patch, call
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException # Import TimeoutException

# Importar la función a probar
from src.data_collection.download_inventory import download_inventory_process

# Importar las constantes para poder mockearlas
from src.data_collection import download_inventory

@pytest.fixture
def mock_selenium_components():
    with patch('src.data_collection.download_inventory.webdriver.Chrome') as mock_chrome, \
         patch('src.data_collection.download_inventory.By', new=By), \
         patch('src.data_collection.download_inventory.WebDriverWait') as mock_webdriver_wait, \
         patch('src.data_collection.download_inventory.EC', new=EC): # EC no necesita ser mockeado, solo By

        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        # Mockear find_element y find_elements
        mock_driver.find_element.return_value = MagicMock()
        mock_driver.find_elements.return_value = [MagicMock()]

        # Mockear WebDriverWait
        mock_wait = MagicMock()
        mock_webdriver_wait.return_value = mock_wait
        mock_wait.until.return_value = MagicMock() # Default return for until

        yield mock_driver, mock_chrome, mock_webdriver_wait

@pytest.fixture
def mock_env_vars():
    with patch.dict(os.environ, {
        'C21_USERNAME': 'test_user',
        'C21_PSW': 'test_password',
        'REI_DB_NAME': 'test_db', # Necesario para el logging en el script principal
        'REI_DB_USER': 'test_user',
        'REI_DB_PASSWORD': 'test_password',
        'REI_DB_HOST': 'test_host',
        'REI_DB_PORT': '5432'
    }):
        yield

@pytest.fixture
def mock_os_functions(tmp_path):
    # Mockear las constantes de ruta en el módulo download_inventory
    with patch.object(download_inventory, 'DOWNLOAD_DIR', str(tmp_path / "downloads")), \
         patch.object(download_inventory, 'DOWNLOAD_FILE_PATH', str(tmp_path / "downloads" / "inventario.xls")), \
         patch.object(download_inventory, 'SCREENSHOT_DIR', str(tmp_path / "screenshots")), \
         patch.object(download_inventory, 'LOG_DIR', str(tmp_path / "logs")), \
         patch('src.data_collection.download_inventory.os.makedirs') as mock_makedirs, \
         patch('src.data_collection.download_inventory.os.path.exists') as mock_exists, \
         patch('src.data_collection.download_inventory.os.listdir') as mock_listdir, \
         patch('src.data_collection.download_inventory.os.path.getsize') as mock_getsize:
        
        # Default mocks for success scenario
        mock_exists.return_value = True
        mock_listdir.return_value = ['inventario.xls']
        mock_getsize.return_value = 1024 # 1KB

        yield mock_makedirs, mock_exists, mock_listdir, mock_getsize

@pytest.fixture
def mock_file_operations():
    with patch('builtins.open', MagicMock()) as mock_open:
        yield mock_open

def test_download_inventory_success(mock_selenium_components, mock_env_vars, mock_os_functions, mock_file_operations):
    mock_driver, mock_chrome, mock_webdriver_wait = mock_selenium_components
    mock_makedirs, mock_exists, mock_listdir, mock_getsize = mock_os_functions
    mock_open = mock_file_operations

    # Arrange
    # Mockear el elemento de descarga para que tenga un atributo 'get_attribute'
    mock_download_element = MagicMock()
    mock_download_element.get_attribute.return_value = "inventario.xls"
    
    # Mockear los elementos que WebDriverWait.until debería devolver
    mock_username_input = MagicMock()
    mock_password_input = MagicMock()
    mock_csrf_token_input = MagicMock(get_attribute=MagicMock(return_value="mock_csrf_token"))
    mock_webdriver_wait.return_value.until.side_effect = [
        mock_username_input, # for EC.visibility_of_element_located((By.NAME, '_username'))
        mock_password_input, # for EC.visibility_of_element_located((By.NAME, '_password'))
        mock_csrf_token_input, # for EC.presence_of_element_located((By.NAME, '_csrf_token'))
        MagicMock(), # for EC.any_of (successful login URL condition)
        MagicMock(), # for EC.element_to_be_clickable (main download button)
        mock_download_element # for EC.element_to_be_clickable (submenu download option)
    ]

    # Mockear find_element para el formulario de login
    mock_login_form = MagicMock()
    mock_driver.find_element.return_value = mock_login_form

    # Act
    download_inventory_process()

    # Assert
    mock_chrome.assert_called_once() # Se llama al constructor de Chrome
    
    # Verificar las llamadas a driver.get
    expected_gets = [
        call("https://plus.21onlinemx.com/login2"),
        call("https://plus.21onlinemx.com/propiedades")
    ]
    mock_driver.get.assert_has_calls(expected_gets)

    mock_username_input.send_keys.assert_called_once_with(os.environ.get('C21_USERNAME'))
    mock_password_input.send_keys.assert_called_once_with(os.environ.get('C21_PSW'))
    mock_login_form.submit.assert_called_once() # Se hace submit del formulario de login
    mock_webdriver_wait.return_value.until.assert_called() # Verificar que se llamó a until
    mock_download_element.click.assert_called_once() # Se hace clic en la opción de descarga del submenú
    mock_driver.quit.assert_called_once() # El navegador se cierra
    mock_exists.assert_called_once_with(download_inventory.DOWNLOAD_FILE_PATH) # Verificar que se llamó a os.path.exists con la ruta correcta
    mock_listdir.assert_called_once_with(download_inventory.DOWNLOAD_DIR) # Verificar que se llamó a os.listdir con la ruta correcta
    mock_getsize.assert_called_once_with(download_inventory.DOWNLOAD_FILE_PATH) # Verificar que se llamó a os.path.getsize con la ruta correcta
    mock_makedirs.assert_has_calls([
        call(download_inventory.DOWNLOAD_DIR, exist_ok=True),
        call(download_inventory.SCREENSHOT_DIR, exist_ok=True)
    ])

def test_download_inventory_login_failure(mock_selenium_components, mock_env_vars, mock_os_functions, mock_file_operations):
    mock_driver, mock_chrome, mock_webdriver_wait = mock_selenium_components
    mock_makedirs, mock_exists, mock_listdir, mock_getsize = mock_os_functions
    mock_open = mock_file_operations

    # Arrange
    # Simular que el login falla (ej. TimeoutException al esperar el URL de login)
    mock_webdriver_wait.return_value.until.side_effect = [
        MagicMock(), # _username
        MagicMock(), # _password
        MagicMock(), # _csrf_token
        TimeoutException("Timeout while verifying login URL") # Simular fallo en la espera del URL
    ]

    # Act
    download_inventory_process()

    # Assert
    mock_chrome.assert_called_once()
    
    # Verificar las llamadas a driver.get
    expected_gets = [
        call("https://plus.21onlinemx.com/login2")
    ]
    mock_driver.get.assert_has_calls(expected_gets)

    mock_driver.quit.assert_called_once() # El navegador debe cerrarse incluso si falla el login
    mock_exists.assert_not_called() # No se debe llegar a verificar el archivo si el login falla
    mock_listdir.assert_not_called()
    mock_getsize.assert_not_called()
    mock_makedirs.assert_has_calls([
        call(download_inventory.DOWNLOAD_DIR, exist_ok=True),
        call(download_inventory.SCREENSHOT_DIR, exist_ok=True)
    ])

def test_download_inventory_no_credentials(mock_selenium_components, mock_os_functions, mock_file_operations):
    mock_driver, mock_chrome, mock_webdriver_wait = mock_selenium_components
    mock_makedirs, mock_exists, mock_listdir, mock_getsize = mock_os_functions
    mock_open = mock_file_operations

    # Arrange: No mockear las variables de entorno para simular que no existen
    with patch.dict(os.environ, clear=True):
        # Act
        download_inventory_process()

        # Assert
        mock_chrome.assert_not_called() # No se debe intentar iniciar el navegador
        mock_makedirs.assert_not_called()
        mock_exists.assert_not_called()
        mock_listdir.assert_not_called()
        mock_getsize.assert_not_called()