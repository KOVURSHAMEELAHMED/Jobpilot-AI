# 📁 backend/auto_job_applicator.py
"""
OFF-CAMPUS AUTO JOB APPLICATOR
Automated job application system using Selenium
"""

import json
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class OffCampusAutoApplicator:
    """Main controller for automated job applications"""
    
    def __init__(self, config_path='config/settings.json'):
        self.config = self.load_configuration(config_path)
        self.driver = None
        self.current_portal = None
        self.applications_today = 0
        self.setup_logger()
        
    def setup_logger(self):
        """Setup application logger"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - OFF_CAMPUS - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/offcampus_applications.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('OffCampusApplicator')
    
    def load_configuration(self, config_path):
        """Load configuration from JSON file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Security warning for credentials
        if 'linkedin' in config and 'password' in config['linkedin']:
            self.logger.warning("Credentials loaded. Ensure config file is encrypted in production.")
        
        return config
    
    def initialize_chrome_driver(self):
        """Initialize Chrome with job application profile"""
        chrome_options = webdriver.ChromeOptions()
        
        # Job application specific settings
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument(f"user-data-dir={self.config['chrome_profile_path']}")
        
        # Anti-detection measures
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Load extension if available
        if self.config.get('browser_extension_path'):
            chrome_options.add_extension(self.config['browser_extension_path'])
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Mask Selenium detection
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.driver.implicitly_wait(10)
        self.logger.info("Chrome driver initialized for Off-Campus applications")
    
    def authenticate_portal(self, portal_name):
        """Authenticate to job portals"""
        auth_handlers = {
            'linkedin': self.authenticate_linkedin,
            'indeed': self.authenticate_indeed,
            'glassdoor': self.authenticate_glassdoor,
            'naukri': self.authenticate_naukri,
            'angelco': self.authenticate_angelco
        }
        
        if portal_name in auth_handlers:
            self.current_portal = portal_name
            return auth_handlers[portal_name]()
        else:
            self.logger.error(f"Unsupported portal: {portal_name}")
            return False
    
    def authenticate_linkedin(self):
        """LinkedIn authentication for job applications"""
        try:
            self.logger.info("🔐 Authenticating to LinkedIn...")
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for login page
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            # Enter credentials
            username_field = self.driver.find_element(By.ID, "username")
            username_field.clear()
            username_field.send_keys(self.config['linkedin']['username'])
            
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.config['linkedin']['password'])
            
            # Submit login
            password_field.send_keys(Keys.RETURN)
            
            # Wait for successful login
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "global-nav"))
            )
            
            self.logger.info("✅ LinkedIn authentication successful")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ LinkedIn authentication failed: {str(e)}")
            return False
    
    def search_offcampus_jobs(self, keywords, location="Remote", experience_level="Entry Level"):
        """Search for off-campus job opportunities"""
        search_queries = {
            'linkedin': f"https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}&f_TPR=r86400&f_E=2",
            'indeed': f"https://www.indeed.com/jobs?q={keywords}&l={location}&fromage=1"
        }
        
        if self.current_portal in search_queries:
            search_url = search_queries[self.current_portal]
            self.logger.info(f"🔍 Searching jobs: {keywords} in {location}")
            self.driver.get(search_url)
            time.sleep(3)
            
            # Apply filters for off-campus positions
            self.apply_job_filters(experience_level)
            
            # Collect job listings
            return self.collect_job_listings()
        
        return []
    
    def apply_job_filters(self, experience_level):
        """Apply filters for off-campus job search"""
        try:
            if self.current_portal == 'linkedin':
                # Click experience level filter
                exp_filter = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Experience level')]"))
                )
                exp_filter.click()
                time.sleep(1)
                
                # Select entry level
                entry_level = self.driver.find_element(By.XPATH, f"//label[contains(text(), '{experience_level}')]")
                entry_level.click()
                time.sleep(1)
                
                # Apply filter
                apply_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Apply')]")
                apply_btn.click()
                time.sleep(2)
                
        except Exception as e:
            self.logger.warning(f"Could not apply filters: {str(e)}")
    
    def collect_job_listings(self, max_jobs=20):
        """Collect job listings from current search"""
        jobs = []
        
        # Scroll to load more jobs
        self.scroll_for_more_jobs()
        
        if self.current_portal == 'linkedin':
            job_cards = self.driver.find_elements(By.CLASS_NAME, "job-card-container")
            
            for card in job_cards[:max_jobs]:
                try:
                    job_info = self.extract_linkedin_job_info(card)
                    if job_info:
                        jobs.append(job_info)
                except Exception as e:
                    continue
        
        self.logger.info(f"📋 Found {len(jobs)} job listings")
        return jobs
    
    def extract_linkedin_job_info(self, job_card):
        """Extract job information from LinkedIn card"""
        try:
            title_element = job_card.find_element(By.CLASS_NAME, "job-card-list__title")
            company_element = job_card.find_element(By.CLASS_NAME, "job-card-container__company-name")
            location_element = job_card.find_element(By.CLASS_NAME, "job-card-container__metadata-item")
            
            job_link = job_card.find_element(By.TAG_NAME, "a").get_attribute("href")
            
            return {
                'title': title_element.text.strip(),
                'company': company_element.text.strip(),
                'location': location_element.text.strip(),
                'portal': 'linkedin',
                'link': job_link,
                'easy_apply': 'Easy Apply' in job_card.text,
                'collected_at': datetime.now().isoformat()
            }
        except:
            return None
    
    def scroll_for_more_jobs(self):
        """Scroll page to load more job listings"""
        try:
            for _ in range(3):  # Scroll 3 times
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(2)
        except:
            pass
    
    def process_job_application(self, job_info, resume_data):
        """Process a single job application"""
        if self.applications_today >= self.config.get('daily_limit', 15):
            self.logger.warning("⚠️ Daily application limit reached")
            return False
        
        try:
            self.logger.info(f"📄 Processing application: {job_info['title']} at {job_info['company']}")
            
            # Navigate to job page
            self.driver.get(job_info['link'])
            time.sleep(3)
            
            # Check if already applied
            if self.check_already_applied():
                self.logger.info("Already applied to this position")
                return False
            
            # Attempt Easy Apply
            if job_info.get('easy_apply', False):
                return self.execute_easy_apply(resume_data)
            else:
                return self.apply_external_redirect(resume_data)
                
        except Exception as e:
            self.logger.error(f"Application failed: {str(e)}")
            return False
    
    def execute_easy_apply(self, resume_data):
        """Execute LinkedIn Easy Apply"""
        try:
            # Click Easy Apply button
            easy_apply_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "jobs-apply-button"))
            )
            easy_apply_btn.click()
            time.sleep(2)
            
            # Fill application form
            application_success = self.fill_application_form(resume_data)
            
            if application_success:
                self.applications_today += 1
                self.log_successful_application()
                
            return application_success
            
        except Exception as e:
            self.logger.error(f"Easy Apply failed: {str(e)}")
            return False
    
    def fill_application_form(self, resume_data):
        """Fill job application form with resume data"""
        try:
            # Fill personal information
            self.fill_personal_info(resume_data)
            
            # Fill contact information
            self.fill_contact_info(resume_data)
            
            # Answer screening questions
            self.answer_screening_questions(resume_data)
            
            # Upload resume if needed
            self.upload_resume_file()
            
            # Submit application
            submit_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Submit application']"))
            )
            submit_btn.click()
            time.sleep(3)
            
            # Verify submission
            if self.verify_application_submission():
                self.logger.info("✅ Application submitted successfully")
                return True
            
        except Exception as e:
            self.logger.error(f"Form filling failed: {str(e)}")
        
        return False
    
    def fill_personal_info(self, resume_data):
        """Fill personal information fields"""
        field_mappings = {
            'firstName': resume_data.get('first_name', ''),
            'lastName': resume_data.get('last_name', ''),
            'address': resume_data.get('address', '')
        }
        
        for field_name, value in field_mappings.items():
            try:
                element = self.driver.find_element(By.NAME, field_name)
                element.clear()
                element.send_keys(value)
                time.sleep(0.5)
            except:
                continue
    
    def run_daily_application_cycle(self):
        """Main execution cycle for daily job applications"""
        self.logger.info("🚀 Starting Off-Campus Auto Job Application Cycle")
        
        try:
            self.initialize_chrome_driver()
            
            # Authenticate to portals
            for portal in self.config['active_portals']:
                if self.authenticate_portal(portal):
                    # Load resume data
                    resume_data = self.load_resume_data()
                    
                    # Process each job search
                    for search in self.config['job_searches']:
                        jobs = self.search_offcampus_jobs(
                            keywords=search['keywords'],
                            location=search.get('location', 'Remote'),
                            experience_level=search.get('experience_level', 'Entry Level')
                        )
                        
                        # Filter and apply to jobs
                        filtered_jobs = self.filter_relevant_jobs(jobs, resume_data)
                        
                        for job in filtered_jobs[:self.config.get('max_per_search', 5)]:
                            if self.process_job_application(job, resume_data):
                                time.sleep(self.config.get('delay_between_applications', 30))
            
        except Exception as e:
            self.logger.error(f"Application cycle failed: {str(e)}")
        
        finally:
            if self.driver:
                self.driver.quit()
            self.logger.info("🏁 Application cycle completed")