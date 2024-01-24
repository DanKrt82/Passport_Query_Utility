"""
Automates checking for available appointments on the Italian police website for 
passport appointments. Uses Selenium for web scraping, logs the process, and 
alerts with a beep sound when an appointment is available.
"""

import time
import logging
import argparse
import winsound
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Configure logging to track script execution
logging.basicConfig(format='%(asctime)s [%(module)s][%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

# Initialize the logger
LOGGER = logging.getLogger("main")

# URL of the website to be scraped
URL = ('https://passaportonline.poliziadistato.it/cittadino/a/sc/'
       'wizardAppuntamentoCittadino/sceltaSede')

def main(cookie_value):
    """
    Main function to initialize the WebDriver, load the webpage, and check for available
    appointments.
    :param cookie_value: The value of the JSESSIONID cookie for authentication.
    """
    try:
        # Initialize the Edge WebDriver
        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service)
        LOGGER.info("Edge WebDriver successfully started.")

        while True: 
            # Load the webpage
            driver.get(URL)
            LOGGER.info("Page loaded: %s", URL)

            # Set a specific cookie required for the session
            cookie = {'name': 'JSESSIONID', 'value': cookie_value}
            driver.add_cookie(cookie)
            LOGGER.info("Cookie set successfully.")
            driver.refresh()

            # Wait for the presence of a table on the page
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            LOGGER.info("Table found on the page.")

            # Iterate through all tables and their rows to find available appointments
            tables = driver.find_elements(By.TAG_NAME, "table")
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) > 1:
                        cell_text = cells[1].text
                        # Check if the cell text indicates availability
                        if "non offre al momento" not in cell_text.lower():
                            # Sound alert and log if availability is found
                            winsound.Beep(440, 500)
                            LOGGER.info("Availability found: %s", cell_text)
                            time.sleep(40000)

            # Wait for 30 seconds before reloading the page
            time.sleep(30)

    except Exception:
        # Log any errors that occur
        LOGGER.error("An error occurred: ", exc_info=True)
        raise
    finally:
        # Quit the WebDriver and log the closure
        driver.quit()
        LOGGER.info("WebDriver closed.")

if __name__ == '__main__':
    # Parse command line arguments for the cookie value
    parser = argparse.ArgumentParser(
        description="Check for available appointments on the Italian police website."
    )
    parser.add_argument("cookie_value", 
                        help="The value of the JSESSIONID cookie for authentication.")
    args = parser.parse_args()

    # Record the execution time and run the main function
    start_time = time.time()
    main(args.cookie_value)
    elapsed_time = time.time() - start_time
    LOGGER.info("Total execution time: %.2f seconds", elapsed_time)
