# pages/access/school_card/student_list_actions_page.py
from ...base_page import BasePage
import time
import os
import allure

class StudentListActionsPage(BasePage):
    """Page object for various actions on student list view, including export"""
    
      # Navigation selectors
    WORKSPACE_BUTTON = "//button[@title='Espace de travail']"
    ACCESS_MODULE = "(//a[@data-menu-xmlid='acces.acces'])[3]"
    CARTE_SCOLAIRE_MENU = "(//span[text()='Carte Scolaire'])[2]"
    APPRENANT_SUBMENU = "(//a[@href='#menu_id=108&action=405'])[2]"
    
    # View toggles
    LIST_VIEW_BUTTON = "//button[@data-tooltip='List']"
    KANBAN_VIEW_BUTTON = "//button[@data-tooltip='Kanban']"
    
    # Selection controls
    SELECT_ALL_CHECKBOX = "(//input[@class='form-check-input'])[1]"
    SELECT_ALL_DOMAIN = "//a[contains(@class,'o_list_select_domain ms-3')]"
    SELECTED_COUNT_TEXT = "//div[contains(@class,'o_list_selection_box')]//span"
    
    # Actions menu
    ACTIONS_DROPDOWN = "(//button[contains(@class,'dropdown-toggle btn')])[1]"
    EXPORT_OPTION = "//span[text()='Exporter']"
    ARCHIVE_OPTION = "//span[text()='Archiver']"
    DELETE_OPTION = "//span[text()='Supprimer']"
    
    # Export dialog
    EXPORT_DIALOG = "//div[@class='modal-content o_export_data_dialog']"
    EXPORT_BUTTON = "(//button[contains(@class,'btn btn-primary')])[4]"
    XLSX_RADIO = "//input[@type='radio' and @data-format='xlsx']"
    CSV_RADIO = "//input[@type='radio' and @data-format='csv']"
    
    # Downloads
    DEFAULT_EXCEL_FILENAME = "Statut de lapprenant (acces.statut.apprenant).xlsx"
    DEFAULT_CSV_FILENAME = "Statut de lapprenant (acces.statut.apprenant).csv"
    
    def __init__(self, page):
        super().__init__(page)
        self.page = page
        # Set default downloads folder based on user home
        self.downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    
    def navigate_to_student_list(self):
        """Navigate to the student page and switch to list view"""
        # Navigate to student page
        self.click_with_retry(self.WORKSPACE_BUTTON)
        self.click_with_retry(self.ACCESS_MODULE)
        self.click_with_retry(self.CARTE_SCOLAIRE_MENU)
        self.click_with_retry(self.APPRENANT_SUBMENU)
        
        # Wait for page to load
        self.wait_for_loading(timeout=5000)
        
        # Switch to list view if needed
        if self.is_element_visible(self.LIST_VIEW_BUTTON, timeout=3000):
            self.click_with_retry(self.LIST_VIEW_BUTTON)
            self.wait_for_loading(timeout=3000)
            return True
        return False
    
    def select_all_students(self):
        """Select all students in the list view"""
        try:
            # Click the select all checkbox
            if self.is_element_visible(self.SELECT_ALL_CHECKBOX, timeout=3000):
                self.click_with_retry(self.SELECT_ALL_CHECKBOX)
                time.sleep(0.5)  # Short wait for UI to update
                
                # Click "Select all" domain option if visible
                if self.is_element_visible(self.SELECT_ALL_DOMAIN, timeout=2000):
                    self.click_with_retry(self.SELECT_ALL_DOMAIN)
                    time.sleep(0.5)  # Short wait for UI to update
                
                # Verify selection count is visible
                return self.is_element_visible(self.SELECTED_COUNT_TEXT, timeout=2000)
            return False
        except:
            return False
    
    def get_selected_count(self):
        """Get the number of selected students from the UI"""
        try:
            count_text = self.get_element_text(self.SELECTED_COUNT_TEXT)
            if count_text:
                # Extract number from text like "80 sélectionné(s)"
                import re
                match = re.search(r'(\d+)', count_text)
                if match:
                    return int(match.group(1))
            return 0
        except:
            return 0
    
    def open_actions_menu(self):
        """Open the Actions dropdown menu"""
        try:
            if self.is_element_visible(self.ACTIONS_DROPDOWN, timeout=3000):
                self.click_with_retry(self.ACTIONS_DROPDOWN)
                return True
            return False
        except:
            return False
    
    def select_export_option(self):
        """Select the Export option from Actions menu"""
        try:
            # Open Actions menu if not already open
            if not self.is_element_visible(self.EXPORT_OPTION, timeout=1000):
                if not self.open_actions_menu():
                    return False
            
            # Click Export option
            if self.is_element_visible(self.EXPORT_OPTION, timeout=2000):
                self.click_with_retry(self.EXPORT_OPTION)
                time.sleep(1)

                # Wait for export dialog
                return self.is_element_visible(self.EXPORT_DIALOG, timeout=5000)
            return False
        except:
            return False
    
    def export_to_excel(self):
        """Export selected students to Excel"""
        try:
            # Ensure XLSX format is selected
            if self.is_element_visible(self.XLSX_RADIO, timeout=2000):
                self.click_with_retry(self.XLSX_RADIO)
            
            # Click Export button
            if self.is_element_visible(self.EXPORT_BUTTON, timeout=3000):
                self.click_with_retry(self.EXPORT_BUTTON)
                
                # Wait briefly for download to start
                time.sleep(1)
                
                return True
            return False
        except:
            return False
    
    def export_to_csv(self):
        """Export selected students to CSV"""
        try:
            # Select CSV format
            if self.is_element_visible(self.CSV_RADIO, timeout=2000):
                self.click_with_retry(self.CSV_RADIO)
            
            # Click Export button
            if self.is_element_visible(self.EXPORT_BUTTON, timeout=3000):
                self.click_with_retry(self.EXPORT_BUTTON)
                
                # Wait briefly for download to start
                time.sleep(1)
                
                return True
            return False
        except:
            return False
    
    def verify_file_downloaded(self, file_name=None, timeout=10):
        """Verify that a file was downloaded successfully"""
        # Use default filename if not specified
        if file_name is None:
            file_name = self.DEFAULT_EXCEL_FILENAME
        
        expected_file = os.path.join(self.downloads_folder, file_name)
        
        # Check for the file
        start_time = time.time()
        while time.time() - start_time < timeout:
            if os.path.exists(expected_file):
                # Get file size to verify it's not empty
                file_size = os.path.getsize(expected_file)
                return {
                    "success": True,
                    "file_path": expected_file,
                    "file_size": file_size,
                    "time_to_download": time.time() - start_time
                }
        
        # If we reach here, file wasn't found
        return {
            "success": False,
            "file_path": None,
            "file_size": 0,
            "time_to_download": time.time() - start_time
        }
    
    def complete_excel_export(self):
        """Complete the entire Excel export process"""
        result = {
            "navigation": False,
            "selection": False, 
            "selected_count": 0,
            "export_dialog": False,
            "export_started": False,
            "file_downloaded": False,
            "file_path": None,
            "file_size": 0,
            "download_time": 0
        }
        
        # Navigate to list view
        result["navigation"] = self.navigate_to_student_list()
        if not result["navigation"]:
            return result
        
        # Select all students
        result["selection"] = self.select_all_students()
        if not result["selection"]:
            return result
        
        # Get count of selected students
        result["selected_count"] = self.get_selected_count()
        
        # Open export dialog
        result["export_dialog"] = self.select_export_option()
        if not result["export_dialog"]:
            return result
        
        # Start export
        result["export_started"] = self.export_to_excel()
        if not result["export_started"]:
            return result
        
        # Verify download
        download_result = self.verify_file_downloaded(self.DEFAULT_EXCEL_FILENAME)
        result["file_downloaded"] = download_result["success"]
        result["file_path"] = download_result["file_path"]
        result["file_size"] = download_result["file_size"]
        result["download_time"] = download_result["time_to_download"]
        
        return result