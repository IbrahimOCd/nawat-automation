# pages/base_page.py
import time
import os
from datetime import datetime

class BasePage:
    """Base page object with common functionality for all pages"""
    
    def __init__(self, page):
        """Initialize base page with Playwright page object"""
        self.page = page
        self.default_timeout = 8000  # Lower default timeout for faster tests
    
    def wait_for_loading(self, timeout=8000):
        """Wait for the Odoo loading indicator to disappear"""
        try:
            # First try to wait for the loading indicator to appear
            self.page.wait_for_selector(".o_loading", state="visible", timeout=1000)
            # Then wait for it to disappear
            self.page.wait_for_selector(".o_loading", state="hidden", timeout=timeout)
        except:
            # If loading indicator never appears, that's fine
            pass
            
        try:
            # Wait for network requests to complete
            self.page.wait_for_load_state("networkidle", timeout=timeout)
        except:
            # If timeout occurs on networkidle, we can still continue
            pass
    
    def navigate_to_module(self, module_name):
        """Navigate to a specific module from the main menu using the span selector"""
        # Click on the module in the side menu using the span with nav-title class
        module_selector = f"//span[@class='nav-title text-truncate ms-3' and @title='{module_name}']"
        
        try:
            # Make sure the menu item is visible first
            self.page.wait_for_selector(module_selector, state="visible", timeout=8000)
            
            # Click the module
            self.page.click(module_selector)
            
            # Wait for navigation to complete
            self.wait_for_loading()
            
            # Verify module loaded by checking for content area
            self.page.wait_for_selector("//div[contains(@class,'o_action_manager')]", 
                                      state="visible", 
                                      timeout=8000)
            return True
        except Exception as e:
            print(f"Error navigating to module {module_name}: {str(e)}")
            return False
    
    def click_with_retry(self, selector, max_retries=3, timeout=1000):
        """Click with retry for handling potential flakiness"""
        for attempt in range(max_retries):
            try:
                # Wait for element to be visible and clickable
                self.page.wait_for_selector(selector, state="visible", timeout=timeout)
                self.page.click(selector)
                
                # Short wait after clicking
                time.sleep(0.3)
                return True
            except Exception as e:
                if attempt == max_retries - 1:
                    # Only take screenshot on final failure to save time
                    filename = selector.replace('/', '_').replace('\\', '_').replace(':', '_')
                    self.take_screenshot(f"click_retry_failure_{filename}")
                    # Re-raise the exception on the last attempt
                    raise e
                
                # Shorter wait before retrying
                time.sleep(0.5)
        
        return False
    
    def get_element_text(self, selector, timeout=5000):
        """Get text content of an element"""
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return self.page.text_content(selector).strip()
        except:
            return None
    
    def is_element_visible(self, selector, timeout=3000):
        """Check if element is visible - with reduced timeout"""
        try:
            return self.page.is_visible(selector, timeout=timeout)
        except:
            return False
    
    def take_screenshot(self, name):
        """Take a screenshot and save it with the given name"""
        # Ensure directory exists
        os.makedirs("reports/screenshots", exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        path = f"reports/screenshots/{filename}"
        
        # Take the screenshot
        try:
            self.page.screenshot(path=path)
            return path
        except:
            print(f"Failed to take screenshot {name}")
            return None
    
    def is_enabled(self, selector):
        """Check if element is enabled (not disabled)"""
        try:
            element = self.page.query_selector(selector)
            if element:
                disabled = element.get_attribute("disabled")
                return disabled is None or disabled.lower() != "true"
            return False
        except:
            return False
            
    def fill_field(self, selector, value, clear_first=True):
        """Fill a form field with the given value"""
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=5000)
            
            if clear_first:
                # Clear the field first
                self.page.fill(selector, "")
                
            # Fill with the new value
            self.page.fill(selector, value)
            return True
        except:
            return False
    
    def select_dropdown_option(self, dropdown_selector, option_text):
        """Select an option from a dropdown by visible text"""
        try:
            # Click to open the dropdown
            self.page.click(dropdown_selector)
            
            # Wait briefly for dropdown options to appear
            time.sleep(0.3)
            
            # Click the option with the matching text
            option_selector = f"//li[contains(@class, 'ui-menu-item')]/a[contains(text(), '{option_text}')]"
            self.page.click(option_selector)
            return True
        except:
            return False
    
    def wait_for_notification(self, expected_text=None, timeout=5000):
        """Wait for notification and optionally verify its text"""
        try:
            # Wait for notification to appear (adjust selector for Odoo notifications)
            notification = self.page.wait_for_selector(".o_notification", state="visible", timeout=timeout)
            
            # If expected text is provided, verify the notification content
            if expected_text and notification:
                actual_text = self.page.text_content(".o_notification_content")
                return expected_text.lower() in actual_text.lower()
            
            return True
        except:
            return False