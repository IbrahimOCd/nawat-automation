# pages/access/class_filter_page.py
from ...base_page import BasePage
import time
import os
import allure

class ClassFilterPage(BasePage):
    """Page object for filtering students by class levels"""
    
    # Navigation selectors
    WORKSPACE_BUTTON = "//button[@title='Espace de travail']"
    ACCESS_MODULE = "(//a[@data-menu-xmlid='acces.acces'])[3]"
    CARTE_SCOLAIRE_MENU = "(//span[text()='Carte Scolaire'])[2]"
    APPRENANT_SUBMENU = "(//a[@href='#menu_id=108&action=405'])[2]"
    
    # Sidebar selectors
    SIDEBAR_ITEM_BASE = "//div[contains(@class,'o_search_panel_label d-flex')]"
    ITEM_TITLE = "span.o_search_panel_label_title"
    
    # Student card selectors
    STUDENT_CARDS = "(//div[contains(@class,'oe_kanban_global_click o_kanban_record_has_image_fill')])"
    NO_STUDENTS_MESSAGE = "//div[@class='o_nocontent_help']//p[1]"
    STUDENT_CLASS = "(//i[contains(@class,'icon na-layer-group-2')]/following-sibling::span)"
    STUDENT_NAME = "(//strong[@class='o_kanban_record_title text-truncate']//span)"
    STUDENT_ID_SELECTOR = "(//i[contains(@class,'icon na-input-numeric')]/following-sibling::span)"  # Added selector for student ID
    
    def __init__(self, page):
        super().__init__(page)
        self.page = page
        # Reduce timeouts for faster execution
        self.wait_timeout = 5000  # 5 seconds timeout
    
    def navigate_from_login(self):
        """Navigate to the student page through the menu structure after login"""
        self.click_with_retry(self.WORKSPACE_BUTTON)
        self.click_with_retry(self.ACCESS_MODULE)
        self.click_with_retry(self.CARTE_SCOLAIRE_MENU)
        self.click_with_retry(self.APPRENANT_SUBMENU)
        
        # Create screenshots directory if it doesn't exist
        os.makedirs("reports/screenshots", exist_ok=True)
    
    def wait_for_page_loaded(self):
        """Wait for the page to be fully loaded"""
        try:
            # Wait for loading to complete with reduced timeout
            self.page.wait_for_load_state("networkidle", timeout=self.wait_timeout)
        except:
            # If timeout occurs, just continue
            pass
    
    def get_sidebar_item(self, index):
        """
        Get a sidebar item by its index (1-based)
        
        Args:
            index: 1-based index of the sidebar item
            
        Returns:
            tuple: (element, title)
        """
        try:
            # Construct XPath for the item
            item_selector = f"({self.SIDEBAR_ITEM_BASE})[{index}]"
            
            # Try to find the item with reduced timeout
            item = self.page.query_selector(item_selector)
            
            if not item:
                return None, f"Item {index}"
            
            # Get the title
            title_element = item.query_selector(self.ITEM_TITLE)
            title = title_element.text_content().strip() if title_element else f"Item {index}"
            
            # Return the element and title
            return item, title
        except Exception as e:
            return None, f"Error Item {index}"
    
    def click_sidebar_item(self, item, title):
        """
        Click on a sidebar item
        
        Args:
            item: The sidebar item element
            title: The title of the item
            
        Returns:
            bool: True if click was successful
        """
        try:
            # Click on the item (no screenshots for speed)
            item.click()
            return True
        except Exception as e:
            return False
    
    def is_class_item(self, title):
        """
        Check if an item is a class by looking for parentheses in the title
        
        Args:
            title: The title of the item
            
        Returns:
            bool: True if it's a class (has parentheses), False otherwise
        """
        return "(" in title and ")" in title
    
    
    def expand_all_items(self):
        """
        Expand all items in the sidebar
        
        Returns:
            list: List of all item titles that were clicked
        """
        clicked_items = []
        current_index = 1
        max_attempts = 100  # Safety limit
        
        # Click on each item in the sidebar
        while current_index <= max_attempts:
            try:
                # Get the item
                item, title = self.get_sidebar_item(current_index)
                
                # If item doesn't exist, we've reached the end
                if not item:
                    break
                
                # Click on the item
                self.click_sidebar_item(item, title)
                clicked_items.append(title)
                
                # Move to the next item
                current_index += 1
            except:
                # Just move to the next item on error
                current_index += 1
        
        return clicked_items
    
    def has_students(self):
        """
        Check if there are any students displayed
        
        Returns:
            bool: True if there are students, False if no students
        """
        try:
            # Check for "no students" message with reduced timeout
            no_students = self.page.query_selector(self.NO_STUDENTS_MESSAGE)
            if no_students:
                return False
            
            # Check if there are student cards
            student_cards = self.page.query_selector_all(self.STUDENT_CARDS)
            return len(student_cards) > 0
        except:
            return False
    
    def verify_students_match_class(self, class_name):
        """
        Verify that all students have the correct class
        
        Args:
            class_name: The expected class name
            
        Returns:
            tuple: (success, details)
        """
        try:
            # Get all student cards
            student_cards = self.page.query_selector_all(self.STUDENT_CARDS)
            total = len(student_cards)
            matching = 0
            mismatched_students = []
            
            # Check each student
            for i, card in enumerate(student_cards):
                try:
                    # Get student name
                    name_element = card.query_selector(self.STUDENT_NAME_SELECTOR)
                    student_name = name_element.text_content().strip() if name_element else f"Student {i+1}"
                    
                    # Get student ID
                    id_element = card.query_selector(self.STUDENT_ID_SELECTOR)
                    student_id = id_element.text_content().strip() if id_element else "Unknown ID"
                    
                    # Get the class element
                    class_element = card.query_selector(self.STUDENT_CLASS_SELECTOR)
                    
                    if class_element:
                        # Get the actual class
                        actual_class = class_element.text_content().strip()
                        
                        if actual_class == class_name:
                            matching += 1
                        else:
                            # Record detailed information about the mismatched student
                            mismatched_students.append({
                                "index": i+1,
                                "name": student_name,
                                "id": student_id,
                                "expected_class": class_name,
                                "actual_class": actual_class
                            })
                except:
                    continue
            
            # Calculate result
            success = len(mismatched_students) == 0
            details = {
                "total": total,
                "matching": matching,
                "mismatched_students": mismatched_students
            }
            
            return success, details
        except Exception as e:
            return False, {"error": str(e)}