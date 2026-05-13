# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time

# # Reel URL
# url = "https://www.instagram.com/gozoop/p/DYMs0DUAipj/"

# # Chrome options
# options = Options()
# options.add_argument("--start-maximized")
# options.add_argument("--disable-blink-features=AutomationControlled")

# # Start browser
# driver = webdriver.Chrome(options=options)

# try:
#     # Open page
#     driver.get(url)

#     # Wait until elements load
#     wait = WebDriverWait(driver, 20)

#     wait.until(
#         EC.presence_of_all_elements_located(
#             (By.CLASS_NAME, "xe9ewy2")
#         )
#     )

#     # Small extra wait
#     time.sleep(3)

#     # Get all elements
#     elements = driver.find_elements(By.CLASS_NAME, "xe9ewy2")

#     values = []

#     for el in elements:
#         text = el.text.strip()

#         if text:
#             values.append(text)

#     print("\nFound Values:")
#     print(values)

#     # First = likes
#     # Second = comments
#     if len(values) >= 2:
#         likes = values[0]
#         comments = values[1]

#         print("\n====================")
#         print("Likes    :", likes)
#         print("Comments :", comments)
#         print("====================")
#     else:
#         print("Could not find enough values")

# except Exception as e:
#     print("Error:", e)

# finally:
#     driver.quit()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Instagram URL
url = "https://www.instagram.com/reel/DXBB07DjAtr/"

# Chrome options
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

# Start browser
driver = webdriver.Chrome(options=options)

try:
    # Open page
    driver.get(url)

    # Wait for page load
    wait = WebDriverWait(driver, 20)

    # Wait for likes/comments elements
    wait.until(
        EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "xe9ewy2")
        )
    )

    time.sleep(3)

    # =========================
    # GET LIKES & COMMENTS
    # =========================

    elements = driver.find_elements(By.CLASS_NAME, "xe9ewy2")

    values = []

    for el in elements:
        text = el.text.strip()

        if text:
            values.append(text)

    likes = values[0] if len(values) > 0 else "Not Found"
    comments = values[1] if len(values) > 1 else "Not Found"

    # =========================
    # GET POST DATE
    # =========================

    try:
        # Get time tag
        time_element = driver.find_element(By.TAG_NAME, "time")

        # Visible date
        post_date = time_element.text.strip()

        # ISO datetime
        datetime_value = time_element.get_attribute("datetime")

    except Exception:
        post_date = "Not Found"
        datetime_value = "Not Found"

    # =========================
    # PRINT DATA
    # =========================

    print("\n====================")
    print("Likes       :", likes)
    print("Comments    :", comments)
    print("Post Date   :", post_date)
    print("DateTime    :", datetime_value)
    print("====================")

except Exception as e:
    print("Error:", e)

finally:
    driver.quit()