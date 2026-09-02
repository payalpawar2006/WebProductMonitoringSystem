from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import BASE_URL, ELEMENT_TIMEOUT, MAX_RETRIES
from database import Database
from monitor import check_product_change
from logger import log_info, log_error

from datetime import datetime

import time
import os


# ==========================================
# SCREENSHOT FUNCTION
# ==========================================

def take_error_screenshot(driver):

    os.makedirs("screenshots", exist_ok=True)

    filename = datetime.now().strftime(
        "screenshots/error_%Y%m%d_%H%M%S.png"
    )

    driver.save_screenshot(filename)

    print("Screenshot saved:", filename)

    log_error(f"Screenshot saved: {filename}")


# ==========================================
# BROWSER SETUP
# ==========================================

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)


# ==========================================
# DATABASE
# ==========================================

database = Database()


# ==========================================
# DUPLICATE PREVENTION
# ==========================================

scraped_urls = set()


try:

    print("\n==========================================")
    print("     WEB PRODUCT MONITORING SYSTEM")
    print("==========================================")

    log_info("Monitoring system started.")

    print("\nOpening website...")

    driver.get(BASE_URL)

    log_info(f"Website opened: {BASE_URL}")

    wait = WebDriverWait(driver, ELEMENT_TIMEOUT)


    # ==========================================
    # PAGINATION
    # ==========================================

    page_number = 1

    while True:

        print(f"\n========== PAGE {page_number} ==========")

        log_info(f"Scraping page {page_number}")


        # ==========================================
        # WAIT FOR PRODUCTS
        # ==========================================

        products = wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.CSS_SELECTOR,
                    "article.product_pod"
                )
            )
        )

        print(f"Products found: {len(products)}")


        # ==========================================
        # SCRAPE EACH PRODUCT
        # ==========================================

        for number, product in enumerate(products, start=1):

            success = False


            # ==========================================
            # RETRY SYSTEM
            # ==========================================

            for attempt in range(1, MAX_RETRIES + 1):

                try:

                    print(
                        f"\nProduct {number} - Attempt {attempt}"
                    )


                    # ==========================================
                    # PRODUCT NAME
                    # ==========================================

                    name = product.find_element(
                        By.CSS_SELECTOR,
                        "h3 a"
                    ).get_attribute("title")


                    # ==========================================
                    # PRICE
                    # ==========================================

                    price_text = product.find_element(
                        By.CSS_SELECTOR,
                        ".price_color"
                    ).text

                    price = float(
                        price_text
                        .replace("£", "")
                        .strip()
                    )


                    # ==========================================
                    # AVAILABILITY
                    # ==========================================

                    availability = product.find_element(
                        By.CSS_SELECTOR,
                        ".availability"
                    ).text.strip()


                    # ==========================================
                    # RATING
                    # ==========================================

                    rating = product.find_element(
                        By.CSS_SELECTOR,
                        "p.star-rating"
                    ).get_attribute("class")


                    # ==========================================
                    # PRODUCT URL
                    # ==========================================

                    url = product.find_element(
                        By.CSS_SELECTOR,
                        "h3 a"
                    ).get_attribute("href")


                    # ==========================================
                    # DUPLICATE CHECK
                    # ==========================================

                    if url in scraped_urls:

                        print(
                            f"Duplicate skipped: {name}"
                        )

                        success = True

                        break


                    scraped_urls.add(url)


                    # ==========================================
                    # CHECK PRODUCT CHANGE
                    # ==========================================

                    change = check_product_change(
                        database,
                        name,
                        price,
                        availability,
                        url
                    )


                    # ==========================================
                    # DISPLAY PRODUCT
                    # ==========================================

                    print("\nProduct Details")
                    print("-----------------------------")

                    print("Name:", name)
                    print("Price:", price)
                    print("Availability:", availability)
                    print("Rating:", rating)
                    print("URL:", url)
                    print("Status:", change)


                    # ==========================================
                    # TIMESTAMP
                    # ==========================================

                    scraped_at = datetime.now().isoformat()


                    # ==========================================
                    # SAVE SNAPSHOT
                    # ==========================================

                    database.insert_product(
                        name,
                        price,
                        availability,
                        rating,
                        url,
                        scraped_at
                    )


                    # ==========================================
                    # LOG PRODUCT
                    # ==========================================

                    log_info(
                        f"Product: {name} | "
                        f"Price: {price} | "
                        f"Availability: {availability} | "
                        f"Status: {change}"
                    )


                    # ==========================================
                    # SUCCESS
                    # ==========================================

                    success = True

                    break


                except Exception as error:

                    print(
                        f"Attempt {attempt} failed: {error}"
                    )

                    log_error(
                        f"Product {number} "
                        f"Attempt {attempt} failed: {error}"
                    )


                    # ==========================================
                    # MAX RETRIES
                    # ==========================================

                    if attempt == MAX_RETRIES:

                        print(
                            "\nMaximum retries reached."
                        )

                        log_error(
                            f"Product {number} failed "
                            f"after {MAX_RETRIES} attempts."
                        )


                        # ==========================================
                        # SCREENSHOT
                        # ==========================================

                        take_error_screenshot(driver)


                    else:

                        print("Retrying...")

                        time.sleep(1)


        # ==========================================
        # FIND NEXT BUTTON
        # ==========================================

        next_buttons = driver.find_elements(
            By.CSS_SELECTOR,
            "li.next a"
        )


        # ==========================================
        # NO NEXT PAGE
        # ==========================================

        if not next_buttons:

            print("\nNo more pages.")

            log_info("No more pages found.")

            break


        # ==========================================
        # NEXT PAGE
        # ==========================================

        print("Moving to next page...")

        log_info(
            f"Moving from page {page_number} "
            f"to next page."
        )

        next_buttons[0].click()

        time.sleep(1)

        page_number += 1


    # ==========================================
    # COMPLETED
    # ==========================================

    print("\n==========================================")
    print("SCRAPING & MONITORING COMPLETED!")
    print(
        f"Total unique products: {len(scraped_urls)}"
    )
    print("Data saved in: data/products.db")
    print("Log saved in: logs/monitor.log")
    print("==========================================")


    log_info(
        f"Monitoring completed. "
        f"Total unique products: {len(scraped_urls)}"
    )


    input("\nPress Enter to close browser...")


# ==========================================
# CLEANUP
# ==========================================

finally:

    database.close()

    driver.quit()

    log_info("Browser and database closed.")