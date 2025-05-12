# pages/base_page.py
import time
import os
from datetime import datetime

class BasePage:
    """Base page object with common functionality for all pages"""
    
    def __init__(self, page):
        """Initialize base page with Playwright page object"""
        self.page = page
    
    def wait_for_loading(self, timeout=20000):
        """Wait for the Odoo loading indicator to disappear"""
        # First wait for the loading indicator to appear (if it will)
        try:
            self.page.wait_for_selector(".o_loading", state="visible", timeout=5000)
            # Then wait for it to disappear
            self.page.wait_for_selector(".o_loading", state="hidden", timeout=timeout)
        except:
            # If loading indicator never appears, that's fine
            pass
            
        # Wait for network requests to complete
        self.page.wait_for_load_state("networkidle", timeout=timeout)
    
    def navigate_to_module(self, module_name):
        """Navigate to a specific module from the main menu using the span selector
        
        Args:
            module_name: The name of the module to navigate to
        """
        # Click on the module in the side menu using the span with nav-title class
        module_selector = f"//span[@class='nav-title text-truncate ms-3' and @title='{module_name}']"
        
        # Make sure the menu item is visible first
        self.page.wait_for_selector(module_selector, state="visible", timeout=10000)
        
        # Click the module
        self.page.click(module_selector)
        
        # Wait for navigation to complete
        self.wait_for_loading()
        
        # Verify module loaded by checking for content area
        self.page.wait_for_selector("//div[contains(@class,'o_action_manager')]", 
                                  state="visible", 
                                  timeout=10000)
    
    def click_with_retry(self, selector, max_retries=3, timeout=1000):
        """Click with retry for handling potential flakiness
        
        Args:
            selector: Element selector to click
            max_retries: Maximum number of attempts
            timeout: Wait time between retries in ms
            
        Returns:
            bool: True if click was successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                # Wait for element to be visible and clickable
                self.page.wait_for_selector(selector, state="visible", timeout=timeout)
                self.page.click(selector)
                
                # Wait a moment after clicking to let the page react
                time.sleep(0.5)
                return True
            except Exception as e:
                if attempt == max_retries - 1:
                    # Take screenshot on final failure
                    self.take_screenshot(f"click_retry_failure_{selector.replace('/','_')}")
                    # Re-raise the exception on the last attempt
                    raise e
                
                # Wait before retrying
                self.page.wait_for_timeout(timeout)
        
        return False
    
    def get_element_text(self, selector, timeout=5000):
        """Get text content of an element
        
        Args:
            selector: Element selector
            timeout: Wait timeout in ms
            
        Returns:
            str: Text content of the element or None if not found
        """
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return self.page.text_content(selector).strip()
        except:
            return None
    
    def is_element_visible(self, selector, timeout=5000):
        """Check if element is visible
        
        Args:
            selector: Element selector
            timeout: Maximum wait time in ms
            
        Returns:
            bool: True if element is visible, False otherwise
        """
        try:
            return self.page.is_visible(selector, timeout=timeout)
        except:
            return False
    
    def take_screenshot(self, name):
        """Take a screenshot and save it with the given name
        
        Args:
            name: Base name for the screenshot
            
        Returns:
            str: Path to the saved screenshot
        """
        # Ensure directory exists
        os.makedirs("reports/screenshots", exist_ok=True)
        
        # First ensure any loading operations are complete
        self.wait_for_loading()
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        path = f"reports/screenshots/{filename}"
        
        # Take the screenshot after data is loaded
        self.page.screenshot(path=path)
        return path
    
    def fill_field(self, selector, value, clear_first=True):
        """Fill a form field with the given value
        
        Args:
            selector: Field selector
            value: Value to fill
            clear_first: Whether to clear the field first
        """
        self.page.wait_for_selector(selector, state="visible")
        
        if clear_first:
            # Clear the field first
            self.page.fill(selector, "")
            
        # Fill with the new value
        self.page.fill(selector, value)
    
    def select_dropdown_option(self, dropdown_selector, option_text):
        """Select an option from a dropdown by visible text
        
        Args:
            dropdown_selector: Selector for the dropdown
            option_text: Text of the option to select
        """
        # Click to open the dropdown
        self.page.click(dropdown_selector)
        
        # Wait for dropdown options to appear
        self.page.wait_for_timeout(500)  
        
        # Click the option with the matching text
        option_selector = f"//li[contains(@class, 'ui-menu-item')]/a[contains(text(), '{option_text}')]"
        self.page.click(option_selector)
    
    def wait_for_notification(self, expected_text=None, timeout=10000):
        """Wait for notification and optionally verify its text
        
        Args:
            expected_text: Expected notification text (optional)
            timeout: Maximum wait time in ms
            
        Returns:
            bool: True if notification appeared with expected text, False otherwise
        """
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