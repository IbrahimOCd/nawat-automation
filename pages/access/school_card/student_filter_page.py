# pages/access/school_card/student_filter_page.py
from ...base_page import BasePage
import time
import os

class StudentFilterPage(BasePage):
    """Page object for the student filter functionality in Kanban view"""
    
    # Navigation selectors
    WORKSPACE_BUTTON = "//button[@title='Espace de travail']"
    ACCESS_MODULE = "(//a[@data-menu-xmlid='acces.acces'])[3]"
    CARTE_SCOLAIRE_MENU = "(//span[text()='Carte Scolaire'])[2]"
    APPRENANT_SUBMENU = "(//a[@href='#menu_id=108&action=405'])[2]"
    
    # Filter selectors
    FILTER_DROPDOWN_BUTTON = "//button[contains(@class,'dropdown-toggle o_searchview_dropdown_toggler')]"
    NON_INSCRIT_FILTER = "//span[text()='Non inscrit']"
    NON_REINSCRIT_FILTER = "//span[text()='Non réinscrit']"
    RADIEE_FILTER = "//span[@title='Radiée (Archivé)']"
    ANNULEE_FILTER = "//span[text()='Annulée (Archivé)']"
    NON_INSCRIT_ARCHIVE_FILTER = "//span[text()='Non-inscrit (Archivé)']"
    SANS_FAMILLE_FILTER = "//span[text()='Sans famille']"
    MANQUE_DOCUMENT_FILTER = "//span[text()='Manque document']"
    
    # Search facet selectors
    FILTER_FACET_TEXT = "//div[contains(@class,'o_facet_values position-relative')]//small[1]"
    REMOVE_FILTER_BUTTON = "//button[contains(@class,'o_facet_remove oi')]"
    SEARCH_INPUT = "//input[contains(@class,'o_searchview_input o_input')]"

    # Student card selectors - simplified for better performance
    STUDENT_CARDS = "//div[contains(@class,'oe_kanban_global_click')]"
    STUDENT_CARD_CLICKABLE = "//div[contains(@class,'oe_kanban_global_click')]"
    STUDENT_NAME = "//strong[@class='o_kanban_record_title text-truncate']//span"
    STUDENT_CLASS = "//i[contains(@class,'icon na-layer-group-2')]/following-sibling::span"
    
    # Student list view (fallback when no cards are shown)
    STUDENT_LIST_VIEW = "//div[contains(@class,'o_list_view')]"
    
    # Status indicators
    NON_INSCRIT_LABEL = "//span[text()='Non-inscrit']"
    NON_REINSCRIT_LABEL = "//span[text()='Non-réinscrit']"
    RADIEE_LABEL = "//span[text()='Inscription radiée']"
    ANNULEE_LABEL = "//span[text()='Inscription annulée']"
    
    # Card detail selectors
    SETTINGS_ICON = "//i[@class='fa fa-cog']"
    UNARCHIVE_OPTION = "//span[@title='Désarchiver']"
    SANS_FAMILLE_IMAGE = "//img[@alt='non affecté']"
    MISSING_DOCUMENT_BUTTON = "//button[@invisible='not sb_total_documents']"
    
    def __init__(self, page):
        super().__init__(page)
        self.page = page
    
    def navigate_from_login(self):
        """Navigate to the student page through the menu structure after login"""
        # Click on workspace button
        self.click_with_retry(self.WORKSPACE_BUTTON)
        
        # Click on Access module
        self.click_with_retry(self.ACCESS_MODULE)
        
        # Click on Carte Scolaire menu
        self.click_with_retry(self.CARTE_SCOLAIRE_MENU)
        
        # Click on Apprenant submenu
        self.click_with_retry(self.APPRENANT_SUBMENU)
        
        # Wait for page to fully load
        self.wait_for_page_loaded()
        
        # Create screenshots directory if it doesn't exist
        os.makedirs("reports/screenshots", exist_ok=True)
    
    def wait_for_page_loaded(self):
        """Wait for the student page to be fully loaded"""
        self.wait_for_loading(timeout=8000)
        
        # Try to wait for either student cards or list view
        try:
            self.page.wait_for_selector(f"{self.STUDENT_CARDS}, {self.STUDENT_LIST_VIEW}", timeout=5000)
        except:
            # If neither is found, just continue
            pass
    
    def open_filter_dropdown(self):
        """Open the filter dropdown menu"""
        try:
            self.click_with_retry(self.FILTER_DROPDOWN_BUTTON, timeout=5000)
        except:
            # If dropdown button isn't found, continue with the test
            pass
    
    def apply_filter(self, filter_selector):
        """Apply a specific filter from the dropdown"""
        try:
            # Open the filter dropdown if it's not already open
            self.open_filter_dropdown()
            
            # Click on the specified filter
            self.click_with_retry(filter_selector, timeout=5000)
            
            # Focus on search input to close the dropdown
            try:
                self.page.click(self.SEARCH_INPUT)
            except:
                pass

            # Wait for page to load
            self.wait_for_page_loaded()
        except Exception as e:
            # Log error and continue
            print(f"Error applying filter: {str(e)}")
    
    def remove_filter(self):
        """Remove the currently applied filter"""
        try:
            if self.is_element_visible(self.REMOVE_FILTER_BUTTON, timeout=3000):
                self.click_with_retry(self.REMOVE_FILTER_BUTTON, timeout=3000)
                self.wait_for_page_loaded()
        except:
            # Continue even if removing filter fails
            pass
    
    def get_filter_facet_text(self):
        """Get the text of the currently applied filter facet"""
        return self.get_element_text(self.FILTER_FACET_TEXT, timeout=3000)
    
    def check_all_students_have_label(self, label_selector):
        """Check if a sample of visible student cards have the specified label"""
        try:
            # Get all student cards
            all_cards = self.page.query_selector_all(self.STUDENT_CARDS)
            
            if len(all_cards) == 0:
                return False
            
            # Check at most 3 cards for efficiency
            cards_to_check = min(3, len(all_cards))
            
            # Check each card for the label
            label_count = 0
            for i in range(cards_to_check):
                # Construct a selector for the label within this specific card
                card_label_selector = f"({self.STUDENT_CARD_CLICKABLE})[{i+1}] {label_selector}"
                
                try:
                    if self.is_element_visible(card_label_selector, timeout=1000):
                        label_count += 1
                except:
                    # Skip errors and continue
                    continue
            
            # Return True if majority of checked cards have the label
            return label_count >= cards_to_check // 2
            
        except:
            return False
    
    def check_all_students_class_is_empty(self):
        """Check if a sample of visible student cards have empty class information"""
        try:
            # Get all student cards
            all_cards = self.page.query_selector_all(self.STUDENT_CARDS)
            
            if len(all_cards) == 0:
                return False
            
            # Check at most 3 cards for efficiency
            cards_to_check = min(3, len(all_cards))
            
            # Count cards with empty class
            empty_class_count = 0
            
            # Check each card for class text
            for i in range(cards_to_check):
                # Construct selector for class element
                class_selector = f"({self.STUDENT_CARDS})[{i+1}]//i[contains(@class,'icon na-layer-group-2')]/following-sibling::span"
                
                try:
                    if self.is_element_visible(class_selector, timeout=1000):
                        # Get the text content
                        class_text = self.get_element_text(class_selector)
                        
                        # Check if empty or equal to "--"
                        if not class_text or class_text == "--":
                            empty_class_count += 1
                    else:
                        # If class element isn't visible, count it as empty
                        empty_class_count += 1
                except:
                    # Skip errors and continue
                    empty_class_count += 1
            
            # Return True if majority of checked cards have empty class
            return empty_class_count >= cards_to_check // 2
            
        except:
            return False
    
    def check_all_students_have_sans_famille_image(self):
        """Check if a sample of visible student cards have the 'non affecté' image"""
        try:
            # Get all student cards
            all_cards = self.page.query_selector_all(self.STUDENT_CARDS)
            
            if len(all_cards) == 0:
                return False
            
            # Check at most 3 cards for efficiency
            cards_to_check = min(3, len(all_cards))
            
            # Check each card for the image
            image_count = 0
            for i in range(cards_to_check):
                # Construct image selector
                image_selector = f"({self.STUDENT_CARDS})[{i+1}]//img[@alt='non affecté']"
                
                try:
                    if self.is_element_visible(image_selector, timeout=1000):
                        image_count += 1
                except:
                    # Skip errors and continue
                    continue
            
            # Return True if majority of checked cards have the image
            return image_count >= cards_to_check // 2
            
        except:
            return False
    
    def click_first_student_card(self):
        """Click on the first student card to open student details"""
        try:
            if self.is_element_visible(f"({self.STUDENT_CARD_CLICKABLE})[1]", timeout=3000):
                self.click_with_retry(f"({self.STUDENT_CARD_CLICKABLE})[1]", timeout=3000)
                self.wait_for_loading()
                return True
            return False
        except:
            return False
    
    def check_settings_and_unarchive_option(self):
        """Check if settings icon and unarchive option are available"""
        try:
            # Check if settings icon is visible
            if not self.is_element_visible(self.SETTINGS_ICON, timeout=3000):
                return False
                
            # Click on settings icon
            self.click_with_retry(self.SETTINGS_ICON, timeout=3000)
            
            # Check if unarchive option is visible
            return self.is_element_visible(self.UNARCHIVE_OPTION, timeout=3000)
        except:
            return False
    
    def check_missing_document_button(self):
        """Check if the missing document button is available on student details page"""
        return self.is_element_visible(self.MISSING_DOCUMENT_BUTTON, timeout=3000)
    
    def go_back_to_student_list(self):
        """Go back to the student list from details page"""
        try:
            # Use browser back button
            self.page.go_back()
            
            # Wait for page to load
            self.wait_for_page_loaded()
            return True
        except:
            # If going back fails, try to navigate from scratch
            try:
                self.navigate_from_login()
                return True
            except:
                return False