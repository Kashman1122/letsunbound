import time
import random
import csv
import os
import json
import platform
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup

# List of profile URLs to scrape
profile_urls = [
    "https://www.linkedin.com/in/nav-agarwal-45009a158/",
    "https://www.linkedin.com/in/tarini-malhotra-645518230/",
    "https://www.linkedin.com/in/ahaana-bharat-ram-3a8863241/",
    "https://www.linkedin.com/in/mahi-shingari-a98552304/",
    "https://www.linkedin.com/in/avani-advani-79b072251/",
    "https://www.linkedin.com/in/tia-mathur-b67594281/",
    "https://www.linkedin.com/in/shaury-sinha/"
]

# Configuration parameters
CONFIG = {
    "output_dir": "linkedin_data",
    "csv_filename": "linkedin_profiles.csv",
    "json_filename": "linkedin_profiles.json",
    "timeout": 15,
    "min_delay": 15,
    "max_delay": 30,
    "scroll_min": 3,
    "scroll_max": 7
}


class LinkedInScraper:
    def __init__(self, username, password):
        """Initialize the LinkedIn scraper with credentials"""
        self.username = username
        self.password = password
        self.driver = None
        self.profiles_data = []

        # Create output directory if it doesn't exist
        if not os.path.exists(CONFIG["output_dir"]):
            os.makedirs(CONFIG["output_dir"])

    def create_stealth_driver(self):
        """Create a Selenium WebDriver with advanced anti-detection measures"""
        try:
            # Set up user data directory - important to fix the prefs file error
            system = platform.system()
            # Create a dedicated Chrome user data directory for this script
            if system == "Windows":
                user_data_dir = os.path.join(os.environ["LOCALAPPDATA"], "LinkedInScraper", "UserData")
            else:  # Linux or Mac
                user_data_dir = os.path.join(os.path.expanduser("~"), ".LinkedInScraper", "UserData")

            # Create the directory if it doesn't exist
            os.makedirs(user_data_dir, exist_ok=True)

            options = Options()

            # Set user data directory to prevent prefs file writing issues
            options.add_argument(f"--user-data-dir={user_data_dir}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            # Common anti-detection measures
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--start-maximized")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            # Add realistic user agent with recent Chrome version
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36")

            # Additional privacy and fingerprinting protections
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-extensions")

            print("Creating Chrome WebDriver...")

            # Using Service class for better control
            chrome_service = Service()
            driver = webdriver.Chrome(service=chrome_service, options=options)

            # Apply additional stealth settings directly to the page
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")

            print("Chrome WebDriver created successfully.")
            return driver

        except Exception as e:
            print(f"Error creating Chrome driver: {e}")
            print("\nTrying alternative approach with simplified options...")

            # Fallback to a simpler configuration if the first attempt fails
            try:
                basic_options = Options()
                basic_options.add_argument("--no-sandbox")
                basic_options.add_argument("--disable-dev-shm-usage")

                driver = webdriver.Chrome(options=basic_options)
                print("Chrome WebDriver created with fallback options.")
                return driver
            except Exception as e2:
                print(f"Second attempt failed: {e2}")
                raise

    def add_random_delays(self, min_delay=2, max_delay=5):
        """Add a random delay to simulate human behavior"""
        base_delay = random.uniform(min_delay, max_delay)
        noise = random.uniform(0.5, 2)
        time.sleep(base_delay + noise)

    def perform_random_scrolls(self, min_scrolls=3, max_scrolls=7):
        """Perform random scrolling to simulate human behavior"""
        try:
            # Get page height
            total_height = self.driver.execute_script("return document.body.scrollHeight")

            # Random number of scroll actions
            num_scrolls = random.randint(min_scrolls, max_scrolls)

            for _ in range(num_scrolls):
                # Random scroll position
                scroll_to = random.randint(100, int(total_height * 0.8))
                self.driver.execute_script(f"window.scrollTo(0, {scroll_to})")
                time.sleep(random.uniform(0.5, 2))

                # Occasionally scroll back up a bit to mimic natural reading
                if random.random() > 0.7:
                    scroll_back = random.randint(50, scroll_to)
                    self.driver.execute_script(f"window.scrollTo(0, {scroll_back})")
                    time.sleep(random.uniform(0.3, 1))
        except Exception as e:
            print(f"Warning: Error during scrolling: {e}")
            # Continue even if scrolling fails

    def login_to_linkedin(self):
        """Log in to LinkedIn with enhanced anti-detection measures"""
        try:
            # Go to login page
            print("Navigating to LinkedIn login page...")
            self.driver.get("https://www.linkedin.com/login")
            self.add_random_delays()

            # Enter username with human-like typing
            print("Entering username...")
            username_field = WebDriverWait(self.driver, CONFIG["timeout"]).until(
                EC.presence_of_element_located((By.ID, "username"))
            )

            # Type username with random delays between characters
            for char in self.username:
                username_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))

            self.add_random_delays()

            # Enter password with human-like typing
            print("Entering password...")
            password_field = self.driver.find_element(By.ID, "password")
            for char in self.password:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))

            self.add_random_delays()

            # Move mouse to login button and click
            print("Clicking login button...")
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()

            # Wait for login to complete and dashboard to load
            try:
                WebDriverWait(self.driver, CONFIG["timeout"]).until(
                    EC.presence_of_element_located((By.ID, "global-nav"))
                )
                print("✅ Successfully logged in to LinkedIn")
                return True
            except TimeoutException:
                # Check if there's a security verification step
                if "security verification" in self.driver.page_source.lower() or "captcha" in self.driver.page_source.lower():
                    print("⚠️ Security verification detected. Please complete it manually.")
                    # Wait for manual intervention
                    input("Press Enter after completing the security verification...")
                    return True
                else:
                    print("❌ Login unsuccessful. Please check credentials or for unusual login activity.")
                    print("Page source preview:", self.driver.page_source[:200])  # Debug info
                    return False

        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def extract_profile_data(self, soup, url):
        """Extract profile data from the parsed HTML"""
        profile_data = {
            'profile_url': url,
            'scrape_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'name': 'Not found',
            'headline': 'Not found',
            'location': 'Not found',
            'about': 'Not found',
            'experience': [],
            'education': [],
            'skills': [],
            'certifications': [],
            'languages': []
        }

        # Extract name
        try:
            name_element = soup.find('h1', class_=lambda c: c and 'text-heading-xlarge' in c)
            if name_element:
                profile_data['name'] = name_element.get_text().strip()
        except Exception as e:
            print(f"⚠️ Error extracting name: {e}")

        # Extract headline
        try:
            headline_element = soup.find('div', class_=lambda c: c and 'text-body-medium' in c)
            if headline_element:
                profile_data['headline'] = headline_element.get_text().strip()
        except Exception as e:
            print(f"⚠️ Error extracting headline: {e}")

        # Extract location
        try:
            location_element = soup.find('span', class_=lambda c: c and 'text-body-small inline' in c)
            if location_element:
                profile_data['location'] = location_element.get_text().strip()
        except Exception as e:
            print(f"⚠️ Error extracting location: {e}")

        # Extract about section
        try:
            about_section = soup.find(lambda tag: tag.name == 'section' and tag.find('div', {'id': 'about'}))
            if about_section:
                about_text = about_section.find('div', class_=lambda c: c and 'display-flex' in c)
                if about_text:
                    profile_data['about'] = about_text.get_text().strip()
        except Exception as e:
            print(f"⚠️ Error extracting about section: {e}")

        # Extract experience
        try:
            experience_section = soup.find(lambda tag: tag.name == 'section' and tag.find('div', {'id': 'experience'}))
            if experience_section:
                experience_items = experience_section.find_all('li', class_=lambda c: c and 'artdeco-list__item' in c)

                for item in experience_items:
                    job_info = {
                        'company': 'Not found',
                        'title': 'Not found',
                        'date_range': 'Not found',
                        'duration': 'Not found',
                        'location': 'Not found',
                        'description': 'Not found'
                    }

                    # Company name
                    company_element = item.find('span', class_=lambda c: c and 'pvs-entity__path-node' in c)
                    if company_element:
                        job_info['company'] = company_element.get_text().strip()

                    # Job title
                    title_element = item.find('span', class_=lambda c: c and 'pvs-entity__title-text' in c)
                    if title_element:
                        job_info['title'] = title_element.get_text().strip()

                    # Dates
                    date_element = item.find('span', class_=lambda c: c and 'pvs-entity__date-range' in c)
                    if date_element:
                        date_range = date_element.get_text().strip()
                        job_info['date_range'] = date_range

                        # Try to extract duration if available
                        duration_element = item.find('span', class_=lambda c: c and 'pvs-entity__caption-text' in c)
                        if duration_element:
                            job_info['duration'] = duration_element.get_text().strip()

                    # Description
                    desc_element = item.find('div', class_=lambda c: c and 'pvs-list__outer-container' in c)
                    if desc_element:
                        job_info['description'] = desc_element.get_text().strip()

                    if job_info:
                        profile_data['experience'].append(job_info)
        except Exception as e:
            print(f"⚠️ Error extracting experience: {e}")

        # Extract education
        try:
            education_section = soup.find(lambda tag: tag.name == 'section' and tag.find('div', {'id': 'education'}))
            if education_section:
                education_items = education_section.find_all('li', class_=lambda c: c and 'artdeco-list__item' in c)

                for item in education_items:
                    edu_info = {
                        'school': 'Not found',
                        'degree': 'Not found',
                        'field_of_study': 'Not found',
                        'date_range': 'Not found',
                        'activities': 'Not found'
                    }

                    # School name
                    school_element = item.find('span', class_=lambda c: c and 'pvs-entity__title-text' in c)
                    if school_element:
                        edu_info['school'] = school_element.get_text().strip()

                    # Degree and Field
                    degree_element = item.find('span', class_=lambda c: c and 'pvs-entity__secondary-title' in c)
                    if degree_element:
                        degree_text = degree_element.get_text().strip()
                        degree_parts = degree_text.split(',', 1)

                        if len(degree_parts) > 0:
                            edu_info['degree'] = degree_parts[0].strip()

                        if len(degree_parts) > 1:
                            edu_info['field_of_study'] = degree_parts[1].strip()

                    # Dates
                    date_element = item.find('span', class_=lambda c: c and 'pvs-entity__date-range' in c)
                    if date_element:
                        edu_info['date_range'] = date_element.get_text().strip()

                    # Activities
                    activities_element = item.find('div', class_=lambda c: c and 'pvs-list__outer-container' in c)
                    if activities_element:
                        edu_info['activities'] = activities_element.get_text().strip()

                    if edu_info:
                        profile_data['education'].append(edu_info)
        except Exception as e:
            print(f"⚠️ Error extracting education: {e}")

        # Extract skills
        try:
            skills_section = soup.find(lambda tag: tag.name == 'section' and tag.find('div', {'id': 'skills'}))
            if skills_section:
                skill_items = skills_section.find_all('span', class_=lambda c: c and 'pvs-entity__text' in c)

                for item in skill_items:
                    skill_text = item.get_text().strip()
                    if skill_text and len(skill_text) < 50:  # Filtering out non-skill text
                        profile_data['skills'].append(skill_text)
        except Exception as e:
            print(f"⚠️ Error extracting skills: {e}")

        # Extract certifications
        try:
            cert_section = soup.find(lambda tag: tag.name == 'section' and tag.find('div', {'id': 'certifications'}))
            if cert_section:
                cert_items = cert_section.find_all('li', class_=lambda c: c and 'artdeco-list__item' in c)

                for item in cert_items:
                    cert_info = {
                        'name': 'Not found',
                        'issuer': 'Not found',
                        'date': 'Not found'
                    }

                    # Certificate name
                    name_element = item.find('span', class_=lambda c: c and 'pvs-entity__title-text' in c)
                    if name_element:
                        cert_info['name'] = name_element.get_text().strip()

                    # Issuer
                    issuer_element = item.find('span', class_=lambda c: c and 'pvs-entity__secondary-title' in c)
                    if issuer_element:
                        cert_info['issuer'] = issuer_element.get_text().strip()

                    # Date
                    date_element = item.find('span', class_=lambda c: c and 'pvs-entity__date-range' in c)
                    if date_element:
                        cert_info['date'] = date_element.get_text().strip()

                    if cert_info:
                        profile_data['certifications'].append(cert_info)
        except Exception as e:
            print(f"⚠️ Error extracting certifications: {e}")

        return profile_data

    def scrape_profile(self, url):
        """Scrape a LinkedIn profile with anti-detection measures"""
        try:
            print(f"\n🔍 Navigating to profile: {url}")
            self.driver.get(url)

            # Wait for profile to load
            try:
                WebDriverWait(self.driver, CONFIG["timeout"]).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "pvs-profile-actions"))
                )
            except TimeoutException:
                print("⚠️ Profile page did not load properly within the timeout period")
                # Try alternative selectors that might be present on the profile page
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 'text-heading-xlarge')]"))
                    )
                    print("Found profile name - continuing with extraction")
                except TimeoutException:
                    # Check if we've been detected
                    if "we've restricted" in self.driver.page_source.lower() or "unusual activity" in self.driver.page_source.lower():
                        print("❌ LinkedIn has detected automation. Try again later or with different settings.")
                        return None
                    print("Proceeding anyway and attempting to extract data")

            # Simulate human behavior
            self.add_random_delays()
            self.perform_random_scrolls(CONFIG["scroll_min"], CONFIG["scroll_max"])

            # Expand sections if present
            sections_to_expand = [
                "//button[contains(., 'Show more skills')]",
                "//button[contains(., 'Show all experiences')]",
                "//button[contains(., 'Show all education')]",
                "//button[contains(., 'Show more')]"
            ]

            for xpath in sections_to_expand:
                try:
                    show_more_buttons = self.driver.find_elements(By.XPATH, xpath)
                    for button in show_more_buttons:
                        try:
                            # Only click if button is visible and enabled
                            if button.is_displayed() and button.is_enabled():
                                self.driver.execute_script("arguments[0].click();", button)
                                self.add_random_delays(1, 3)
                        except StaleElementReferenceException:
                            # Element might have become stale after DOM updates
                            pass
                except Exception as e:
                    pass  # Silently continue if can't expand a section

            # More human-like behavior
            self.perform_random_scrolls(CONFIG["scroll_min"], CONFIG["scroll_max"])
            self.add_random_delays()

            # Get the page source and parse it
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract data
            profile_data = self.extract_profile_data(soup, url)

            return profile_data

        except Exception as e:
            print(f"❌ Error scraping profile {url}: {e}")
            return None

    def save_to_csv(self, filename=None):
        """Save the scraped profiles to a CSV file"""
        if not self.profiles_data:
            print("❌ No profile data to save")
            return

        if not filename:
            filename = os.path.join(CONFIG["output_dir"], CONFIG["csv_filename"])

        # Flatten nested data
        flattened_data = []
        for profile in self.profiles_data:
            if not profile:  # Skip None values
                continue

            flat_profile = {
                'profile_url': profile.get('profile_url', 'Not found'),
                'scrape_date': profile.get('scrape_date', 'Not found'),
                'name': profile.get('name', 'Not found'),
                'headline': profile.get('headline', 'Not found'),
                'location': profile.get('location', 'Not found'),
                'about': profile.get('about', 'Not found'),
                'skills': ', '.join(profile.get('skills', [])),
            }

            # Add experience data
            experiences = profile.get('experience', [])
            for i, exp in enumerate(experiences[:5]):  # Limit to 5 experiences
                prefix = f"experience_{i + 1}_"
                for key, value in exp.items():
                    flat_profile[prefix + key] = value

            # Add education data
            educations = profile.get('education', [])
            for i, edu in enumerate(educations[:3]):  # Limit to 3 educations
                prefix = f"education_{i + 1}_"
                for key, value in edu.items():
                    flat_profile[prefix + key] = value

            # Add certification data
            certifications = profile.get('certifications', [])
            for i, cert in enumerate(certifications[:5]):  # Limit to 5 certifications
                prefix = f"certification_{i + 1}_"
                for key, value in cert.items():
                    flat_profile[prefix + key] = value

            flattened_data.append(flat_profile)

        # Get all possible fields
        all_fields = set()
        for profile in flattened_data:
            all_fields.update(profile.keys())

        # Create a list of sorted fields with a specific order for better readability
        priority_fields = [
            'profile_url', 'scrape_date', 'name', 'headline', 'location', 'about', 'skills'
        ]

        # Sort the fields with priority fields first, then alphabetically
        sorted_fields = priority_fields + sorted([f for f in all_fields if f not in priority_fields])

        # Write to CSV
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=sorted_fields)
                writer.writeheader()
                for profile in flattened_data:
                    writer.writerow(profile)

            print(f"✅ Successfully saved data to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving to CSV: {e}")
            # Try saving to a different location if the first attempt failed
            try:
                backup_filename = f"linkedin_profiles_{int(time.time())}.csv"
                print(f"Attempting to save to alternate location: {backup_filename}")
                with open(backup_filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=sorted_fields)
                    writer.writeheader()
                    for profile in flattened_data:
                        writer.writerow(profile)
                print(f"✅ Successfully saved data to {backup_filename}")
                return True
            except Exception as e2:
                print(f"❌ Backup save failed: {e2}")
                return False

    def save_to_json(self, filename=None):
        """Save the scraped profiles to a JSON file"""
        if not self.profiles_data:
            print("❌ No profile data to save")
            return

        if not filename:
            filename = os.path.join(CONFIG["output_dir"], CONFIG["json_filename"])

        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(self.profiles_data, jsonfile, indent=4, ensure_ascii=False)

            print(f"✅ Successfully saved data to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving to JSON: {e}")
            # Try saving to a different location if the first attempt failed
            try:
                backup_filename = f"linkedin_profiles_{int(time.time())}.json"
                print(f"Attempting to save to alternate location: {backup_filename}")
                with open(backup_filename, 'w', encoding='utf-8') as jsonfile:
                    json.dump(self.profiles_data, jsonfile, indent=4, ensure_ascii=False)
                print(f"✅ Successfully saved data to {backup_filename}")
                return True
            except Exception as e2:
                print(f"❌ Backup save failed: {e2}")
                return False

    def visit_random_pages(self, num_pages=2):
        """Visit some random LinkedIn pages to mimic normal browsing"""
        random_pages = [
            "https://www.linkedin.com/feed/",
            "https://www.linkedin.com/mynetwork/",
            "https://www.linkedin.com/jobs/",
            "https://www.linkedin.com/notifications/"
        ]

        # Visit random pages
        for _ in range(random.randint(1, num_pages)):
            try:
                random_page = random.choice(random_pages)
                print(f"🌐 Visiting {random_page} to mimic normal browsing")
                self.driver.get(random_page)
                time.sleep(random.uniform(5, 10))
                self.perform_random_scrolls()
            except Exception as e:
                print(f"⚠️ Error during random page visit: {e}")
                # Continue even if random page visit fails

    def run(self, profile_urls):
        """Run the scraper on a list of profile URLs"""
        try:
            # Initialize the driver
            print("Initializing Chrome driver...")
            self.driver = self.create_stealth_driver()

            # Login to LinkedIn
            if self.login_to_linkedin():

                # Add a longer delay after login to avoid suspicion
                time.sleep(random.uniform(5, 10))

                # Visit some random LinkedIn pages to mimic normal browsing
                self.visit_random_pages()

                # Track successful and failed scrapes
                successful = 0
                failed = 0

                # Now scrape each profile
                for index, url in enumerate(profile_urls):
                    print(f"\n[{index + 1}/{len(profile_urls)}] 🔍 Scraping profile: {url}")
                    profile_data = self.scrape_profile(url)

                    if profile_data:
                        self.profiles_data.append(profile_data)
                        successful += 1
                        print(f"✅ Successfully scraped profile: {profile_data['name']}")
                    else:
                        failed += 1
                        print(f"❌ Failed to scrape profile: {url}")

                    # Save the data periodically in case of a crash
                    if (index + 1) % 3 == 0 or index == len(profile_urls) - 1:
                        print("\n💾 Saving intermediate results...")
                        self.save_to_csv()
                        self.save_to_json()

                    # Don't add delay after the last profile
                    if index < len(profile_urls) - 1:
                        # Add a substantial delay between profile visits
                        delay = random.uniform(CONFIG["min_delay"], CONFIG["max_delay"])
                        print(f"⏳ Waiting {delay:.1f} seconds before the next profile...")
                        time.sleep(delay)

                        # Visit a random page again to break the pattern
                        self.visit_random_pages(1)

                # Save the final data
                print("\n💾 Saving final results...")
                self.save_to_csv()
                self.save_to_json()

                print(f"\n📊 Scraping Summary:")
                print(f"✅ Successfully scraped: {successful} profiles")
                print(f"❌ Failed to scrape: {failed} profiles")

                return True

            return False

        except Exception as e:
            print(f"❌ An error occurred in the main scraping process: {e}")

            # Try to save any data that was collected before the error
            if self.profiles_data:
                print("Attempting to save data collected before the error...")
                self.save_to_csv(f"linkedin_recovery_{int(time.time())}.csv")
                self.save_to_json(f"linkedin_recovery_{int(time.time())}.json")

            return False

        finally:
            if self.driver:
                print("🔚 Closing browser...")
                try:
                    self.driver.quit()
                except Exception as e:
                    print(f"Note: Error while closing browser: {e}")


def main():
    # LinkedIn credentials - replace with your own
    linkedin_username = "choprakashish94@gmail.com"
    linkedin_password = "Harekrishna123@#$"

    # Create and run the scraper
    scraper = LinkedInScraper(linkedin_username, linkedin_password)
    scraper.run(profile_urls)


if __name__ == "__main__":
    main()