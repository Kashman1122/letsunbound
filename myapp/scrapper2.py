# # import csv
# # import time
# # import re
# # import random
# # import logging
# # from typing import Dict, List, Any
# # import os
# #
# # from selenium import webdriver
# # from selenium.webdriver.chrome.options import Options
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC
# # from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
# #
# # # Set up logging
# # logging.basicConfig(
# #     level=logging.INFO,
# #     format='%(asctime)s - %(levelname)s - %(message)s',
# #     handlers=[
# #         logging.StreamHandler()  # Only use stream handler for Kaggle
# #     ]
# # )
# # logger = logging.getLogger()
# #
# #
# # def setup_webdriver() -> webdriver.Chrome:
# #     """
# #     Set up and configure Chrome WebDriver for Kaggle environment
# #     """
# #     chrome_options = Options()
# #     # Headless mode is required for Kaggle
# #     chrome_options.add_argument("--headless")
# #     chrome_options.add_argument("--disable-gpu")
# #     chrome_options.add_argument("--no-sandbox")
# #     chrome_options.add_argument("--disable-dev-shm-usage")
# #     chrome_options.add_argument("--window-size=1920,1200")
# #
# #     # Add stability options
# #     chrome_options.add_argument("--disable-extensions")
# #     chrome_options.add_argument("--disable-notifications")
# #     chrome_options.add_argument("--disable-infobars")
# #
# #     # Add user agent
# #     chrome_options.add_argument(
# #         "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
# #
# #     try:
# #         # For Kaggle, we'll use the basic driver initialization
# #         driver = webdriver.Chrome(options=chrome_options)
# #         return driver
# #     except Exception as e:
# #         logger.error(f"Failed to create Chrome driver: {e}")
# #         raise
# #
# #
# # def format_university_slug(name: str) -> str:
# #     """
# #     Format university name for use in URL.
# #     Example: "University of Puerto Rico: Aguadilla" -> "university-of-puerto-rico-aguadilla"
# #     """
# #     # Replace special characters and lowercase
# #     slug = name.lower()
# #     # Replace colon and other punctuation
# #     slug = re.sub(r'[:\-–—,\'"]', ' ', slug)
# #     # Replace multiple spaces with single space
# #     slug = re.sub(r'\s+', ' ', slug).strip()
# #     # Replace spaces with hyphens
# #     slug = slug.replace(' ', '-')
# #     # Remove any remaining special characters
# #     slug = re.sub(r'[^\w\-]', '', slug)
# #     return slug
# #
# #
# # def read_universities_from_csv(filename: str) -> List[Dict[str, str]]:
# #     """
# #     Read university data from CSV file.
# #     """
# #     universities = []
# #     try:
# #         with open(filename, 'r', encoding='utf-8') as file:
# #             reader = csv.DictReader(file)
# #             for row in reader:
# #                 universities.append(row)
# #         return universities
# #     except Exception as e:
# #         logger.error(f"Error reading CSV file: {e}")
# #         return []
# #
# #
# # def extract_all_elements_text(driver, selector, method=By.CSS_SELECTOR, wait_time=3):
# #     """
# #     Extract text from all elements matching the selector.
# #     Returns a list of strings.
# #     """
# #     try:
# #         WebDriverWait(driver, wait_time).until(
# #             EC.presence_of_element_located((method, selector))
# #         )
# #         elements = driver.find_elements(method, selector)
# #         return [el.text.strip() for el in elements if el.text.strip()]
# #     except Exception as e:
# #         logger.warning(f"Error extracting elements text: {e}")
# #         return []
# #
# #
# # def scrape_academics_section(driver, college_name: str, save_screenshot=False):
# #     """
# #     Specifically scrape majors data from the academics section
# #     """
# #     data = {
# #         "college_name": college_name,
# #         "majors": []
# #     }
# #
# #     # Try the specific class you mentioned
# #     major_selectors = [
# #         # Your specific class
# #         ".cb-roboto-light.csp-profile-majors-typeahead-item",
# #         # Alternative selectors to try
# #         "li.cb-roboto-light.csp-profile-majors-typeahead-item",
# #         "li[class*='csp-profile-majors-typeahead-item']",
# #         "li[class*='majors-typeahead-item']",
# #         "ul[class*='csp-majors-typeahead-unordered-list'] li"
# #     ]
# #
# #     # Try each selector
# #     for selector in major_selectors:
# #         logger.info(f"Trying selector: {selector}")
# #         majors = extract_all_elements_text(driver, selector)
# #         if majors:
# #             data["majors"] = majors
# #             logger.info(f"Found {len(majors)} majors using selector: {selector}")
# #             break
# #
# #     # If no majors found with specific selectors, try a more general approach
# #     if not data["majors"]:
# #         try:
# #             # Try to find any list items in a container that might contain majors
# #             logger.info("Trying general approach for finding majors")
# #
# #             # Look for elements that might contain major names
# #             major_elements = driver.find_elements(By.XPATH,
# #                                                   "//li[contains(@class, 'majors') or contains(@id, 'majors')]")
# #             if major_elements:
# #                 data["majors"] = [el.text.strip() for el in major_elements if el.text.strip()]
# #                 logger.info(f"Found {len(data['majors'])} majors using general approach")
# #         except Exception as e:
# #             logger.warning(f"Error with general majors search: {e}")
# #
# #     # Save screenshot for debugging if needed
# #     if save_screenshot:
# #         try:
# #             screenshot_name = f"{college_name.replace(' ', '_')}_academics.png"
# #             driver.save_screenshot(screenshot_name)
# #             logger.info(f"Screenshot saved as {screenshot_name}")
# #         except Exception as e:
# #             logger.warning(f"Could not save screenshot: {e}")
# #
# #     # If still no majors found, add debugging info to data
# #     if not data["majors"]:
# #         logger.warning(f"No majors found for {college_name}")
# #
# #         # Try to get page source for debugging
# #         try:
# #             # Get just a sample of the page source to avoid overly large logs
# #             page_source = driver.page_source[:5000]  # First 5000 chars
# #             data["debug_page_source_sample"] = page_source
# #         except:
# #             pass
# #
# #     return data
# #
# #
# # def scrape_college_majors(csv_file: str, output_file="college_majors.csv", continue_from=None, limit=None):
# #     """
# #     Main function to scrape only the academics section for majors
# #     """
# #     universities = read_universities_from_csv(csv_file)
# #     if not universities:
# #         logger.error("No universities found in the CSV file.")
# #         return
# #
# #     # Check if we're continuing from a previous run
# #     start_index = 0
# #     if continue_from:
# #         for i, uni in enumerate(universities):
# #             if uni['college_name'] == continue_from:
# #                 start_index = i
# #                 logger.info(f"Continuing from {continue_from} (index {start_index})")
# #                 break
# #
# #     # Apply limit if specified
# #     if limit and limit > 0:
# #         universities = universities[start_index:start_index + limit]
# #     else:
# #         universities = universities[start_index:]
# #
# #     driver = None
# #     results = []
# #
# #     # For incremental saving
# #     checkpoint_interval = 10  # Save progress every 10 universities
# #
# #     try:
# #         driver = setup_webdriver()
# #
# #         for i, uni in enumerate(universities):
# #             college_name = uni['college_name']
# #             slug = format_university_slug(college_name)
# #
# #             # Create URL specifically for academics section
# #             academics_url = f"https://bigfuture.collegeboard.org/colleges/{slug}/academics"
# #
# #             logger.info(f"Processing ({i + 1}/{len(universities)}): {college_name}")
# #             logger.info(f"URL: {academics_url}")
# #
# #             # Add random delay to avoid detection
# #             delay = 2 + random.random() * 3  # 2-5 seconds
# #             logger.info(f"Waiting for {delay:.2f} seconds...")
# #             time.sleep(delay)
# #
# #             try:
# #                 # Navigate to academics section
# #                 driver.get(academics_url)
# #
# #                 # Wait for page to load
# #                 time.sleep(3)
# #
# #                 # Check for popup and close it if needed
# #                 try:
# #                     popup_button = WebDriverWait(driver, 3).until(
# #                         EC.presence_of_element_located((By.XPATH, "//button[text()='Maybe Later']"))
# #                     )
# #                     popup_button.click()
# #                     logger.info("Closed popup dialog")
# #                 except:
# #                     pass  # No popup found
# #
# #                 # Scrape academics data
# #                 college_data = scrape_academics_section(driver, college_name, save_screenshot=(
# #                             i < 5))  # Save screenshots for the first 5 only
# #
# #                 # Add to results
# #                 results.append(college_data)
# #                 logger.info(f"Found {len(college_data.get('majors', []))} majors for {college_name}")
# #
# #                 # Save checkpoint periodically
# #                 if (i + 1) % checkpoint_interval == 0:
# #                     logger.info(f"Saving checkpoint after processing {i + 1} universities...")
# #
# #                     # Ensure we have all fields for CSV
# #                     all_fields = ["college_name", "majors"]
# #
# #                     with open(f"checkpoint_{i + 1}_{output_file}", 'w', newline='', encoding='utf-8') as csvfile:
# #                         writer = csv.writer(csvfile)
# #                         writer.writerow(["college_name", "majors"])  # Header
# #
# #                         for college in results:
# #                             writer.writerow([
# #                                 college["college_name"],
# #                                 "|".join(college.get("majors", []))
# #                             ])
# #
# #             except Exception as e:
# #                 logger.error(f"Error processing {college_name}: {e}")
# #
# #                 # Record the error
# #                 results.append({
# #                     "college_name": college_name,
# #                     "error": str(e),
# #                     "majors": []
# #                 })
# #
# #                 # Try to recover the session if needed
# #                 if i % 20 == 0:  # Every 20 colleges, restart the driver
# #                     try:
# #                         driver.quit()
# #                     except:
# #                         pass
# #
# #                     logger.info("Reinitializing WebDriver...")
# #                     time.sleep(5)
# #                     driver = setup_webdriver()
# #
# #             logger.info("-" * 50)
# #
# #         # Save final results to CSV
# #         with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
# #             writer = csv.writer(csvfile)
# #             writer.writerow(["college_name", "majors"])  # Header
# #
# #             for college in results:
# #                 writer.writerow([
# #                     college["college_name"],
# #                     "|".join(college.get("majors", []))
# #                 ])
# #
# #         logger.info(f"All results saved to {output_file}. Processed {len(results)} universities.")
# #
# #     except Exception as e:
# #         logger.error(f"Critical error during scraping: {e}")
# #         # Try to save what we have
# #         if results:
# #             emergency_file = f"emergency_majors_{int(time.time())}.csv"
# #             with open(emergency_file, 'w', newline='', encoding='utf-8') as csvfile:
# #                 writer = csv.writer(csvfile)
# #                 writer.writerow(["college_name", "majors"])  # Header
# #
# #                 for college in results:
# #                     writer.writerow([
# #                         college["college_name"],
# #                         "|".join(college.get("majors", []))
# #                     ])
# #             logger.info(f"Saved emergency data to {emergency_file}")
# #     finally:
# #         if driver:
# #             driver.quit()
# #
# #
# # # Example usage
# # if __name__ == "__main__":
# #     # Path to your CSV file with university names
# #     csv_file = "university_data.csv"
# #
# #     # Output CSV file
# #     output_file = "academics_detail.csv"
# #
# #     # To limit the number of universities to process (useful for testing in Kaggle)
# #     scrape_college_majors(csv_file, output_file, limit=270)
# #
# #     # To process all universities
# #     # scrape_college_majors(csv_file, output_file)
#
#
# import time
# import random
# import csv
# import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
# from webdriver_manager.chrome import ChromeDriverManager
# import sys
# import traceback
#
# # Set up Chrome options
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument(
#     "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36")
# #
# # # Initialize csv file
# # csv_filename = "niche_colleges_focused.csv"
# # with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
# #     csv_writer = csv.writer(csvfile)
# #     csv_writer.writerow(['Rank_Badge', 'College_Name'])
# #
# #
# # def initialize_driver():
# #     print("Initializing new WebDriver instance...")
# #     try:
# #         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
# #         return driver
# #     except Exception as e:
# #         print(f"Error initializing WebDriver: {e}")
# #         traceback.print_exc()
# #         sys.exit(1)
# #
# #
# # # Function to extract only the specified class data
# # def extract_focused_data(page_number, driver, max_retries=3):
# #     url = f"https://www.niche.com/colleges/search/best-colleges/?page={page_number}"
# #     print(f"Scraping page {page_number}...")
# #
# #     colleges_data = []
# #     retries = 0
# #
# #     while retries < max_retries:
# #         try:
# #             # Add random delay between 4 to 6 seconds
# #             delay = random.uniform(4, 6)
# #             time.sleep(delay)
# #
# #             driver.get(url)
# #
# #             # Wait for the college items to load
# #             wait = WebDriverWait(driver, 15)
# #             wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search-results__list__item")))
# #
# #             # Allow extra time for JavaScript to fully load
# #             time.sleep(2)
# #
# #             # Extract data using standard CSS selectors first
# #             rank_badges = driver.find_elements(By.CSS_SELECTOR, ".search-result-badge")
# #             college_names = driver.find_elements(By.CSS_SELECTOR, "[data-testid='search-result__title']")
# #
# #             # If the standard selectors don't work, try the specific class names
# #             if not rank_badges:
# #                 print("Trying alternative selectors for rank badges...")
# #                 rank_badges = driver.find_elements(By.CSS_SELECTOR, ".MuiTypography-preheaderSmall")
# #                 if not rank_badges:
# #                     rank_badges = driver.find_elements(By.CSS_SELECTOR, "[class*='search-result-badge']")
# #
# #             if not college_names:
# #                 print("Trying alternative selectors for college names...")
# #                 college_names = driver.find_elements(By.CSS_SELECTOR, ".MuiTypography-labelMedium")
# #                 if not college_names:
# #                     college_names = driver.find_elements(By.CSS_SELECTOR, "[class*='MuiLink-underlineHover']")
# #
# #             print(f"Found {len(rank_badges)} rank badges and {len(college_names)} college names")
# #
# #             # Match them up and save the data
# #             for i in range(min(len(rank_badges), len(college_names))):
# #                 try:
# #                     rank_badge_text = rank_badges[i].text.strip()
# #                     college_name_text = college_names[i].text.strip()
# #
# #                     if rank_badge_text and college_name_text:
# #                         college_data = [rank_badge_text, college_name_text]
# #                         colleges_data.append(college_data)
# #
# #                         # Write to CSV
# #                         with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
# #                             csv_writer = csv.writer(csvfile)
# #                             csv_writer.writerow(college_data)
# #
# #                 except Exception as e:
# #                     print(f"Error processing item {i}: {e}")
# #
# #             # If we got here without exceptions and found data, break out of the retry loop
# #             if colleges_data:
# #                 break
# #             else:
# #                 print("No data found, retrying...")
# #                 retries += 1
# #
# #         except TimeoutException:
# #             print(f"Timeout on page {page_number}, retrying... ({retries + 1}/{max_retries})")
# #             retries += 1
# #             # Take a screenshot for debugging
# #             try:
# #                 driver.save_screenshot(f"timeout_page_{page_number}.png")
# #             except:
# #                 pass
# #
# #         except WebDriverException as e:
# #             print(f"WebDriver error on page {page_number}: {e}")
# #             print("Restarting the driver...")
# #             try:
# #                 driver.quit()
# #             except:
# #                 pass
# #             driver = initialize_driver()
# #             retries += 1
# #
# #         except Exception as e:
# #             print(f"Unexpected error on page {page_number}: {e}")
# #             traceback.print_exc()
# #             retries += 1
# #
# #     return colleges_data, driver
# #
# #
# # # Main scraping function
# # def scrape_niche_focused():
# #     all_colleges = []
# #     driver = initialize_driver()
# #
# #     try:
# #         for page in range(1, 107):  # Pages 1 to 106
# #             try:
# #                 colleges_on_page, driver = extract_focused_data(page, driver)
# #                 all_colleges.extend(colleges_on_page)
# #                 print(f"Completed page {page}. Total colleges scraped so far: {len(all_colleges)}")
# #             except Exception as e:
# #                 print(f"Error processing page {page}: {e}")
# #                 traceback.print_exc()
# #                 # Reinitialize driver if there's an issue
# #                 try:
# #                     driver.quit()
# #                 except:
# #                     pass
# #                 driver = initialize_driver()
# #     except Exception as e:
# #         print(f"Error during scraping: {e}")
# #         traceback.print_exc()
# #     finally:
# #         try:
# #             driver.quit()
# #         except:
# #             pass
# #
# #     # Create a DataFrame
# #     df = pd.DataFrame(all_colleges, columns=['Rank_Badge', 'College_Name'])
# #
# #     # Save to CSV (backup)
# #     df.to_csv("niche_colleges_focused_dataframe.csv", index=False)
# #
# #     print(f"Focused scraping completed. Data saved to {csv_filename} and niche_colleges_focused_dataframe.csv")
# #     return df
# #
# #
# # # Run the scraper
# # if __name__ == "__main__":
# #     try:
# #         college_data = scrape_niche_focused()
# #         print(f"Total colleges scraped: {len(college_data)}")
# #     except Exception as e:
# #         print(f"Fatal error in main program: {e}")
# #         traceback.print_exc()
#
#
# import time
# import random
# import csv
# import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
# from webdriver_manager.chrome import ChromeDriverManager
# import sys
# import traceback
#
# # Set up Chrome options
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument(
#     "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36")
#
# # Initialize csv file
# csv_filename = "majors_data.csv"
# with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
#     csv_writer = csv.writer(csvfile)
#     csv_writer.writerow(['Major_Category', 'Subcategory'])
#
#
# def initialize_driver():
#     print("Initializing new WebDriver instance...")
#     try:
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
#         return driver
#     except Exception as e:
#         print(f"Error initializing WebDriver: {e}")
#         traceback.print_exc()
#         sys.exit(1)
#
#
# def extract_majors_data(driver, max_retries=3):
#     url = "https://www.niche.com/colleges/major-rankings/"
#     print(f"Scraping majors data from {url}...")
#
#     majors_data = []
#     retries = 0
#
#     while retries < max_retries:
#         try:
#             # Add random delay between 4 to 6 seconds
#             delay = random.uniform(4, 6)
#             time.sleep(delay)
#
#             driver.get(url)
#
#             # Wait for the major categories to load
#             wait = WebDriverWait(driver, 15)
#             wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ce__list__category-title")))
#
#             # Allow extra time for JavaScript to fully load
#             time.sleep(3)
#
#             # Extract all major categories
#             major_categories = driver.find_elements(By.CLASS_NAME, "ce__list__category-title")
#
#             print(f"Found {len(major_categories)} major categories")
#
#             # For each major category
#             for category in major_categories:
#                 try:
#                     category_name = category.text.strip()
#                     print(f"Processing major category: {category_name}")
#
#                     # Find the parent element to search for subcategories within this category's section
#                     parent_div = category.find_element(By.XPATH,
#                                                        "./ancestor::div[contains(@id, 'arts') or contains(@class, 'ce_list-container')]")
#
#                     # Find all subcategories within this category section
#                     subcategories = parent_div.find_elements(By.CLASS_NAME, "ce__list__subcategory-title")
#
#                     print(f"  Found {len(subcategories)} subcategories for {category_name}")
#
#                     if len(subcategories) == 0:
#                         # Try an alternative selector to find subcategories
#                         subcategories = parent_div.find_elements(By.CSS_SELECTOR, "h3")
#                         print(
#                             f"  After alternative search: Found {len(subcategories)} subcategories for {category_name}")
#
#                     # If no subcategories found, add the category with an empty subcategory
#                     if len(subcategories) == 0:
#                         majors_data.append([category_name, ""])
#
#                         # Write to CSV
#                         with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
#                             csv_writer = csv.writer(csvfile)
#                             csv_writer.writerow([category_name, ""])
#                     else:
#                         # For each subcategory under this major category
#                         for subcategory in subcategories:
#                             try:
#                                 subcategory_name = subcategory.text.strip()
#
#                                 # Filter out any non-subcategory text that might be captured
#                                 if subcategory_name and len(subcategory_name) > 0:
#                                     print(f"    Subcategory: {subcategory_name}")
#                                     majors_data.append([category_name, subcategory_name])
#
#                                     # Write to CSV
#                                     with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
#                                         csv_writer = csv.writer(csvfile)
#                                         csv_writer.writerow([category_name, subcategory_name])
#                             except Exception as e:
#                                 print(f"Error processing subcategory: {e}")
#
#                 except Exception as e:
#                     print(f"Error processing category {category_name}: {e}")
#
#             # If we successfully processed data, break out of retry loop
#             if majors_data:
#                 break
#             else:
#                 print("No data found, retrying...")
#                 retries += 1
#
#         except TimeoutException:
#             print(f"Timeout while scraping, retrying... ({retries + 1}/{max_retries})")
#             retries += 1
#             # Take a screenshot for debugging
#             try:
#                 driver.save_screenshot(f"timeout_majors.png")
#             except:
#                 pass
#
#         except WebDriverException as e:
#             print(f"WebDriver error: {e}")
#             print("Restarting the driver...")
#             try:
#                 driver.quit()
#             except:
#                 pass
#             driver = initialize_driver()
#             retries += 1
#
#         except Exception as e:
#             print(f"Unexpected error: {e}")
#             traceback.print_exc()
#             retries += 1
#
#     return majors_data, driver
#
#
# # Main scraping function
# def scrape_niche_majors():
#     driver = initialize_driver()
#
#     try:
#         # Try a different approach to better handle the categories and subcategories
#         all_majors_data, driver = extract_majors_data(driver)
#
#         # Create a DataFrame
#         df = pd.DataFrame(all_majors_data, columns=['Major_Category', 'Subcategory'])
#
#         # Save to CSV (backup)
#         df.to_csv("majors_data_backup.csv", index=False)
#
#         print(f"Majors scraping completed. Data saved to {csv_filename} and majors_data_backup.csv")
#         return df
#
#     except Exception as e:
#         print(f"Error during scraping: {e}")
#         traceback.print_exc()
#     finally:
#         try:
#             driver.quit()
#         except:
#             pass
#
#
# # Extended extraction function that tries multiple approaches
# def extract_majors_data_extended(driver):
#     """
#     This function tries multiple approaches to extract the major categories and their subcategories
#     """
#     url = "https://www.niche.com/colleges/major-rankings/"
#     print(f"Scraping majors data with extended approach from {url}...")
#
#     majors_data = []
#
#     try:
#         driver.get(url)
#
#         # Wait for the page to load
#         wait = WebDriverWait(driver, 15)
#         wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ce__list__category-title")))
#
#         # Allow extra time for JavaScript to fully load
#         time.sleep(3)
#
#         # Take a screenshot to verify what we're seeing
#         driver.save_screenshot("niche_majors_page.png")
#
#         # Get all major categories from the page
#         major_categories = driver.find_elements(By.CLASS_NAME, "ce__list__category-title")
#         print(f"Found {len(major_categories)} major categories")
#
#         # For each major category div
#         for i, category in enumerate(major_categories):
#             try:
#                 category_name = category.text.strip()
#                 print(f"Processing major category {i + 1}: {category_name}")
#
#                 # Try to find the parent container that contains all subcategories for this category
#                 # Method 1: Look for specific structural elements
#                 try:
#                     # Find the closest parent div that might contain subcategories
#                     parent_div = category.find_element(By.XPATH,
#                                                        "./ancestor::div[contains(@id, text()) or contains(@class, 'ce_list-container')]")
#
#                     # Look for subcategories within this div
#                     subcategories = parent_div.find_elements(By.CLASS_NAME, "ce__list__subcategory-title")
#
#                     if not subcategories:
#                         # Alternative: try to find h3 elements
#                         subcategories = parent_div.find_elements(By.CSS_SELECTOR, "h3:not(.ce__list__category-title)")
#
#                     if not subcategories:
#                         # Try a more generic approach - find all elements with specific text patterns
#                         subcategories = parent_div.find_elements(By.XPATH, ".//div[contains(@class, 'ce__list')]//h3")
#
#                     print(f"  Found {len(subcategories)} subcategories for {category_name}")
#
#                     # Process subcategories
#                     for subcategory in subcategories:
#                         subcategory_name = subcategory.text.strip()
#                         if subcategory_name:
#                             print(f"    Subcategory: {subcategory_name}")
#                             majors_data.append([category_name, subcategory_name])
#
#                 except Exception as inner_e:
#                     print(f"Error finding subcategories for {category_name}: {inner_e}")
#                     # Fallback: Try to find subcategories based on position in the DOM
#                     try:
#                         # Find the next elements after this category header that might be subcategories
#                         # This is a simplistic approach that might work in some cases
#                         parent_element = category.find_element(By.XPATH, "./parent::div")
#                         following_elements = parent_element.find_elements(By.XPATH,
#                                                                           "./following-sibling::div[position() < 10]")
#
#                         subcategory_found = False
#                         for elem in following_elements:
#                             # Check if this is another category heading (which would end our search)
#                             if elem.find_elements(By.CLASS_NAME, "ce__list__category-title"):
#                                 break
#
#                             # Try to find subcategories within this element
#                             subcategory_elements = elem.find_elements(By.CLASS_NAME, "ce__list__subcategory-title")
#                             if not subcategory_elements:
#                                 subcategory_elements = elem.find_elements(By.TAG_NAME, "h3")
#
#                             # Process any found subcategories
#                             for subcategory in subcategory_elements:
#                                 subcategory_name = subcategory.text.strip()
#                                 if subcategory_name:
#                                     print(f"    Subcategory (fallback): {subcategory_name}")
#                                     majors_data.append([category_name, subcategory_name])
#                                     subcategory_found = True
#
#                         # If no subcategories were found, add the category with an empty subcategory
#                         if not subcategory_found:
#                             majors_data.append([category_name, ""])
#
#                     except Exception as fallback_e:
#                         print(f"Fallback method failed for {category_name}: {fallback_e}")
#                         majors_data.append([category_name, ""])
#
#             except Exception as e:
#                 print(f"Error processing major category: {e}")
#
#         # If the normal approach didn't work, try a completely different method
#         if not majors_data:
#             print("Trying alternate extraction method...")
#
#             # Get all h2 elements (likely major categories)
#             h2_elements = driver.find_elements(By.TAG_NAME, "h2")
#             for h2 in h2_elements:
#                 try:
#                     category_name = h2.text.strip()
#                     if category_name:
#                         print(f"Found major category (h2): {category_name}")
#
#                         # Look for the nearby h3 elements that might be subcategories
#                         # This is a simple approximation, may need refinement
#                         parent = h2.find_element(By.XPATH, "./ancestor::div[1]")
#                         h3_elements = parent.find_elements(By.TAG_NAME, "h3")
#
#                         if h3_elements:
#                             for h3 in h3_elements:
#                                 subcategory_name = h3.text.strip()
#                                 if subcategory_name:
#                                     print(f"  Subcategory (h3): {subcategory_name}")
#                                     majors_data.append([category_name, subcategory_name])
#                         else:
#                             majors_data.append([category_name, ""])
#
#                 except Exception as alt_e:
#                     print(f"Error in alternate method: {alt_e}")
#
#         # Write data to CSV
#         with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
#             csv_writer = csv.writer(csvfile)
#             for data_row in majors_data:
#                 csv_writer.writerow(data_row)
#
#         return majors_data
#
#     except Exception as e:
#         print(f"Error in extended extraction: {e}")
#         traceback.print_exc()
#         return []
#
#
# # Run the scraper
# if __name__ == "__main__":
#     try:
#         # First try the standard approach
#         majors_data = scrape_niche_majors()
#
#         # If we didn't get any data, try the extended approach
#         if majors_data is None or len(majors_data) == 0:
#             print("Standard approach failed, trying extended approach...")
#             driver = initialize_driver()
#             try:
#                 majors_data = extract_majors_data_extended(driver)
#             finally:
#                 driver.quit()
#
#         # Report results
#         if majors_data is not None:
#             print(f"Total major categories and subcategories scraped: {len(majors_data)}")
#         else:
#             print("Failed to scrape major data")
#
#     except Exception as e:
#         print(f"Fatal error in main program: {e}")
#         traceback.print_exc()


import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re


def setup_driver():
    """Setup Chrome driver with options"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Remove this line if you want to see the browser
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    # You might need to specify the path to your chromedriver
    # service = Service('/path/to/chromedriver')  # Uncomment and modify if needed
    # driver = webdriver.Chrome(service=service, options=chrome_options)

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def extract_source_code_links(text):
    """Extract source code links from text"""
    links = []
    # Look for common patterns of source code links
    patterns = [
        r'https?://github\.com/[^\s<>"\']+',
        r'https?://gitlab\.com/[^\s<>"\']+',
        r'https?://bitbucket\.org/[^\s<>"\']+',
        r'https?://[^\s<>"\']*(?:source|code|github|git)[^\s<>"\']*'
    ]

    for pattern in patterns:
        found_links = re.findall(pattern, text, re.IGNORECASE)
        links.extend(found_links)

    return list(set(links))  # Remove duplicates


def scrape_iot_projects():
    """Main scraping function"""
    url = "https://www.knowledgehut.com/blog/cloud-computing/iot-projects"
    driver = setup_driver()

    projects_data = []

    try:
        print("Loading the webpage...")
        driver.get(url)

        # Wait for the page to load
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Scroll down to load all content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Find all image containers with the specified class
        print("Looking for project containers...")
        image_containers = driver.find_elements(By.CLASS_NAME, "jsx-f6d60829cbef0e92.image.w-full")

        if not image_containers:
            # Try alternative selectors
            image_containers = driver.find_elements(By.CSS_SELECTOR, ".jsx-f6d60829cbef0e92.image.w-full")

        if not image_containers:
            # Try finding by partial class name
            image_containers = driver.find_elements(By.CSS_SELECTOR, "[class*='image'][class*='w-full']")

        print(f"Found {len(image_containers)} potential project containers")

        # If we still don't find the specific containers, let's look for ckeditorFont class directly
        if not image_containers:
            print("Trying alternative approach - looking for ckeditorFont class directly...")
            ckeditor_elements = driver.find_elements(By.CLASS_NAME, "ckeditorFont")
            print(f"Found {len(ckeditor_elements)} ckeditorFont elements")

            # Process each ckeditorFont section
            for i, element in enumerate(ckeditor_elements):
                try:
                    project_data = process_ckeditor_element(element, i + 1)
                    if project_data:
                        projects_data.append(project_data)
                except Exception as e:
                    print(f"Error processing ckeditorFont element {i + 1}: {str(e)}")
                    continue
        else:
            # Process each image container
            for i, container in enumerate(image_containers):
                try:
                    # Look for ckeditorFont class within this container
                    ckeditor_elements = container.find_elements(By.CLASS_NAME, "ckeditorFont")

                    for j, ckeditor_element in enumerate(ckeditor_elements):
                        project_data = process_ckeditor_element(ckeditor_element, f"{i + 1}.{j + 1}")
                        if project_data:
                            projects_data.append(project_data)

                except Exception as e:
                    print(f"Error processing container {i + 1}: {str(e)}")
                    continue

        print(f"Successfully extracted {len(projects_data)} projects")

    except TimeoutException:
        print("Timeout: Page took too long to load")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()

    return projects_data


def process_ckeditor_element(element, index):
    """Process a single ckeditorFont element to extract project data"""
    project_data = {
        'idea': '',
        'about': '',
        'requirements': '',
        'source_code': ''
    }

    try:
        # Get all child elements
        h3_elements = element.find_elements(By.TAG_NAME, "h3")
        p_elements = element.find_elements(By.TAG_NAME, "p")
        ul_elements = element.find_elements(By.TAG_NAME, "ul")

        # Extract h3 (idea)
        if h3_elements:
            project_data['idea'] = h3_elements[0].text.strip()

        # Extract p (about) and look for source code links
        if p_elements:
            about_text = ""
            source_links = []

            for p in p_elements:
                p_text = p.text.strip()
                if p_text:
                    about_text += p_text + " "

                # Look for links within p tags
                links = p.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute('href')
                    if href:
                        source_links.append(href)

                # Also extract links from text content
                text_links = extract_source_code_links(p.get_attribute('innerHTML'))
                source_links.extend(text_links)

            project_data['about'] = about_text.strip()
            project_data['source_code'] = '; '.join(list(set(source_links))) if source_links else ''

        # Extract ul li (requirements)
        if ul_elements:
            requirements = []
            for ul in ul_elements:
                li_elements = ul.find_elements(By.TAG_NAME, "li")
                for li in li_elements:
                    li_text = li.text.strip()
                    if li_text:
                        requirements.append(li_text)

            project_data['requirements'] = '; '.join(requirements)

        # Only return if we have at least an idea or about section
        if project_data['idea'] or project_data['about']:
            print(f"Extracted project {index}: {project_data['idea'][:50]}...")
            return project_data

    except Exception as e:
        print(f"Error processing element {index}: {str(e)}")

    return None


def save_to_csv(projects_data, filename="iot_projects.csv"):
    """Save the scraped data to CSV file"""
    if projects_data:
        # Define CSV headers
        headers = ['idea', 'about', 'requirements', 'source_code']

        # Write to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(projects_data)

        print(f"Data saved to {filename}")
        print(f"Total projects saved: {len(projects_data)}")

        # Display summary
        print("\nData Summary:")
        print(f"Projects with ideas: {sum(1 for p in projects_data if p['idea'])}")
        print(f"Projects with about section: {sum(1 for p in projects_data if p['about'])}")
        print(f"Projects with requirements: {sum(1 for p in projects_data if p['requirements'])}")
        print(f"Projects with source code links: {sum(1 for p in projects_data if p['source_code'])}")

        return projects_data
    else:
        print("No data to save")
        return None


def main():
    """Main execution function"""
    print("Starting IoT Projects Scraper...")
    print("Make sure you have Chrome browser and chromedriver installed")
    print("You can download chromedriver from: https://chromedriver.chromium.org/")

    # Scrape the data
    projects_data = scrape_iot_projects()

    # Save to CSV
    if projects_data:
        saved_data = save_to_csv(projects_data)

        # Display first few projects
        if saved_data:
            print("\nFirst 3 projects preview:")
            for i, project in enumerate(saved_data[:3]):
                print(f"\nProject {i + 1}:")
                print(f"Idea: {project['idea'][:100]}{'...' if len(project['idea']) > 100 else ''}")
                print(f"About: {project['about'][:100]}{'...' if len(project['about']) > 100 else ''}")
                print(
                    f"Requirements: {project['requirements'][:100]}{'...' if len(project['requirements']) > 100 else ''}")
                print(
                    f"Source Code: {project['source_code'][:100]}{'...' if len(project['source_code']) > 100 else ''}")
    else:
        print("No projects were scraped. Please check the website structure or your internet connection.")


if __name__ == "__main__":
    main()