# pages/base_page.py
import time

class BasePage:
    def __init__(self, page):
        self.page = page
    
    def wait_for_loading(self):
        """Wait for the Odoo loading indicator to disappear"""
        # First wait for the loading indicator to appear (if it will)
        try:
            self.page.wait_for_selector(".o_loading", state="visible", timeout=5000)
            # Then wait for it to disappear
            self.page.wait_for_selector(".o_loading", state="hidden", timeout=20000)
        except:
            # If loading indicator never appears, that's fine
            pass
            
        # Additional wait to ensure data is loaded
        time.sleep(2)
    
    def navigate_to_module(self, module_name):
        """Navigate to a specific module from the main menu using the working selector"""
        # Click on the module in the side menu using the span with nav-title class
        self.page.click(f"//span[@class='nav-title text-truncate ms-3' and @title='{module_name}']")
        
        # Wait for navigation to complete
        self.wait_for_loading()
        
        # Verify module loaded by checking for content area
        self.page.wait_for_selector("//div[contains(@class,'o_action_manager')]", state="visible", timeout=10000)
        
        # Additional wait for data to load
        time.sleep(2)
    

    
    def click_with_retry(self, selector, max_retries=3):
        """Click with retry for handling potential flakiness"""
        for attempt in range(max_retries):
            try:
                self.page.click(selector)
                # Wait a moment after clicking to let the page react
                time.sleep(1)
                return True
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                self.page.wait_for_timeout(1000)  # Wait before retrying
        return False
    
    def get_element_text(self, selector):
        """Get text content of an element"""
        return self.page.text_content(selector)
    
    def is_element_visible(self, selector):
        """Check if element is visible"""
        return self.page.is_visible(selector)
    
    def take_screenshot(self, name):
        """Take a screenshot and save it with the given name"""
        # First ensure any loading operations are complete
        self.wait_for_loading()
        
        # Take the screenshot after data is loaded
        self.page.screenshot(path=f"reports/screenshots/{name}.png")