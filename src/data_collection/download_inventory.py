import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from src.utils.logging_config import setup_logging
from src.utils.constants import LOGIN_URL, PROPERTIES_PAGE_URL

# --- CONFIGURATION ---

# File and directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')
DOWNLOAD_FILE_NAME = 'inventario.xls'
DOWNLOAD_FILE_PATH = os.path.join(DOWNLOAD_DIR, DOWNLOAD_FILE_NAME)
SCREENSHOT_DIR = os.path.join(BASE_DIR, 'screenshots')
LOG_DIR = "logs"  # Added for test patching

# Wait times
DEFAULT_WAIT_TIME = 30 # Seconds

# --- LOGGING CONFIGURATION ---
setup_logging(log_file_prefix="download_inventory_log")
logger = logging.getLogger(__name__)

# --- AUXILIARY FUNCTIONS ---
def save_screenshot(driver, name):
    timestamp = int(time.time())
    filename = os.path.join(SCREENSHOT_DIR, f"{timestamp}_{name}.png")
    driver.save_screenshot(filename)
    logger.info(f"Screenshot saved: {filename}")

def setup_webdriver(download_dir):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # Run in headless mode (no GUI)
    options.add_argument('--start-maximized') # Start browser maximized
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Configure download preferences for Chrome
    prefs = {"download.default_directory" : download_dir,
             "download.prompt_for_download": False,
             "download.directory_upgrade": True,
             "plugins.always_open_pdf_externally": True # To prevent Chrome from opening PDFs in the browser
            }
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=options)

def _perform_login(driver, username, password):
    logger.info("1. Initializing browser and navigating to login page...")
    driver.get(LOGIN_URL)
    save_screenshot(driver, "1_initial_login_page")
    logger.info(f"Current URL: {driver.current_url}")

    logger.info("Waiting for login fields to be visible...")
    username_input = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
        EC.visibility_of_element_located((By.NAME, '_username'))
    )
    password_input = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
        EC.visibility_of_element_located((By.NAME, '_password'))
    )
    csrf_token_input = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
        EC.presence_of_element_located((By.NAME, '_csrf_token'))
    )
    logger.info("Login fields found.")

    username_input.send_keys(username)
    password_input.send_keys(password)

    csrf_token = csrf_token_input.get_attribute('value')
    logger.info(f"CSRF Token obtained by Selenium: {csrf_token}")

    login_form = driver.find_element(By.ID, 'kt_login_signin_form')
    logger.info("Submitting login form...")
    login_form.submit()
    save_screenshot(driver, "2_after_login_submit")
    logger.info(f"URL after form submission: {driver.current_url}")

    try:
        WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
            EC.any_of(
                EC.url_contains(PROPERTIES_PAGE_URL),
                EC.url_to_be('https://plus.21onlinemx.com/')
            )
        )
        logger.info("Successful login URL condition met.")
    except TimeoutException:
        logger.error(f"Timeout while verifying login URL. Current URL: {driver.current_url}")
        html_filename = os.path.join(SCREENSHOT_DIR, f"{int(time.time())}_login_failed_page_source.html")
        logger.error(f"Saving page content after login attempt to '{html_filename}'...")
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        return False
    
    if driver.current_url.startswith(PROPERTIES_PAGE_URL) or driver.current_url == 'https://plus.21onlinemx.com/':
        logger.info("Login successful with Selenium. Redirected to: " + driver.current_url)
        logger.info("Final URL verification successful. Proceeding with navigation to properties.")
        return True
    else:
        logger.error(f"Final URL does not match successful login expectations: {driver.current_url}")
        html_filename = os.path.join(SCREENSHOT_DIR, f"{int(time.time())}_unexpected_post_login_page_source.html")
        logger.error(f"Saving unexpected page content to '{html_filename}'...")
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        return False

def _navigate_to_properties_page(driver):
    logger.info("2. Navigating to properties page...")
    save_screenshot(driver, "3_before_properties_navigation")
    driver.get(PROPERTIES_PAGE_URL)
    save_screenshot(driver, "4_after_properties_navigation")
    logger.info(f"Current URL after navigating to properties: {driver.current_url}")
    return True

def _initiate_download(driver):
    download_button_xpath = "//button[@type='button' and contains(@class, 'btn-seguimiento') and contains(., 'Descargar o Imprimir Inventario')]"
    logger.info("Waiting for the main download button to be clickable...")
    download_button = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
        EC.element_to_be_clickable((By.XPATH, download_button_xpath))
    )
    save_screenshot(driver, "5_before_main_download_button_click")
    logger.info("Main 'Download or Print Inventory' button found. Clicking...")
    download_button.click()
    save_screenshot(driver, "6_after_main_download_button_click")

    logger.info("Waiting for the download submenu to appear...")
    download_option_xpath = "//a[contains(., 'Descargar Inventario')] | //button[contains(., 'Descargar Inventario')] | //li[contains(., 'Descargar Inventario')]"
    download_option = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
        EC.element_to_be_clickable((By.XPATH, download_option_xpath))
    )
    save_screenshot(driver, "7_before_submenu_download_click")
    logger.info("Submenu 'Download Inventory' option found. Clicking...")
    download_option.click()
    save_screenshot(driver, "8_after_submenu_download_click")

    logger.info("Waiting a moment for the download to start...")
    time.sleep(15)
    return True

def download_inventory_process():
    USERNAME = os.environ.get('C21_USERNAME')
    PASSWORD = os.environ.get('C21_PSW')

    logger.info(f"Script reading C21_USERNAME: {USERNAME}")
    logger.info(f"Script reading C21_PSW: {'*' * len(PASSWORD) if PASSWORD else 'None'}")

    if not USERNAME or not PASSWORD:
        logger.error("X Error: C21_USERNAME and C21_PSW environment variables are not configured.")
        logger.error("Please configure them before running the script.")
        return False

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    driver = None

    try:
        driver = setup_webdriver(DOWNLOAD_DIR)

        if not _perform_login(driver, USERNAME, PASSWORD):
            return False
        
        if not _navigate_to_properties_page(driver):
            return False

        if not _initiate_download(driver):
            return False

        logger.info(f"Listing contents of download directory: {DOWNLOAD_DIR}")
        downloaded_files = os.listdir(DOWNLOAD_DIR)
        for f in downloaded_files:
            logger.info(f"  - {f}")

        logger.info(f"Verifying if the file was downloaded to: {DOWNLOAD_FILE_PATH}")
        if os.path.exists(DOWNLOAD_FILE_PATH):
            file_size_kb = round(os.path.getsize(DOWNLOAD_FILE_PATH) / 1024, 1)
            logger.info(f"✅ Inventory downloaded successfully: {DOWNLOAD_FILE_PATH} ({file_size_kb} KB)")
            return True
        else:
            logger.error("X 'inventory.xls' was not generated.")
            logger.error("Verify Selenium download configuration and if the button truly initiates a direct download.")
            logger.error("You can also check the browser console in non-headless mode for download errors.")
            return False

    except TimeoutException as e:
        logger.error(f"X Timeout Error: {e}")
        logger.error("An element was not found or a page did not load in time.")
        return False
    except WebDriverException as e:
        logger.error(f"X WebDriver Error: {e}")
        logger.error("Ensure the browser driver (ChromeDriver/GeckoDriver) is installed and in your PATH.")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return False
    finally:
        if driver:
            driver.quit()

def main():
    download_inventory_process()

if __name__ == "__main__":
    main()
