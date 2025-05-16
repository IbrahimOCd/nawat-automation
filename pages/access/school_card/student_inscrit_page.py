# pages/access/student_inscrit_page.py
from ...base_page import BasePage
import time
import os

class StudentInscritPage(BasePage):
    """Page object for the student enrollment (inscrit) page in Kanban view"""
    
    # Navigation selectors
    WORKSPACE_BUTTON = "//button[@title='Espace de travail']"
    ACCESS_MODULE = "(//a[@data-menu-xmlid='acces.acces'])[3]"
    CARTE_SCOLAIRE_MENU = "(//button[@class='dropdown-toggle']//span)[1]"
    APPRENANT_SUBMENU = "(//a[@href='#menu_id=108&action=405'])[2]"
    
    # Main elements
    PAGE_TITLE = "//ol[contains(@class,'breadcrumb')]/li[contains(text(),'Apprenant')]"
    KANBAN_VIEW = "//div[contains(@class,'o_action_manager')]"
    
    # Student cards and status
    STUDENT_CARDS = "(//div[contains(@class,'oe_kanban_global_click o_kanban_record_has_image_fill')])"
    ENROLLED_ICON = "//i[@title='circle-success']"  # Icon indicating student is enrolled
    STUDENT_NAME = "(//strong[@class='o_kanban_record_title text-truncate']//span)"
    STUDENT_CLASS = "(//i[contains(@class,'icon na-layer-group-2')]/following-sibling::span)"
    
    # Navigation and filters
    NEXT_PAGE_BUTTON = "(//button[contains(@class,'btn btn-secondary')])[3]"
    PREV_PAGE_BUTTON = "(//button[contains(@class,'btn btn-secondary')])[2]"
    PAGINATION_INFO = "//nav[contains(@class,'o_pager d-flex')]"
    
    # Search and actions
    SEARCH_INPUT = "//input[contains(@class,'o_searchview_input o_input')]"
    
    def __init__(self, page):
        super().__init__(page)
        self.page = page
    
    def wait_for_page_loaded(self):
        """Wait for the student page to be fully loaded"""
        # Wait for kanban view to be visible
        self.page.wait_for_selector(self.KANBAN_VIEW, state="visible", timeout=10000)
        
        # Wait for at least one student card to appear
        self.page.wait_for_selector(self.STUDENT_CARDS, state="visible", timeout=10000)
        
        # Additional wait for all elements to settle
        self.page.wait_for_load_state("networkidle")
        time.sleep(1)  # Extra wait for stability
    def navigate_from_login(self):
        """Navigate to the student page through the menu structure after login"""
        # Click on workspace button
        self.click_with_retry(self.WORKSPACE_BUTTON)
        
        # Click on Access module
        self.click_with_retry(self.ACCESS_MODULE)
        
        # Click on Carte Scolaire menu
        self.click_with_retry(self.CARTE_SCOLAIRE_MENU)
        
        # Wait a moment for submenu to appear
        
        # Click on Apprenant submenu
        self.click_with_retry(self.APPRENANT_SUBMENU)
        
        # Wait for page to fully load
        self.wait_for_page_loaded()
        
        # Take screenshot after navigation
        os.makedirs("reports/screenshots", exist_ok=True)
        self.page.screenshot(path="reports/screenshots/navigation_to_student_page.png")
 
    
    def is_student_page_displayed(self):
        """Verify we are on the student enrollment page"""
        return (
            self.page.is_visible(self.KANBAN_VIEW) and
            self.page.is_visible(self.STUDENT_CARDS) and
            self.page.is_visible(self.PAGINATION_INFO)
        )
    
    def get_total_students_count(self):
        """Get the total number of students from pagination info"""
        try:
            pagination_text = self.page.text_content(self.PAGINATION_INFO)
            # Extract numbers from text like "1-80 / 321"
            if "/" in pagination_text:
                total = pagination_text.split("/")[1].strip()
                return int(total)
            return 0
        except Exception as e:
            print(f"Error getting total students count: {str(e)}")
            return 0
    
    def get_visible_students_count(self):
        """Get the number of student cards visible on the current page"""
        try:
            return len(self.page.query_selector_all(self.STUDENT_CARDS))
        except Exception as e:
            print(f"Error getting visible students count: {str(e)}")
            return 0
    
    def get_all_enrolled_students(self):
        """
        Get all enrolled students across all pages without duplicates
        
        Returns:
            tuple: (total_enrolled_count, list_of_enrolled_students)
        """
        all_enrolled_students = []
        current_page = 1
        max_pages = 10  # Safety limit to prevent infinite loops
        
        # Get total students from pagination info
        total_students = self.get_total_students_count()
        print(f"Total students according to pagination: {total_students}")
        
        # Calculate expected number of pages
        students_per_page = 80  
        expected_pages = (total_students + students_per_page - 1) // students_per_page
        print(f"Expected number of pages: {expected_pages}")
        
        # Process the first page
        students_info = self.get_students_info()
        enrolled_students = [s for s in students_info if s.get("enrolled", False)]
        all_enrolled_students.extend(enrolled_students)
        
        print(f"Page {current_page}: Found {len(enrolled_students)} enrolled students")
        
        # Take screenshot of first page
        os.makedirs("reports/screenshots", exist_ok=True)
        self.page.screenshot(path=f"reports/screenshots/enrolled_students_page_{current_page}.png")
        
        # Check if there are more pages
        has_next = self.page.evaluate("""
        () => {
            const nextButton = document.querySelector('button.o_pager_next');
            return nextButton && !nextButton.disabled;
        }
        """)
        
        # Navigate through remaining pages
        while has_next and current_page < expected_pages and current_page < max_pages:
            # Go to next page
            self.page.click('button.o_pager_next')
            self.wait_for_loading()
            current_page += 1
            
            # Get enrolled students on this page
            students_info = self.get_students_info()
            enrolled_students = [s for s in students_info if s.get("enrolled", False)]
            all_enrolled_students.extend(enrolled_students)
            
            print(f"Page {current_page}: Found {len(enrolled_students)} enrolled students")
            
            # Take screenshot of this page
            self.page.screenshot(path=f"reports/screenshots/enrolled_students_page_{current_page}.png")
            
            # Check if there's another page
            has_next = self.page.evaluate("""
            () => {
                const nextButton = document.querySelector('button.o_pager_next');
                return nextButton && !nextButton.disabled;
            }
            """)
        
        # Don't attempt to go back to the first page - this is causing issues
        # Just return the collected information
        
        total_enrolled = len(all_enrolled_students)
        return total_enrolled, all_enrolled_students
    def navigate_to_next_page(self):
        """Click the next page button if available"""
        try:
            # Check if button is visible
            if self.page.is_visible(self.NEXT_PAGE_BUTTON):
                # Try to click it
                self.click_with_retry(self.NEXT_PAGE_BUTTON)
                self.wait_for_loading()
                self.wait_for_page_loaded()
                return True
            return False
        except Exception as e:
            print(f"Error navigating to next page: {str(e)}")
            return False
        
    def navigate_to_previous_page(self):
        """Click the previous page button if available"""
        if self.page.is_visible(self.PREV_PAGE_BUTTON) and self.is_enabled(self.PREV_PAGE_BUTTON):
            self.click_with_retry(self.PREV_PAGE_BUTTON)
            self.wait_for_loading()
            self.wait_for_page_loaded()
            return True
        return False
    
    def get_students_info(self):
        """Get list of visible students with their info using JavaScript evaluation"""
        try:
            # Use JavaScript to extract all student info at once
            students_info = self.page.evaluate("""
            () => {
                const studentCards = document.querySelectorAll('.o_kanban_record');
                return Array.from(studentCards).map(card => {
                    // Get student name
                    const nameElement = card.querySelector('.o_kanban_record_title');
                    const name = nameElement ? nameElement.textContent.trim() : 'Unknown';
                    
                    // Get student class
                    const classElement = card.querySelector('.o_kanban_record_subtitle');
                    const classInfo = classElement ? classElement.textContent.trim() : '--';
                    
                    // Check if enrolled (has success icon)
                    const enrolledIcon = card.querySelector('.text-success') || 
                                        card.querySelector('i.fa-check-circle') ||
                                        card.querySelector('i[title="circle-success"]');
                    
                    return {
                        name: name,
                        class: classInfo,
                        enrolled: !!enrolledIcon
                    };
                });
            }
            """)
            
            return students_info
        except Exception as e:
            print(f"Error getting students info: {str(e)}")
            # Take a screenshot for debugging
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            self.page.screenshot(path=f"reports/screenshots/error_getting_students_{timestamp}.png")
            return []
    def get_enrolled_students_count(self):
        """Get the number of enrolled students (with success icon) on the current page"""
        try:
            # Use JavaScript to count enrolled students
            enrolled_count = self.page.evaluate("""
            () => {
                const studentCards = document.querySelectorAll('.o_kanban_record');
                let count = 0;
                
                for (const card of studentCards) {
                    const enrolledIcon = card.querySelector('.text-success') || 
                                        card.querySelector('i.fa-check-circle') ||
                                        card.querySelector('i[title="circle-success"]');
                    if (enrolledIcon) {
                        count++;
                    }
                }
                
                return count;
            }
            """)
            
            return enrolled_count
        except Exception as e:
            print(f"Error getting enrolled students count: {str(e)}")
            return 0
    def search_student(self, search_text):
        """
        Search for a specific student
        
        Args:
            search_text: Text to search for
        """
        # Clear and fill the search input
        self.page.click(self.SEARCH_INPUT)  # First click to focus
        self.page.fill(self.SEARCH_INPUT, "")
        self.page.fill(self.SEARCH_INPUT, search_text)
        
        # Press Enter to search
        self.page.press(self.SEARCH_INPUT, "Enter")
        
        # Wait for results
        self.wait_for_loading()
        self.wait_for_page_loaded()
        
        # Take screenshot of search results
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        os.makedirs("reports/screenshots", exist_ok=True)
        self.page.screenshot(path=f"reports/screenshots/search_{search_text}_{timestamp}.png")