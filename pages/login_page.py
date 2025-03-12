# pages/login_page.py
from .base_page import BasePage
import time

class LoginPage(BasePage):
    # Locators
    USERNAME_INPUT = "input[name='login']"
    PASSWORD_INPUT = "input[name='password']"
    LOGIN_BUTTON = "button[type='submit']"
    ERROR_MESSAGE = ".o_error_detail"
    MAIN_NAVBAR = "//span[@class='nav-title text-truncate ms-3' ]"
    APP_CONTENT = "//div[contains(@class,'o_action_manager')]"
    
    def __init__(self, page):
        super().__init__(page)
        self.page = page
    
    def navigate(self):
        """Navigate to the login page"""
        self.page.goto("https://dev.nawat.ma/web/login")
        # Wait for login form to be fully loaded
        self.page.wait_for_selector(self.USERNAME_INPUT, state="visible")
        self.page.wait_for_selector(self.PASSWORD_INPUT, state="visible")
        self.page.wait_for_selector(self.LOGIN_BUTTON, state="visible")
    
    def login(self, username, password):
        """Login with the given credentials"""
        self.page.fill(self.USERNAME_INPUT, username)
        self.page.fill(self.PASSWORD_INPUT, password)
        self.page.click(self.LOGIN_BUTTON)
        
        try:
            # First check if login was unsuccessful and error is shown
            if self.page.is_visible(self.ERROR_MESSAGE, timeout=5000):
                return False
                
            # If no error, wait for main navbar indicating successful login
            self.page.wait_for_selector(self.MAIN_NAVBAR, state="visible", timeout=15000)
            
            # Wait for app content to be loaded
            self.page.wait_for_selector(self.APP_CONTENT, state="visible", timeout=15000)
            
            # Give additional time for data to fully load
            time.sleep(3)
            
            # Check if we're really logged in by verifying user menu is accessible
            if not self.page.is_visible(self.MAIN_NAVBAR, timeout=2000):
                return False
                
            return True
        except Exception as e:
            # Take screenshot for debugging
            self.page.screenshot(path="reports/screenshots/login_failure.png")
            print(f"Login failed with error: {str(e)}")
            return False