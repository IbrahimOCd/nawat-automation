# pages/login_page.py
from .base_page import BasePage
import time
import os

class LoginPage(BasePage):
    # Locators
    USERNAME_INPUT = "input[name='login']"
    PASSWORD_INPUT = "input[name='password']"
    LOGIN_BUTTON = "button[type='submit']"
    ERROR_MESSAGE = ".alert-danger"
    MAIN_NAVBAR = "//span[@class='nav-title text-truncate ms-3']"
    APP_CONTENT = "//div[contains(@class,'o_action_manager')]"
    
    # Language selectors - updated based on screenshot evidence
    LANGUAGE_DROPDOWN = "//button[contains(@class,'btn border-0')]"
    LANGUAGE_OPTION_EN = "//a[@title='English (US)']"
    LANGUAGE_OPTION_FR = "//a[@title=' Français']"
    LANGUAGE_OPTION_AR = "//a[@title=' الْعَرَبيّة']"
    
    # Labels in different languages (based on your screenshots)
    LABELS = {
        "en": {
            "username_label": "Username",
            "password_label": "Password",
            "submit_button": "Log in",
            "error_invalid": "Wrong login/password"
        },
        "fr": {
            "username_label": "Identifiant",
            "password_label": "Mot de passe",
            "submit_button": "Se connecter",
            "error_invalid": "Mauvais nom d'utilisateur/mot de passe"
        },
        "ar": {
            "username_label": "اسم المستخدم",
            "password_label": "كلمة المرور",
            "submit_button": "تسجيل الدخول",
            "error_invalid": "خطأ في اسم المستخدم أو كلمة المرور"
        }
    }
    
    # Mapping of language codes to language dropdown options
    LANGUAGE_OPTIONS = {
        "en": LANGUAGE_OPTION_EN,
        "fr": LANGUAGE_OPTION_FR,
        "ar": LANGUAGE_OPTION_AR
    }
    
    def __init__(self, page):
        super().__init__(page)
        self.page = page
        self.current_language = "en"  # Default language
    
    def navigate(self):
        """Navigate to the login page"""
        self.page.goto("https://dev.nawat.ma/web/login")
        # Wait for login form to be fully loaded
        self.page.wait_for_selector(self.USERNAME_INPUT, state="visible")
        self.page.wait_for_selector(self.PASSWORD_INPUT, state="visible")
        self.page.wait_for_selector(self.LOGIN_BUTTON, state="visible")
    
    def switch_language(self, language_code):
        """
        Switch the interface language
        
        Args:
            language_code: 'en' for English, 'fr' for French, 'ar' for Arabic
        
        Returns:
            bool: True if switch was successful, False otherwise
        """
        if language_code not in self.LANGUAGE_OPTIONS:
            print(f"Unsupported language code: {language_code}")
            return False
        
        try:
            # Find and click the language dropdown
            self.page.click(self.LANGUAGE_DROPDOWN)
            
            # Wait for dropdown to appear
            
            # Click on the language option
            self.page.click(self.LANGUAGE_OPTIONS[language_code])
            
            # Wait for page to reload/update
            self.page.wait_for_load_state("networkidle")
            
            # Take a screenshot after language switch
            os.makedirs("reports/screenshots", exist_ok=True)
            self.page.screenshot(path=f"reports/screenshots/language_switch_{language_code}.png")
            
            # Set current language
            self.current_language = language_code
            return True
                
        except Exception as e:
            print(f"Error switching language: {str(e)}")
            # Take screenshot of the failure
            os.makedirs("reports/screenshots", exist_ok=True)
            self.page.screenshot(path=f"reports/screenshots/language_switch_failure_{language_code}.png")
            return False
    
    def verify_login_form_elements(self):
        """
        Verify that login form elements match the current language
        
        Returns:
            dict: Results of verification for each element
        """
        results = {}
        lang = self.current_language
        
        try:
            # Check username label
            username_label_element = self.page.locator("label", has_text=self.LABELS[lang]["username_label"])
            results["username_label"] = username_label_element.is_visible()
            
            # Check password label
            password_label_element = self.page.locator("label", has_text=self.LABELS[lang]["password_label"])
            results["password_label"] = password_label_element.is_visible()
            
            # Check submit button text
            button_text = self.page.text_content(self.LOGIN_BUTTON)
            results["submit_button"] = self.LABELS[lang]["submit_button"] in button_text
            
            # Take a screenshot for verification
            os.makedirs("reports/screenshots", exist_ok=True)
            self.page.screenshot(path=f"reports/screenshots/verify_elements_{lang}.png")
            
            return results
            
        except Exception as e:
            print(f"Error verifying form elements: {str(e)}")
            os.makedirs("reports/screenshots", exist_ok=True)
            self.page.screenshot(path=f"reports/screenshots/verify_elements_failure_{lang}.png")
            return {"error": str(e)}
    
    def login(self, username, password):
        """Login with the given credentials"""
        # Clear the fields first (to ensure no residual data)
        self.page.fill(self.USERNAME_INPUT, "")
        self.page.fill(self.PASSWORD_INPUT, "")
        
        # Fill the fields with provided credentials
        self.page.fill(self.USERNAME_INPUT, username)
        self.page.fill(self.PASSWORD_INPUT, password)
        
        # Click login button
        self.page.click(self.LOGIN_BUTTON)
        
        try:
            # First check if login was unsuccessful and error is shown
            if self.page.is_visible(".alert-danger, .o_error_detail", timeout=5000):
                # Take screenshot of the error
                os.makedirs("reports/screenshots", exist_ok=True)
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                self.page.screenshot(path=f"reports/screenshots/login_error_{timestamp}.png")
                return False
                
            # If no error, wait for main navbar indicating successful login
            self.page.wait_for_selector(self.MAIN_NAVBAR, state="visible", timeout=15000)
            
            # Wait for app content to be loaded
            self.page.wait_for_selector(self.APP_CONTENT, state="visible", timeout=15000)
            
            # Give additional time for data to fully load
            
            # Check if we're really logged in by verifying user menu is accessible
            if not self.page.is_visible(self.MAIN_NAVBAR, timeout=2000):
                return False
                
            # Take screenshot of successful login
            os.makedirs("reports/screenshots", exist_ok=True)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            self.page.screenshot(path=f"reports/screenshots/login_success_{timestamp}.png")
            
            return True
        except Exception as e:
            # Take screenshot for debugging
            os.makedirs("reports/screenshots", exist_ok=True)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            self.page.screenshot(path=f"reports/screenshots/login_failure_{timestamp}.png")
            print(f"Login failed with error: {str(e)}")
            return False
    
    def get_error_message(self):
        """Get the error message text if login failed"""
        for selector in [".alert-danger", ".o_error_detail"]:
            if self.page.is_visible(selector):
                return self.page.text_content(selector).strip()
        return None
    
    def verify_error_message(self):
        """
        Verify that the error message matches the expected message in the current language
        
        Returns:
            bool: True if error message matches expected text for current language
        """
        error_message = self.get_error_message()
        if not error_message:
            return False
            
        expected_text = self.LABELS[self.current_language]["error_invalid"]
        return expected_text.lower() in error_message.lower()