import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# --- CONFIGURATION ---
# URLs
LOGIN_URL = 'https://plus.21onlinemx.com/login2'
PROPERTIES_PAGE_URL = 'https://plus.21onlinemx.com/propiedades'

# File and directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')
DOWNLOAD_FILE_NAME = 'inventario.xls'
DOWNLOAD_FILE_PATH = os.path.join(DOWNLOAD_DIR, DOWNLOAD_FILE_NAME)
SCREENSHOT_DIR = os.path.join(BASE_DIR, 'screenshots')
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Wait times
DEFAULT_WAIT_TIME = 30 # Seconds

# --- LOGGING CONFIGURATION ---
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, f"script_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
    ]
)

# Configure StreamHandler for console with a concise format
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# --- AUXILIARY FUNCTIONS ---
def save_screenshot_with_timestamp(driver, name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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

def main():
    # Create directories if they don't exist
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # Credentials will be read from environment variables for security
    USERNAME = os.environ.get('C21_USERNAME')
    PASSWORD = os.environ.get('C21_PSW')

    logger.info(f"Script reading C21_USERNAME: {USERNAME}")
    logger.info(f"Script reading C21_PSW: {'*' * len(PASSWORD) if PASSWORD else 'None'}")

    if not USERNAME or not PASSWORD:
        logger.error("X Error: C21_USERNAME and C21_PSW environment variables are not configured.")
        logger.error("Please configure them before running the script.")
        exit(1)

    driver = None # Initialize driver to None to ensure it closes in case of error

    try:
        driver = setup_webdriver(DOWNLOAD_DIR)

        logger.info("1. Initializing browser and navigating to login page...")
        driver.get(LOGIN_URL)
        save_screenshot_with_timestamp(driver, "1_initial_login_page")
        logger.info(f"Current URL: {driver.current_url}")

        logger.info("Waiting for login fields to be visible...")
        # Wait for login form fields to be present and visible
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

        # Fill the form
        username_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)

        # Get CSRF token from Selenium
        csrf_token = csrf_token_input.get_attribute('value')
        logger.info(f"CSRF Token obtained by Selenium: {csrf_token}")

        login_form = driver.find_element(By.ID, 'kt_login_signin_form') # Ensure this ID is correct
        logger.info("Submitting login form...")
        login_form.submit()
        save_screenshot_with_timestamp(driver, "2_after_login_submit")

        logger.info(f"URL after form submission: {driver.current_url}")

        # Wait for successful login (properties page URL or root URL)
        logger.info("Waiting for URL to be properties page or root after login...")
        try:
            WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
                EC.any_of(
                    EC.url_contains(PROPERTIES_PAGE_URL),
                    EC.url_to_be('https://plus.21onlinemx.com/')
                )
            )
            logger.info("Successful login URL condition met.")
        except TimeoutException:
            logger.error(f"X Timeout while verifying login URL. Current URL: {driver.current_url}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = os.path.join(SCREENSHOT_DIR, f"{timestamp}_login_failed_page_source.html")
            logger.error(f"Saving page content after login attempt to '{html_filename}'...")
            with open(html_filename, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            exit(1)

        # After waiting, explicitly verify the URL to confirm final status
        if driver.current_url.startswith(PROPERTIES_PAGE_URL) or driver.current_url == 'https://plus.21onlinemx.com/':
            logger.info("Login successful with Selenium. Redirected to: " + driver.current_url)
            logger.info("Final URL verification successful. Proceeding with navigation to properties.")
        else:
            logger.error(f"X Final URL does not match successful login expectations: {driver.current_url}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = os.path.join(SCREENSHOT_DIR, f"{timestamp}_unexpected_post_login_page_source.html")
            logger.error(f"Saving unexpected page content to '{html_filename}'...")
            with open(html_filename, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            exit(1)

        logger.info("2. Navigating to properties page...")
        save_screenshot_with_timestamp(driver, "3_before_properties_navigation")
        driver.get(PROPERTIES_PAGE_URL)
        save_screenshot_with_timestamp(driver, "4_after_properties_navigation")
        logger.info(f"Current URL after navigating to properties: {driver.current_url}")

        # Wait for the main download button to be visible and click it
        download_button_xpath = "//button[@type='button' and contains(@class, 'btn-seguimiento') and contains(., 'Descargar o Imprimir Inventario')]"
        logger.info("Waiting for the main download button to be clickable...")
        download_button = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, download_button_xpath))
        )
        save_screenshot_with_timestamp(driver, "5_before_main_download_button_click")
        logger.info("Main 'Download or Print Inventory' button found. Clicking...")
        download_button.click()
        save_screenshot_with_timestamp(driver, "6_after_main_download_button_click")

        logger.info("Waiting for the download submenu to appear...")
        # Assuming the 'Descargar Inventario' option is in an element with specific text
        # and is clickable once the submenu appears.
        # It could be an <a>, <button>, or <li> within a menu.
        # Adjust this XPath if it doesn't work on your site.
        download_option_xpath = "//a[contains(., 'Descargar Inventario')] | //button[contains(., 'Descargar Inventario')] | //li[contains(., 'Descargar Inventario')]"
        download_option = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, download_option_xpath))
        )
        save_screenshot_with_timestamp(driver, "7_before_submenu_download_click")
        logger.info("Submenu 'Download Inventory' option found. Clicking...")
        download_option.click()
        save_screenshot_with_timestamp(driver, "8_after_submenu_download_click")

        logger.info("Waiting a moment for the download to start...")
        time.sleep(15) # Increased wait time for download

        # List content of download directory for debugging
        logger.info(f"Listing contents of download directory: {DOWNLOAD_DIR}")
        downloaded_files = os.listdir(DOWNLOAD_DIR)
        for f in downloaded_files:
            logger.info(f"  - {f}")

        # Verify if the file was downloaded
        logger.info(f"Verifying if the file was downloaded to: {DOWNLOAD_FILE_PATH}")
        if os.path.exists(DOWNLOAD_FILE_PATH):
            file_size_kb = round(os.path.getsize(DOWNLOAD_FILE_PATH) / 1024, 1)
            logger.info(f"✅ Inventory downloaded successfully: {DOWNLOAD_FILE_PATH} ({file_size_kb} KB)")
        else:
            logger.error("X 'inventory.xls' was not generated.")
            logger.error("Verify Selenium download configuration and if the button truly initiates a direct download.")
            logger.error("You can also check the browser console in non-headless mode for download errors.")
            exit(1)

    except TimeoutException as e:
        logger.error(f"X Timeout Error: {e}")
        logger.error("An element was not found or a page did not load in time.")
        exit(1)
    except WebDriverException as e:
        logger.error(f"X WebDriver Error: {e}")
        logger.error("Ensure the browser driver (ChromeDriver/GeckoDriver) is installed and in your PATH.")
        exit(1)
    except Exception as e:
        logger.error(f"X An unexpected error occurred: {e}")
        exit(1)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
