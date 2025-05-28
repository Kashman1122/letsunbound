# import json
# import time
# from typing import List, Dict
#
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
#
#
# def setup_webdriver() -> webdriver.Chrome:
#     """
#     Set up and configure Chrome WebDriver with robust options.
#
#     Returns:
#         Configured Chrome WebDriver instance
#     """
#     chrome_options = Options()
#     # Headless mode options
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#
#     # Additional options to improve reliability
#     chrome_options.add_argument("--remote-debugging-port=9222")
#     chrome_options.add_argument("--window-size=1920,1080")
#
#     # Try multiple methods to initialize WebDriver
#     try:
#         # Attempt to use WebDriver Manager for automatic driver management
#         from webdriver_manager.chrome import ChromeDriverManager
#         from selenium.webdriver.chrome.service import Service
#
#         service = Service(ChromeDriverManager().install())
#         driver = webdriver.Chrome(service=service, options=chrome_options)
#     except ImportError:
#         # Fallback to default ChromeDriver if WebDriver Manager is not installed
#         driver = webdriver.Chrome(options=chrome_options)
#
#     return driver
#
#
# def extract_detail_text(college, base_class: str, index: int = 0) -> str:
#     """
#     Safely extract text from elements with a specific class.
#
#     Args:
#         college: Selenium WebElement representing a college card
#         base_class: Base CSS class to find elements
#         index: Index of the element to extract (default 0)
#
#     Returns:
#         Extracted text or empty string if not found
#     """
#     try:
#         details = college.find_elements(By.CLASS_NAME, base_class)
#         return details[index].text if details else ""
#     except (IndexError, NoSuchElementException):
#         return ""
#
#
# def scrape_college_data(url: str) -> List[Dict[str, str]]:
#     """
#     Scrape comprehensive college data from the specified URL.
#
#     Args:
#         url (str): The URL to scrape college data from
#
#     Returns:
#         List of dictionaries containing detailed college information
#     """
#     # Initialize WebDriver
#     driver = setup_webdriver()
#     college_data = []
#
#     try:
#         # Navigate to the URL with explicit wait
#         driver.get(url)
#
#         # Wait for college cards to load (up to 20 seconds)
#         wait = WebDriverWait(driver, 2000)
#         wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cs-college-card-details")))
#
#         # Find and click "See More" button to load additional colleges
#         while True:
#             try:
#                 see_more_button = driver.find_element(By.CLASS_NAME, "cb-btn-black")
#                 see_more_button.click()
#                 time.sleep(2)  # Wait for new colleges to load
#             except (NoSuchElementException, WebDriverException):
#                 break  # No more "See More" button or error, exit loop
#
#         # Find all college cards
#         colleges = driver.find_elements(By.CLASS_NAME, "cs-college-card-details")
#
#         # Extract data from each college card
#         for college in colleges:
#             try:
#                 # Basic college information
#                 name = college.find_element(By.CLASS_NAME, "cs-college-card-college-name").text
#                 address = college.find_element(By.CLASS_NAME, "cs-college-card-college-address").text
#
#                 # Additional detailed information using new class selectors
#                 details_rows = college.find_elements(By.CLASS_NAME, "cs-college-card-details-row")
#
#                 # Profile info extraction
#                 profile_details = college.find_elements(By.CLASS_NAME, "cb-no-padding")
#                 profile_texts = college.find_elements(By.CLASS_NAME,
#                                                       "cb-no-padding.cs-college-card-details-profile-info-text")
#
#                 # Graduation rate and average cost
#                 graduation_rate = extract_detail_text(college, "cb-roboto-medium", 0)
#                 average_cost = extract_detail_text(college, "cb-roboto-medium", 1)
#
#                 college_data.append({
#                     "college_name": name,
#                     "address": address,
#                     "details": [detail.text for detail in details_rows],
#                     "profile_details": [detail.text for detail in profile_details],
#                     "profile_texts": [text.text for text in profile_texts],
#                     "graduation_rate": graduation_rate,
#                     "average_cost": average_cost
#                 })
#             except NoSuchElementException as e:
#                 print(f"Could not extract details for a college card: {e}")
#
#         return college_data
#
#     except TimeoutException:
#         print("Timeout: Page took too long to load")
#         return []
#     except WebDriverException as e:
#         print(f"WebDriver error occurred: {e}")
#         return []
#     finally:
#         # Always ensure the driver is closed
#         driver.quit()
#
#
# def save_to_json(data: List[Dict[str, str]], filename: str = "colleges.json"):
#     """
#     Save college data to a JSON file.
#
#     Args:
#         data (List[Dict]): List of college dictionaries
#         filename (str): Output JSON filename
#     """
#     try:
#         with open(filename, "w", encoding="utf-8") as f:
#             json.dump(data, f, indent=4, ensure_ascii=False)
#         print(f"Data successfully saved to {filename}")
#     except IOError as e:
#         print(f"Error saving data to JSON: {e}")
#
#
# def main():
#     """
#     Main function to orchestrate web scraping process.
#     """
#     url = "https://bigfuture.collegeboard.org/college-search/"
#
#     try:
#         # Scrape college data
#         colleges = scrape_college_data(url)
#
#         # Save to JSON if data was collected
#         if colleges:
#             save_to_json(colleges)
#         else:
#             print("No college data was scraped.")
#
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#
#
# if __name__ == "__main__":
#     main()


# import json
# import time
# from typing import List, Dict
#
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import (
#     TimeoutException,
#     NoSuchElementException,
#     WebDriverException,
#     ElementClickInterceptedException,
#     StaleElementReferenceException
# )
# from selenium.webdriver.remote.webelement import WebElement
#
#
# def setup_webdriver() -> webdriver.Chrome:
#     """
#     Set up and configure Chrome WebDriver with robust options.
#     """
#     chrome_options = Options()
#     # Disable headless to help with potential rendering issues
#     # chrome_options.add_argument("--headless")  # Uncomment if needed
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--remote-debugging-port=9222")
#     chrome_options.add_argument("--window-size=1920,1200")
#
#     # Additional options to improve stability
#     chrome_options.add_argument("--disable-extensions")
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     chrome_options.add_experimental_option('useAutomationExtension', False)
#
#     try:
#         from webdriver_manager.chrome import ChromeDriverManager
#         from selenium.webdriver.chrome.service import Service
#
#         service = Service(ChromeDriverManager().install())
#         driver = webdriver.Chrome(service=service, options=chrome_options)
#     except ImportError:
#         driver = webdriver.Chrome(options=chrome_options)
#
#     return driver
#
#
# def advanced_click_button(driver: webdriver.Chrome, button_locator: tuple, max_attempts: int = 5) -> bool:
#     """
#     Advanced button clicking method with multiple strategies.
#     """
#     wait = WebDriverWait(driver, 10)
#     attempts = 0
#
#     while attempts < max_attempts:
#         try:
#             # Find button using multiple locator strategies
#             try:
#                 # Try XPath first
#                 button = wait.until(EC.element_to_be_clickable(button_locator))
#             except:
#                 # Fallback to alternative locator
#                 alt_locator = (By.XPATH, "//button[contains(@class, 'cb-btn-black') and contains(text(), 'Show More')]")
#                 button = wait.until(EC.element_to_be_clickable(alt_locator))
#
#             # Remove potential overlays
#             driver.execute_script("""
#                 // Remove potential overlays
#                 var overlays = document.querySelectorAll('.modal, .popup, .overlay');
#                 overlays.forEach(function(overlay) {
#                     overlay.remove();
#                 });
#
#                 // Hide any fixed position elements
#                 var fixedElements = document.querySelectorAll('body > *');
#                 fixedElements.forEach(function(el) {
#                     if (getComputedStyle(el).position === 'fixed') {
#                         el.style.display = 'none';
#                     }
#                 });
#             """)
#
#             # Scroll button into view with more precise scrolling
#             driver.execute_script("""
#                 arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'nearest'});
#             """, button)
#             time.sleep(1)
#
#             # Try multiple click methods
#             try:
#                 # Method 1: JavaScript click
#                 driver.execute_script("arguments[0].click();", button)
#             except Exception as js_err:
#                 try:
#                     # Method 2: Selenium click
#                     button.click()
#                 except Exception as sel_err:
#                     # Method 3: Action chains click
#                     from selenium.webdriver.common.action_chains import ActionChains
#                     ActionChains(driver).move_to_element(button).click().perform()
#
#             # Wait for potential page updates
#             time.sleep(3)
#             return True
#
#         except Exception as e:
#             print(f"Click attempt {attempts + 1} failed: {e}")
#             attempts += 1
#             time.sleep(2)
#
#     print("Failed to click 'Show More' button after multiple attempts.")
#     return False
#
#
# def scrape_college_data(url: str, max_colleges: int = 300) -> List[Dict[str, str]]:
#     """
#     Scrape comprehensive college data with a specific limit.
#     """
#     driver = setup_webdriver()
#     college_data = []
#
#     try:
#         driver.get(url)
#
#         # Wait for initial college cards
#         wait = WebDriverWait(driver, 30)
#         wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cs-college-card-details")))
#
#         # Button locators
#         button_locator = (
#         By.XPATH, "//button[contains(@class, 'cb-btn-black') and contains(text(), 'Show More Colleges')]")
#
#         # Continuous loading with limit
#         while len(college_data) < max_colleges:
#             # Find current colleges
#             colleges = driver.find_elements(By.CLASS_NAME, "cs-college-card-details")
#
#             # Extract data from current batch of colleges
#             for college in colleges[len(college_data):]:
#                 if len(college_data) >= max_colleges:
#                     break
#
#                 try:
#                     name = college.find_element(By.CLASS_NAME, "cs-college-card-college-name").text
#                     address = college.find_element(By.CLASS_NAME, "cs-college-card-college-address").text
#
#                     details_rows = college.find_elements(By.CLASS_NAME, "cs-college-card-details-row")
#                     profile_details = college.find_elements(By.CLASS_NAME, "cb-no-padding")
#                     profile_texts = college.find_elements(By.CLASS_NAME,
#                                                           "cb-no-padding.cs-college-card-details-profile-info-text")
#
#                     graduation_rate = extract_detail_text(college, "cb-roboto-medium", 0)
#                     average_cost = extract_detail_text(college, "cb-roboto-medium", 1)
#
#                     college_data.append({
#                         "college_name": name,
#                         "address": address,
#                         "details": [detail.text for detail in details_rows],
#                         "profile_details": [detail.text for detail in profile_details],
#                         "profile_texts": [text.text for text in profile_texts],
#                         "graduation_rate": graduation_rate,
#                         "average_cost": average_cost
#                     })
#
#                     print(f"Scraped college {len(college_data)}: {name}")
#
#                 except NoSuchElementException as e:
#                     print(f"Could not extract details for a college card: {e}")
#
#             # If we've reached the limit, break
#             if len(college_data) >= max_colleges:
#                 break
#
#             # Try to load more colleges
#             try:
#                 if not advanced_click_button(driver, button_locator):
#                     break
#                 time.sleep(3)
#             except Exception as e:
#                 print(f"Error loading more colleges: {e}")
#                 break
#
#     except Exception as e:
#         print(f"Unexpected error during scraping: {e}")
#     finally:
#         driver.quit()
#
#     return college_data[:max_colleges]
#
#
# def extract_detail_text(college, base_class: str, index: int = 0) -> str:
#     """
#     Safely extract text from elements with a specific class.
#     """
#     try:
#         details = college.find_elements(By.CLASS_NAME, base_class)
#         return details[index].text if details else ""
#     except (IndexError, NoSuchElementException):
#         return ""
#
#
# def save_to_json(data: List[Dict[str, str]], filename: str = "colleges.json"):
#     """
#     Save college data to a JSON file.
#     """
#     try:
#         with open(filename, "w", encoding="utf-8") as f:
#             json.dump(data, f, indent=4, ensure_ascii=False)
#         print(f"Data successfully saved to {filename}")
#     except IOError as e:
#         print(f"Error saving data to JSON: {e}")
#
#
# def main():
#     """
#     Main function to orchestrate web scraping process.
#     """
#     url = "https://bigfuture.collegeboard.org/college-search/filters"
#
#     try:
#         # Scrape 300 college instances
#         colleges = scrape_college_data(url, max_colleges=4322)
#
#         # Save to JSON if data was collected
#         if colleges:
#             save_to_json(colleges)
#             print(f"Total colleges scraped: {len(colleges)}")
#         else:
#             print("No college data was scraped.")
#
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#
#
# if __name__ == "__main__":
#     main()


# import csv
# import time
# import re
# import random
# from typing import Dict, List, Tuple
# import logging
# from urllib3.util.retry import Retry
#
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
#
# # Set up logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("scraper.log"),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger()
#
#
# def setup_webdriver() -> webdriver.Chrome:
#     """
#     Set up and configure Chrome WebDriver with robust options.
#     """
#     chrome_options = Options()
#     # Basic options for stability
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--window-size=1920,1200")
#     chrome_options.add_argument("--disable-extensions")
#
#     # Add more stability options
#     chrome_options.add_argument("--disable-notifications")
#     chrome_options.add_argument("--disable-infobars")
#     chrome_options.add_argument("--disable-popup-blocking")
#     chrome_options.add_argument("--disable-automation")
#
#     # Page crash handling
#     chrome_options.add_argument("--disable-features=NetworkService")
#     chrome_options.add_argument("--disable-features=VizDisplayCompositor")
#
#     # Try alternative approach to creating the driver
#     try:
#         # First try with webdriver_manager
#         try:
#             from webdriver_manager.chrome import ChromeDriverManager
#             from selenium.webdriver.chrome.service import Service
#             service = Service(ChromeDriverManager().install())
#             driver = webdriver.Chrome(service=service, options=chrome_options)
#             return driver
#         except Exception as e:
#             logger.warning(f"Could not create driver with webdriver_manager: {e}")
#
#         # Fall back to creating driver directly
#         driver = webdriver.Chrome(options=chrome_options)
#         return driver
#     except Exception as e:
#         logger.error(f"Failed to create Chrome driver: {e}")
#
#         # As a last resort, try with Edge or Firefox
#         try:
#             logger.info("Trying Microsoft Edge WebDriver instead...")
#             from selenium.webdriver.edge.options import Options as EdgeOptions
#             edge_options = EdgeOptions()
#             edge_options.add_argument("--disable-gpu")
#             edge_options.add_argument("--no-sandbox")
#             edge_options.add_argument("--disable-dev-shm-usage")
#             from selenium.webdriver.edge.service import Service as EdgeService
#             try:
#                 from webdriver_manager.microsoft import EdgeChromiumDriverManager
#                 edge_service = EdgeService(EdgeChromiumDriverManager().install())
#                 driver = webdriver.Edge(service=edge_service, options=edge_options)
#             except ImportError:
#                 driver = webdriver.Edge(options=edge_options)
#             return driver
#         except Exception as edge_err:
#             logger.error(f"Edge WebDriver also failed: {edge_err}")
#
#             # Finally try Firefox
#             try:
#                 logger.info("Trying Firefox WebDriver as last resort...")
#                 from selenium.webdriver.firefox.options import Options as FirefoxOptions
#                 firefox_options = FirefoxOptions()
#                 driver = webdriver.Firefox(options=firefox_options)
#                 return driver
#             except Exception as ff_err:
#                 logger.error(f"Firefox WebDriver also failed: {ff_err}")
#                 raise Exception("Could not initialize any WebDriver")
#
#
# def format_university_slug(name: str) -> str:
#     """
#     Format university name for use in URL.
#     Example: "University of Puerto Rico: Aguadilla" -> "university-of-puerto-rico-aguadilla"
#     """
#     # Replace special characters and lowercase
#     slug = name.lower()
#     # Replace colon and other punctuation
#     slug = re.sub(r'[:\-–—,\'"]', ' ', slug)
#     # Replace multiple spaces with single space
#     slug = re.sub(r'\s+', ' ', slug).strip()
#     # Replace spaces with hyphens
#     slug = slug.replace(' ', '-')
#     return slug
#
#
# def read_universities_from_csv(filename: str) -> List[Dict[str, str]]:
#     """
#     Read university data from CSV file.
#     """
#     universities = []
#     try:
#         with open(filename, 'r', encoding='utf-8') as file:
#             reader = csv.DictReader(file)
#             for row in reader:
#                 universities.append(row)
#         return universities
#     except Exception as e:
#         logger.error(f"Error reading CSV file: {e}")
#         return []
#
#
# def extract_college_description(driver: webdriver.Chrome, url: str, max_retries=3) -> Tuple[bool, str]:
#     """
#     Navigate to the college page and extract the description.
#     Includes retry mechanism for reliability.
#     Returns a tuple of (success, description)
#     """
#     retries = 0
#     backoff_time = 2  # Start with 2 seconds
#
#     while retries <= max_retries:
#         try:
#             driver.get(url)
#
#             # Add a random delay between 3-5 seconds to simulate human behavior
#             time.sleep(3 + random.random() * 2)
#
#             # Try multiple approaches to find the description paragraph
#             description = ""
#
#             # Approach 1: Try using the specific class
#             try:
#                 p_element = WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, "p.sc-c14b4e63-5.MrxQm"))
#                 )
#                 description = p_element.text
#                 return True, description
#             except:
#                 pass
#
#             # Approach 2: Try using ID
#             try:
#                 p_element = driver.find_element(By.ID, "more-about-text")
#                 description = p_element.text
#                 return True, description
#             except:
#                 pass
#
#             # Approach 3: Try using data-testid attribute
#             try:
#                 p_element = driver.find_element(By.CSS_SELECTOR, "p[data-testid='more-about-text']")
#                 description = p_element.text
#                 return True, description
#             except:
#                 pass
#
#             # Approach 4: Try finding any paragraph in the overview section
#             try:
#                 # Look for content after Overview heading
#                 overview_section = driver.find_element(By.XPATH, "//h2[text()='Overview']/following::p[1]")
#                 description = overview_section.text
#                 return True, description
#             except:
#                 pass
#
#             # Approach 5: Try to find the longest paragraph on the page
#             try:
#                 p_elements = driver.find_elements(By.TAG_NAME, "p")
#                 if p_elements:
#                     # Find the longest paragraph (likely the description)
#                     longest_p = max(p_elements, key=lambda p: len(p.text) if p.text else 0)
#                     description = longest_p.text
#                     return True, description
#             except:
#                 pass
#
#             return False, "Description not found"
#
#         except WebDriverException as e:
#             logger.warning(f"WebDriver error on attempt {retries + 1}/{max_retries + 1}: {e}")
#             retries += 1
#
#             if retries > max_retries:
#                 return False, f"Error after {max_retries + 1} attempts: {str(e)}"
#
#             # Exponential backoff with jitter
#             sleep_time = backoff_time + (random.random() * 2)
#             logger.info(f"Retrying in {sleep_time:.2f} seconds...")
#             time.sleep(sleep_time)
#             backoff_time *= 2  # Exponential backoff
#
#             # If browser crashed, restart it
#             try:
#                 driver.quit()
#                 logger.info("Restarting WebDriver after crash...")
#                 driver = setup_webdriver()
#             except:
#                 logger.info("Failed to restart driver, will try again")
#
#         except Exception as e:
#             logger.error(f"Unexpected error: {e}")
#             return False, f"Unexpected error: {str(e)}"
#
#     return False, "Maximum retries exceeded"
#
#
# def save_progress(results, output_file, append=False):
#     """
#     Save current progress to CSV file
#     """
#     mode = 'a' if append else 'w'
#     with open(output_file, mode, newline='', encoding='utf-8') as file:
#         fieldnames = ['college_name', 'url', 'success', 'description']
#         writer = csv.DictWriter(file, fieldnames=fieldnames)
#         if not append:
#             writer.writeheader()
#         for result in results:
#             writer.writerow(result)
#
#     logger.info(f"Progress saved to {output_file}")
#
#
# def scrape_university_descriptions(csv_file: str, output_file: str = "university_descriptions.csv", continue_from=None):
#     """
#     Main function to scrape university descriptions from a CSV file.
#     Added capability to continue from a specific university if the process was interrupted.
#     """
#     universities = read_universities_from_csv(csv_file)
#     if not universities:
#         logger.error("No universities found in the CSV file.")
#         return
#
#     # Check if we're continuing from a previous run
#     start_index = 0
#     if continue_from:
#         for i, uni in enumerate(universities):
#             if uni['college_name'] == continue_from:
#                 start_index = i
#                 logger.info(f"Continuing from {continue_from} (index {start_index})")
#                 break
#
#     # Skip universities we've already processed
#     universities = universities[start_index:]
#
#     driver = None
#     results = []
#     checkpoint_interval = 10  # Save progress every 10 universities
#
#     try:
#         driver = setup_webdriver()
#
#         for i, uni in enumerate(universities):
#             college_name = uni['college_name']
#             slug = format_university_slug(college_name)
#             url = f"https://bigfuture.collegeboard.org/colleges/{slug}"
#
#             logger.info(f"Processing ({i + 1}/{len(universities)}): {college_name}")
#             logger.info(f"URL: {url}")
#
#             # Dynamic delay based on position in the list
#             # Add longer delays every 5 requests to avoid detection
#             if i > 0 and i % 5 == 0:
#                 delay = 10 + random.random() * 5  # 10-15 seconds every 5 requests
#                 logger.info(f"Taking a longer break for {delay:.2f} seconds...")
#                 time.sleep(delay)
#             else:
#                 delay = 3 + random.random() * 4  # 3-7 seconds between normal requests
#                 logger.info(f"Waiting for {delay:.2f} seconds...")
#                 time.sleep(delay)
#
#             try:
#                 success, description = extract_college_description(driver, url)
#
#                 result = {
#                     'college_name': college_name,
#                     'url': url,
#                     'success': success,
#                     'description': description
#                 }
#                 results.append(result)
#
#                 # Log results
#                 if success:
#                     logger.info(f"Success: Description found ({len(description)} chars)")
#                     logger.info(f"Description excerpt: {description[:100]}...")
#                 else:
#                     logger.warning(f"Failed: {description}")
#
#                 # Save checkpoint periodically
#                 if (i + 1) % checkpoint_interval == 0:
#                     logger.info(f"Saving checkpoint after processing {i + 1} universities...")
#                     save_progress(results, f"{output_file}.checkpoint", append=(i > checkpoint_interval))
#                     # Clear results to free memory
#                     results = []
#
#             except Exception as e:
#                 logger.error(f"Error processing {college_name}: {e}")
#
#                 # Save what we have so far if there's a major error
#                 if results:
#                     logger.info("Saving progress before attempting to recover...")
#                     save_progress(results, f"{output_file}.emergency", append=True)
#
#                 # Try to recover the session
#                 try:
#                     driver.quit()
#                 except:
#                     pass
#
#                 logger.info("Reinitializing WebDriver...")
#                 time.sleep(10)  # Wait a bit before reinitializing
#                 driver = setup_webdriver()
#
#             logger.info("-" * 80)
#
#         # Write final results to CSV
#         save_progress(results, output_file, append=False)
#         logger.info(f"All results saved to {output_file}")
#
#     except Exception as e:
#         logger.error(f"Critical error during scraping: {e}")
#         # Save emergency backup
#         if results:
#             save_progress(results, f"{output_file}.emergency", append=True)
#     finally:
#         if driver:
#             driver.quit()
#
#
# if __name__ == "__main__":
#     # Example usage
#     csv_file = "university_data.csv"  # Path to your CSV file
#     output_file = "university_descriptions.csv"
#
#     # To continue from a specific university after a crash
#     # scrape_university_descriptions(csv_file, output_file, continue_from="Concord University")
#
#     # To start from the beginning
#     scrape_university_descriptions(csv_file, output_file)
#
#
#
#


import csv
import time
import re
import random
import json
from typing import Dict, List, Tuple, Any
import logging
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("college_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Define the sections to scrape
SECTIONS = [
    {"name": "overview", "path": ""},  # Empty string for base URL
    {"name": "admissions", "path": "/admissions"},
    {"name": "academics", "path": "/academics"},
    {"name": "costs", "path": "/tuition-and-costs"},
    {"name": "campus-life", "path": "/campus-life"}
]


def setup_webdriver() -> webdriver.Chrome:
    """
    Set up and configure Chrome WebDriver with robust options.
    """
    chrome_options = Options()
    # Basic options for stability
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1200")
    chrome_options.add_argument("--disable-extensions")

    # Add more stability options
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-automation")

    # Page crash handling
    chrome_options.add_argument("--disable-features=NetworkService")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")

    # Add a user agent to appear more like a regular browser
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Try alternative approach to creating the driver
    try:
        # First try with webdriver_manager
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            logger.warning(f"Could not create driver with webdriver_manager: {e}")

        # Fall back to creating driver directly
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"Failed to create Chrome driver: {e}")

        # As a last resort, try with Edge or Firefox
        try:
            logger.info("Trying Microsoft Edge WebDriver instead...")
            from selenium.webdriver.edge.options import Options as EdgeOptions
            edge_options = EdgeOptions()
            edge_options.add_argument("--disable-gpu")
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument("--disable-dev-shm-usage")
            from selenium.webdriver.edge.service import Service as EdgeService
            try:
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                edge_service = EdgeService(EdgeChromiumDriverManager().install())
                driver = webdriver.Edge(service=edge_service, options=edge_options)
            except ImportError:
                driver = webdriver.Edge(options=edge_options)
            return driver
        except Exception as edge_err:
            logger.error(f"Edge WebDriver also failed: {edge_err}")

            # Finally try Firefox
            try:
                logger.info("Trying Firefox WebDriver as last resort...")
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                firefox_options = FirefoxOptions()
                driver = webdriver.Firefox(options=firefox_options)
                return driver
            except Exception as ff_err:
                logger.error(f"Firefox WebDriver also failed: {ff_err}")
                raise Exception("Could not initialize any WebDriver")


def format_university_slug(name: str) -> str:
    """
    Format university name for use in URL.
    Example: "University of Puerto Rico: Aguadilla" -> "university-of-puerto-rico-aguadilla"
    """
    # Replace special characters and lowercase
    slug = name.lower()
    # Replace colon and other punctuation
    slug = re.sub(r'[:\-–—,\'"]', ' ', slug)
    # Replace multiple spaces with single space
    slug = re.sub(r'\s+', ' ', slug).strip()
    # Replace spaces with hyphens
    slug = slug.replace(' ', '-')
    # Remove any remaining special characters
    slug = re.sub(r'[^\w\-]', '', slug)
    return slug


def read_universities_from_csv(filename: str) -> List[Dict[str, str]]:
    """
    Read university data from CSV file.
    """
    universities = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                universities.append(row)
        return universities
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return []


def extract_element_text(driver, selector, method=By.CSS_SELECTOR, wait_time=3):
    """
    Attempt to extract text from an element using the provided selector.
    Returns the text if found, empty string otherwise.
    """
    try:
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((method, selector))
        )
        return element.text.strip()
    except:
        return ""


def extract_all_elements_text(driver, selector, method=By.CSS_SELECTOR, wait_time=3):
    """
    Extract text from all elements matching the selector.
    Returns a list of strings.
    """
    try:
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((method, selector))
        )
        elements = driver.find_elements(method, selector)
        return [el.text.strip() for el in elements if el.text.strip()]
    except:
        return []


def extract_key_value_items(driver, list_selector):
    """
    Extract key-value pairs from list items.
    """
    results = {}
    try:
        list_items = driver.find_elements(By.CSS_SELECTOR, list_selector)
        for item in list_items:
            # Try to find the label/key and value elements
            try:
                # Extract text from divs containing the key and value
                # Based on the HTML structure in the screenshots
                label_divs = item.find_elements(By.CSS_SELECTOR, "div[class*='title']")
                value_divs = item.find_elements(By.CSS_SELECTOR, "div[class*='value'], p[class*='value']")

                if label_divs and value_divs:
                    label = label_divs[0].text.strip()
                    value = value_divs[0].text.strip()
                    if label and value:
                        results[label] = value
            except Exception as e:
                continue
    except Exception as e:
        logger.warning(f"Error extracting key-value items: {e}")

    return results


def scrape_overview_section(driver):
    """
    Scrape data from the Overview section using updated selectors
    """
    data = {}

    # Extract college description - try different selectors based on your screenshots
    description_selectors = [
        "p.sc-c14b4e63-5.MrxQm",
        "p[data-testid='more-about-text']",
        ".cb-text-list-no-indent p",
        "div.cb-margin-bottom-32 p"  # From screenshot 3
    ]

    description = ""
    for selector in description_selectors:
        text = extract_element_text(driver, selector)
        if text:
            description = text
            break

    # If all specific selectors failed, try to find longest paragraph
    if not description:
        try:
            p_elements = driver.find_elements(By.TAG_NAME, "p")
            if p_elements:
                # Find the longest paragraph (likely the description)
                longest_p = max(p_elements, key=lambda p: len(p.text) if p.text else 0)
                description = longest_p.text
        except:
            pass

    data["description"] = description

    # Extract enrollment data - based on screenshot 3
    try:
        # Total undergrad students
        undergrad_value = extract_element_text(driver, "p[id*='list-item-total-undergraduates-value']")
        if undergrad_value:
            data["total_undergrad"] = undergrad_value

        # Total graduate students
        grad_value = extract_element_text(driver, "p[id*='list-item-total-graduates-value']")
        if grad_value:
            data["total_grad"] = grad_value

        # Full-time students
        fulltime_value = extract_element_text(driver, "li[id*='list-item-enrollment-2'] p[class*='value']")
        if fulltime_value:
            data["full_time_students"] = fulltime_value

        # Part-time students
        parttime_value = extract_element_text(driver, "li[id*='list-item-enrollment-3'] p[class*='value']")
        if parttime_value:
            data["part_time_students"] = parttime_value
    except Exception as e:
        logger.warning(f"Error extracting enrollment data: {e}")

    # Extract basic college info from various elements
    try:
        # Try to get college_type and location from any available elements
        college_type = extract_element_text(driver, "[data-testid='college-type']")
        if college_type:
            data["college_type"] = college_type

        location = extract_element_text(driver, "[data-testid='college-location']")
        if location:
            data["location"] = location
    except:
        pass

    return data


def scrape_admissions_section(driver):
    """
    Scrape data from the Admissions section
    """
    data = {}

    # Extract application requirements using more generic selectors
    try:
        # Try to find requirements container
        requirements_items = extract_key_value_items(driver, "li[class*='cb-margin-bottom']")
        if requirements_items:
            data.update(requirements_items)

        # More specific selectors for common fields
        for label, xpath_pattern in [
            ("High School GPA", "//span[contains(text(), 'High School GPA')]/following::span[1]"),
            ("High School Rank", "//span[contains(text(), 'High School Rank')]/following::span[1]"),
            ("College Prep Courses", "//span[contains(text(), 'College Prep')]/following::span[1]"),
            ("SAT/ACT Scores", "//span[contains(text(), 'SAT/ACT')]/following::span[1]"),
            ("Recommendations", "//span[contains(text(), 'Recommendations')]/following::span[1]")
        ]:
            value = extract_element_text(driver, xpath_pattern, By.XPATH)
            if value and label not in data:
                data[label] = value
    except Exception as e:
        logger.warning(f"Error extracting admission requirements: {e}")

    # Application deadline
    deadline = extract_element_text(driver, "h2:contains('Application Deadline') + p")
    if deadline:
        data["Application Deadline"] = deadline

    # Application fee
    fee_text = extract_element_text(driver, "h2:contains('Application Fee') + div")
    if fee_text:
        fee_match = re.search(r'\$(\d+)', fee_text)
        if fee_match:
            data["Application Fee"] = fee_match.group(1)
        else:
            data["Application Fee"] = fee_text

    return data


def scrape_academics_section(driver):
    """
    Scrape data from the Academics section using updated selectors
    """
    data = {}

    # Get degrees offered - based on screenshot 1
    try:
        degrees_text = extract_element_text(driver, "div.csp-profile-majors-typehead-list-content-group-title")
        if not degrees_text:
            # Try another approach from your first screenshot
            degrees_text = extract_element_text(driver, "p[class*='csp-profile-majors']")
            if not degrees_text:
                # Try direct XPath approach
                degrees_text = extract_element_text(
                    driver,
                    "//div[contains(text(), 'The college offers the following degrees:')]",
                    By.XPATH
                )

        if degrees_text:
            data["degrees_offered"] = degrees_text.replace("The college offers the following degrees:", "").strip()
    except Exception as e:
        logger.warning(f"Error extracting degrees offered: {e}")

    # Get list of majors - based on screenshot 1
    try:
        # Try different selectors for majors list
        major_selectors = [
            "li[class*='csp-profile-majors-typehead-list-section-list-item']",
            "li[class*='cb-roboto-light csp-profile-majors-typehead-item']",
            "ul[class*='csp-majors-typehead-unordered-list'] li"
        ]

        majors = []
        for selector in major_selectors:
            majors = extract_all_elements_text(driver, selector)
            if majors:
                break

        if not majors:
            # Try more general approach
            major_elements = driver.find_elements(By.CSS_SELECTOR, "li[id*='majors-typehead-list-section-list-item']")
            majors = [el.text.strip() for el in major_elements if el.text.strip()]

        data["majors"] = majors
    except Exception as e:
        logger.warning(f"Error extracting majors: {e}")

    return data


def scrape_costs_section(driver):
    """
    Scrape data from the Costs section using updated selectors from screenshot 2
    """
    data = {}

    # Average Net Price
    try:
        # Try to find the average net price value
        price_selectors = [
            "div.sc-13223bcc-2.klpQhF",  # From screenshot 2
            "span[alt='$6,095']",  # Try alt attribute from screenshot 2
            "//div[contains(text(), 'Average Per Year After Aid')]/following::div[1]",  # XPath approach
        ]

        for selector in price_selectors:
            method = By.CSS_SELECTOR if not selector.startswith("//") else By.XPATH
            price = extract_element_text(driver, selector, method)
            if price:
                data["Average Net Price"] = price
                break

        # If still not found, try looking for the value in the page
        if "Average Net Price" not in data:
            # Try to find it in any element containing dollar amount and "per year"
            elements = driver.find_elements(By.XPATH, "//*[contains(text(), '$') and contains(text(), 'per year')]")
            if elements:
                data["Average Net Price"] = elements[0].text.strip()
    except Exception as e:
        logger.warning(f"Error extracting average net price: {e}")

    # Extract costs from the costs summary section - using ID from screenshot 2
    try:
        cost_items = extract_key_value_items(driver, "#costs-summary-section li")
        if cost_items:
            data.update(cost_items)

        # Try alternate approach using the classes from screenshot 2
        if not cost_items:
            costs = {}
            li_elements = driver.find_elements(By.CSS_SELECTOR, "ul[id='costs-summary-section'] li")
            for li in li_elements:
                try:
                    label_div = li.find_element(By.CSS_SELECTOR, "div.sc-13223bcc-1.kQUFrk")
                    value_div = li.find_element(By.CSS_SELECTOR, "div.sc-13223bcc-2.klpQhF")
                    if label_div and value_div:
                        label = label_div.text.strip()
                        value = value_div.text.strip()
                        if label and value:
                            costs[label] = value
                except:
                    continue
            if costs:
                data.update(costs)
    except Exception as e:
        logger.warning(f"Error extracting costs breakdown: {e}")

    # Financial aid info
    for label, selector in [
        ("Students Receiving Financial Aid",
         "//div[contains(text(), 'Students Receiving Financial Aid')]/following::div[1]"),
        ("Average Aid Package", "//div[contains(text(), 'Average Aid Package')]/following::div[1]"),
        ("Financial Aid Deadline", "//div[contains(text(), 'Financial Aid Application Due')]/following::div[1]")
    ]:
        try:
            value = extract_element_text(driver, selector, By.XPATH)
            if value:
                data[label] = value
        except:
            continue

    return data


def scrape_campus_life_section(driver):
    """
    Scrape data from the Campus Life section
    """
    data = {}

    # Extract campus life data using XPath
    for label, selector in [
        ("On-Campus Housing", "//div[contains(text(), 'On-Campus Housing')]/following::div[1]"),
        ("Freshmen Required to Live on Campus",
         "//div[contains(text(), 'Freshmen Required to Live on Campus')]/following::div[1]"),
        ("Campus Setting", "//div[contains(text(), 'Campus Setting')]/following::div[1]")
    ]:
        try:
            value = extract_element_text(driver, selector, By.XPATH)
            if value:
                data[label] = value
        except:
            continue

    # Activities and student life info
    activities = extract_element_text(
        driver,
        "//h2[contains(text(), 'Student Life')]/following::p[1]",
        By.XPATH
    )
    if activities:
        data["Student Activities"] = activities

    return data


def scrape_college_data(driver: webdriver.Chrome, college_name: str, base_url: str) -> Dict[str, Any]:
    """
    Scrape data for a college from all sections.
    Returns a dictionary with all collected data.
    """
    all_data = {
        "college_name": college_name,
        "url": base_url,
        "scrape_success": True,
        "scrape_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Track successful sections
    successful_sections = []

    # Process each section
    for section in SECTIONS:
        section_name = section["name"]
        section_url = f"{base_url}{section['path']}"

        logger.info(f"Processing {section_name} section at {section_url}")

        try:
            # Navigate to the section
            driver.get(section_url)

            # Random delay between 2-5 seconds
            delay = 2 + random.random() * 3
            time.sleep(delay)

            # Check for popup and close it if needed
            try:
                # Look for "Stay Ahead Stress Free" popup and click "Maybe Later"
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//button[text()='Maybe Later']"))
                ).click()
                logger.info("Closed popup dialog")
            except:
                pass  # No popup found or couldn't close it

            # Scrape based on the section
            section_data = {}
            if section_name == "overview":
                section_data = scrape_overview_section(driver)
            elif section_name == "admissions":
                section_data = scrape_admissions_section(driver)
            elif section_name == "academics":
                section_data = scrape_academics_section(driver)
            elif section_name == "costs":
                section_data = scrape_costs_section(driver)
            elif section_name == "campus-life":
                section_data = scrape_campus_life_section(driver)

            # Add to our overall data
            all_data[section_name] = section_data
            successful_sections.append(section_name)

            logger.info(f"Successfully scraped {section_name} section with {len(section_data)} data points")

        except Exception as e:
            logger.error(f"Error processing {section_name} section: {str(e)}")
            all_data[section_name] = {"error": str(e)}

    # Update success status
    all_data["successful_sections"] = successful_sections
    if not successful_sections:
        all_data["scrape_success"] = False

    return all_data


def flatten_dict_for_csv(data_dict, prefix=''):
    """
    Convert nested dictionary to flat dictionary for CSV output
    """
    flattened = {}
    for key, value in data_dict.items():
        if isinstance(value, dict):
            # Recursively flatten nested dictionaries
            nested_dict = flatten_dict_for_csv(value, f"{prefix}{key}_")
            flattened.update(nested_dict)
        elif isinstance(value, list):
            # Convert lists to comma-separated strings
            if value:
                flattened[f"{prefix}{key}"] = "|".join(str(item) for item in value)
            else:
                flattened[f"{prefix}{key}"] = ""
        else:
            # Regular key-value pair
            flattened[f"{prefix}{key}"] = value
    return flattened


def save_to_csv(results, output_file="college_data.csv"):
    """
    Save all results directly to a single CSV file
    """
    if not results:
        logger.warning("No results to save to CSV")
        return

    try:
        # Flatten the nested dictionaries for CSV
        flattened_results = []
        for college_data in results:
            flat_data = flatten_dict_for_csv(college_data)
            flattened_results.append(flat_data)

        # Get all possible field names
        all_fields = set()
        for row in flattened_results:
            all_fields.update(row.keys())

        # Sort fields for consistent column order
        sorted_fields = sorted(all_fields)

        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted_fields)
            writer.writeheader()
            writer.writerows(flattened_results)

        logger.info(f"Successfully saved {len(flattened_results)} college records to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")
        return False


def scrape_universities(csv_file: str, output_file="college_data.csv", continue_from=None, limit=None):
    """
    Main function to scrape university data and save directly to CSV.
    - csv_file: Path to CSV with university names
    - output_file: Path to output CSV file
    - continue_from: Optional university name to continue from
    - limit: Optional limit on number of universities to process
    """
    universities = read_universities_from_csv(csv_file)
    if not universities:
        logger.error("No universities found in the CSV file.")
        return

    # Check if we're continuing from a previous run
    start_index = 0
    if continue_from:
        for i, uni in enumerate(universities):
            if uni['college_name'] == continue_from:
                start_index = i
                logger.info(f"Continuing from {continue_from} (index {start_index})")
                break

    # Apply limit if specified
    if limit and limit > 0:
        universities = universities[start_index:start_index + limit]
    else:
        universities = universities[start_index:]

    driver = None
    results = []

    # For incremental saving
    checkpoint_interval = 5  # Save progress every 5 universities

    try:
        driver = setup_webdriver()

        for i, uni in enumerate(universities):
            college_name = uni['college_name']
            slug = format_university_slug(college_name)
            base_url = f"https://bigfuture.collegeboard.org/colleges/{slug}"

            logger.info(f"Processing ({i + 1}/{len(universities)}): {college_name}")
            logger.info(f"Base URL: {base_url}")

            # Dynamic delay based on position in the list
            # Add longer delays every 5 requests to avoid detection
            if i > 0 and i % 5 == 0:
                delay = 10 + random.random() * 5  # 10-15 seconds every 5 requests
                logger.info(f"Taking a longer break for {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                delay = 2 + random.random() * 3  # 2-5 seconds between normal requests
                logger.info(f"Waiting for {delay:.2f} seconds...")
                time.sleep(delay)

            try:
                # Scrape all sections for this college
                college_data = scrape_college_data(driver, college_name, base_url)

                # Add to results
                results.append(college_data)

                # Log success or failure
                if college_data["scrape_success"]:
                    logger.info(f"Successfully scraped data for {college_name}")
                    # Log how many sections were successful
                    successful = len(college_data.get("successful_sections", []))
                    logger.info(f"Scraped {successful}/{len(SECTIONS)} sections successfully")
                else:
                    logger.warning(f"Failed to scrape data for {college_name}")

                # Save checkpoint periodically
                if (i + 1) % checkpoint_interval == 0:
                    logger.info(f"Saving checkpoint after processing {i + 1} universities...")
                    temp_csv = f"college_data_checkpoint_{i + 1}.csv"
                    save_to_csv(results, temp_csv)

            except Exception as e:
                logger.error(f"Error processing {college_name}: {e}")

                # Try to recover the session
                try:
                    driver.quit()
                except:
                    pass

                logger.info("Reinitializing WebDriver...")
                time.sleep(10)  # Wait a bit before reinitializing
                driver = setup_webdriver()

            logger.info("-" * 80)

        # Save final results directly to CSV
        logger.info("Saving all results to CSV...")
        save_to_csv(results, output_file)

        logger.info(f"All results saved to {output_file}. Processed {len(results)} universities.")

    except Exception as e:
        logger.error(f"Critical error during scraping: {e}")
        # Try to save what we have
        if results:
            emergency_file = f"emergency_college_data_{int(time.time())}.csv"
            save_to_csv(results, emergency_file)
            logger.info(f"Saved emergency data to {emergency_file}")
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    # Path to your CSV file
    csv_file = "university_data.csv"

    # Output CSV file
    output_file = "college_data_complete.csv"

    # To continue from a specific university after a crash
    # scrape_universities(csv_file, output_file, continue_from="Concord University")

    # To limit the number of universities to process (useful for testing)
    # scrape_universities(csv_file, output_file, limit=5)

    # To start from the beginning and process all universities
    scrape_universities(csv_file, output_file)


#270 university