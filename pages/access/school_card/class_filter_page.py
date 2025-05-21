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
    ITEM_TITLE = "//span[contains(@class,'o_search_panel_label_title text-truncate')]"
    SIDEBAR_CONTAINER = "//div[contains(@class,'o_search_panel')]"
    
    # Student card selectors
    STUDENT_CARDS = "(//div[contains(@class,'oe_kanban_global_click o_kanban_record_has_image_fill')])"
    NO_STUDENTS_MESSAGE = "//div[@class='o_nocontent_help']//p[1]"
    STUDENT_CLASS = "(//i[contains(@class,'icon na-layer-group-2')]/following-sibling::span)"
    STUDENT_NAME = "(//strong[@class='o_kanban_record_title text-truncate']//span)"
    STUDENT_ID_SELECTOR = "(//i[contains(@class,'icon na-input-numeric')]/following-sibling::span)"
    
    # Loading indicators
    LOADING_INDICATOR = "//div[contains(@class,'o_loading')]"
    KANBAN_VIEW = "//div[contains(@class,'o_kanban_view')]"
    
    def __init__(self, page):
        super().__init__(page)
        self.page = page
        # Faster timeouts for speed
        self.wait_timeout = 5000   # 5 seconds for critical operations
        self.quick_timeout = 1500  # 1.5 seconds for quick checks
        self.micro_timeout = 500   # 0.5 seconds for very quick checks
    
    def navigate_from_login(self):
        """Navigate to the student page through the menu structure after login"""
        self.click_with_retry(self.WORKSPACE_BUTTON)
        self.click_with_retry(self.ACCESS_MODULE)
        self.click_with_retry(self.CARTE_SCOLAIRE_MENU)
        self.click_with_retry(self.APPRENANT_SUBMENU)
        
        # Wait for initial page load
        self.wait_for_page_loaded()
        
        # Create screenshots directory if it doesn't exist
        os.makedirs("reports/screenshots", exist_ok=True)
    
    def wait_for_page_loaded(self):
        """Wait for the page to be fully loaded with proper indicators - FAST VERSION"""
        try:
            # Quick network check
            self.page.wait_for_load_state("domcontentloaded", timeout=self.micro_timeout)
            
            # Skip loading indicator check for speed
            
            # Quick check for kanban view
            try:
                self.page.wait_for_selector(self.KANBAN_VIEW, timeout=self.quick_timeout)
            except:
                pass  # Continue if not found quickly
            
            # Minimal wait for dynamic content
            time.sleep(0.2)
            
        except Exception as e:
            # Fallback: minimal wait
            time.sleep(0.5)
    
    def expand_all_sidebar_items(self):
        """
        Expand all sidebar items FAST with better debugging
        
        Returns:
            bool: True if expansion was successful
        """
        try:
            print(f"🔍 Looking for sidebar items with selector: {self.SIDEBAR_ITEM_BASE}")
            
            # Get initial items
            sidebar_elements = self.page.query_selector_all(self.SIDEBAR_ITEM_BASE)
            print(f"📦 Found {len(sidebar_elements)} sidebar elements initially")
            
            if len(sidebar_elements) == 0:
                # Try alternative selectors
                alt_selectors = [
                    "//div[contains(@class,'o_search_panel_label')]",
                    "//div[contains(@class,'search_panel_label')]", 
                    "//*[contains(@class,'panel_label')]",
                    "//div[@class='o_search_panel_label d-flex']"
                ]
                
                for selector in alt_selectors:
                    elements = self.page.query_selector_all(selector)
                    print(f"🔄 Trying {selector}: {len(elements)} elements")
                    if len(elements) > 0:
                        sidebar_elements = elements
                        break
            
            # Click on each item to expand - FAST
            clicked = 0
            for element in sidebar_elements:
                try:
                    # Fast click without scrolling or waiting
                    element.click()
                    clicked += 1
                except:
                    continue
            
            print(f"✅ Clicked {clicked} elements")
            
            # Single wait for all expansions to complete
            time.sleep(1.5)  # Slightly longer to ensure expansion
            
            return clicked > 0
            
        except Exception as e:
            print(f"❌ Expansion error: {e}")
            return False
    
    def get_all_sidebar_items(self):
        """
        Get all sidebar items FAST with better debugging
        
        Returns:
            list: List of (element, title, is_class) tuples
        """
        items = []
        try:
            # Get all sidebar items with debugging
            sidebar_elements = self.page.query_selector_all(self.SIDEBAR_ITEM_BASE)
            print(f"📋 Found {len(sidebar_elements)} sidebar elements after expansion")
            
            if len(sidebar_elements) == 0:
                # Try alternative selectors if main one fails
                alt_selectors = [
                    "//div[contains(@class,'o_search_panel_label')]",
                    "//div[contains(@class,'search_panel_label')]", 
                    "//*[contains(@class,'panel_label')]"
                ]
                
                for selector in alt_selectors:
                    sidebar_elements = self.page.query_selector_all(selector)
                    print(f"🔄 Trying alternative {selector}: {len(sidebar_elements)} elements")
                    if len(sidebar_elements) > 0:
                        break
            
            # Process elements
            class_count = 0
            for i, element in enumerate(sidebar_elements):
                try:
                    # Get the title - try multiple approaches
                    title_element = element.query_selector(self.ITEM_TITLE)
                    if not title_element:
                        # Try alternative title selectors
                        title_element = element.query_selector("span")
                    
                    title = title_element.text_content().strip() if title_element else ""
                    
                    # Skip empty titles
                    if not title:
                        continue
                    
                    # Check if it's a class
                    is_class = self.is_class_item(title)
                    
                    items.append((element, title, is_class))
                    
                    if is_class:
                        class_count += 1
                        print(f"🎯 Class found: {title}")
                    
                except Exception as e:
                    print(f"⚠️  Error processing element {i}: {e}")
                    continue
            
            print(f"🎓 Total classes detected: {class_count}")
            
        except Exception as e:
            print(f"❌ Error getting sidebar items: {e}")
        
        return items
    
    def click_sidebar_item_safe(self, element, title):
        """
        FAST click on sidebar item
        
        Args:
            element: The sidebar item element
            title: The title of the item
            
        Returns:
            bool: True if click was successful
        """
        try:
            # Fast click without unnecessary waits
            element.click()
            
            # Minimal wait for page response
            time.sleep(0.3)
            
            return True
        except:
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
    
    def has_students(self):
        """
        FAST check if there are any students displayed
        
        Returns:
            bool: True if there are students, False if no students
        """
        try:
            # Quick check for "no students" message
            no_students = self.page.query_selector(self.NO_STUDENTS_MESSAGE)
            if no_students and no_students.is_visible():
                return False
            
            # Quick check for student cards
            student_cards = self.page.query_selector_all(self.STUDENT_CARDS)
            return len(student_cards) > 0
            
        except:
            return False
    
    def verify_students_match_class(self, class_name):
        """
        FAST verify that all students have the correct class
        
        Args:
            class_name: The expected class name
            
        Returns:
            tuple: (success, details)
        """
        try:
            # Get all student cards quickly
            student_cards = self.page.query_selector_all(self.STUDENT_CARDS)
            total = len(student_cards)
            matching = 0
            mismatched_students = []
            
            # Fast check each student
            for i, card in enumerate(student_cards):
                try:
                    # Get student name (fast)
                    name_element = card.query_selector(self.STUDENT_NAME)
                    student_name = name_element.text_content().strip() if name_element else f"Student {i+1}"
                    
                    # Get student ID (fast)
                    id_element = card.query_selector(self.STUDENT_ID_SELECTOR)
                    student_id = id_element.text_content().strip() if id_element else "Unknown ID"
                    
                    # Get the class element (fast)
                    class_element = card.query_selector(self.STUDENT_CLASS)
                    
                    if class_element:
                        # Get the actual class
                        actual_class = class_element.text_content().strip()
                        
                        if actual_class == class_name:
                            matching += 1
                        else:
                            # Record mismatched student
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
                "mismatched_students": mismatched_students,
            }
            
            return success, details
        except:
            return False, {"error": "Verification failed"}
    
    def debug_sidebar_structure(self):
        """
        Enhanced debug method to understand the sidebar structure
        """
        try:
            print("\n🔍 ENHANCED SIDEBAR DEBUG")
            print("=" * 50)
            
            # Take a screenshot first
            try:
                self.page.screenshot(path="reports/screenshots/debug_sidebar.png")
                print("📸 Debug screenshot saved")
            except:
                pass
            
            # Try to find all possible sidebar elements
            possible_selectors = [
                "//div[contains(@class,'o_search_panel_label')]",
                "//div[contains(@class,'search_panel_label')]",
                "//div[contains(@class,'panel_label')]",
                "//div[contains(@class,'search_panel')]//div",
                "//aside//div",
                "[data-search-panel]",
                ".o_search_panel_label",
                ".search_panel_label",
                "//span[contains(text(),'(')]",  # Look for items with parentheses
                "//*[contains(text(),'6ème')]",  # Look for specific class names
                "//*[contains(text(),'5ème')]",
                "//*[contains(text(),'2024')]"
            ]
            
            for selector in possible_selectors:
                try:
                    elements = self.page.query_selector_all(selector)
                    print(f"🔎 '{selector}': {len(elements)} elements")
                    
                    if len(elements) > 0:
                        # Show first few elements with their text
                        for i, elem in enumerate(elements[:5]):
                            try:
                                text = elem.text_content()
                                text = text.strip()[:80] if text else "No text"
                                print(f"   [{i+1}] {text}")
                                
                                # Check if this looks like a class
                                if "(" in text and ")" in text:
                                    print(f"   ⭐ This looks like a class: {text}")
                                    
                            except:
                                print(f"   [{i+1}] Could not get text")
                                
                except Exception as e:
                    print(f"❌ '{selector}': Error - {e}")
            
            # Try to get the page source snippet around sidebar
            try:
                sidebar_html = self.page.evaluate("""
                    () => {
                        const sidebar = document.querySelector('[class*="search_panel"], [class*="sidebar"], aside');
                        return sidebar ? sidebar.outerHTML.substring(0, 1000) : 'No sidebar found';
                    }
                """)
                print(f"\n📄 Sidebar HTML snippet:\n{sidebar_html}")
            except:
                pass
                
        except Exception as e:
            print(f"🚨 Debug error: {e}")
    
    def refresh_sidebar_items(self):
        """
        Refresh the sidebar to get updated items after interactions
        
        Returns:
            list: Updated list of sidebar items
        """
        try:
            # Small wait for sidebar to update
            time.sleep(0.5)
            
            # Get fresh items
            return self.get_all_sidebar_items()
        except Exception as e:
            print(f"Error refreshing sidebar: {e}")
            return []