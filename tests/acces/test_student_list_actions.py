# tests/acces/test_student_list_actions.py
import pytest
import time
import os
import allure
from pages.access.school_card.student_list_actions_page import StudentListActionsPage

@pytest.fixture
def list_actions_page(logged_in_page):
    """Setup the student list actions page"""
    list_actions_page = StudentListActionsPage(logged_in_page)
    return list_actions_page

@allure.feature("Student Management")
@allure.story("Data Export")
def test_export_all_students_to_excel(list_actions_page):
    """Test exporting all students to Excel from list view"""
    with allure.step("Complete Excel export workflow"):
        # Execute the entire export process
        result = list_actions_page.complete_excel_export()
        
        # Create detailed log
        allure.attach(
            f"Navigation to list view: {'✓' if result['navigation'] else '✗'}\n"
            f"Selected all students: {'✓' if result['selection'] else '✗'}\n"
            f"Number of students selected: {result['selected_count']}\n"
            f"Export dialog opened: {'✓' if result['export_dialog'] else '✗'}\n"
            f"Export process started: {'✓' if result['export_started'] else '✗'}\n"
            f"File downloaded successfully: {'✓' if result['file_downloaded'] else '✗'}\n"
            f"Download path: {result['file_path']}\n"
            f"File size: {result['file_size']} bytes\n"
            f"Download time: {result['download_time']:.2f} seconds",
            name="Export Process Details",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # Take final screenshot
        screenshot_path = "reports/screenshots/excel_export_complete.png"
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        list_actions_page.page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, 
                         name="Excel Export Completion", 
                         attachment_type=allure.attachment_type.PNG)
        
        # Add file attachment if available
        if result["file_downloaded"] and os.path.exists(result["file_path"]):
            try:
                # Only attach if file is small enough (under 1MB)
                if result["file_size"] < 1024 * 1024:
                    allure.attach.file(result["file_path"], 
                                     name="Exported Excel File", 
                                     attachment_type=allure.attachment_type.XLSX)
            except:
                pass
        
        # Assertions
        assert result["navigation"], "Failed to navigate to student list view"
        assert result["selection"], "Failed to select all students"
        assert result["export_dialog"], "Failed to open export dialog"
        assert result["export_started"], "Failed to start export process"
        assert result["file_downloaded"], "File was not downloaded successfully"
        assert result["file_size"] > 0, "Downloaded file is empty"

@allure.feature("Student Management")
@allure.story("Performance Test")
def test_export_speed(list_actions_page):
    """Test the speed of student export process"""
    with allure.step("Measure export performance"):
        # Record start time
        start_time = time.time()
        
        # Execute the export process
        result = list_actions_page.complete_excel_export()
        
        # Calculate total execution time
        total_time = time.time() - start_time
        
        # Log performance metrics
        allure.attach(
            f"Total test execution time: {total_time:.2f} seconds\n"
            f"Navigation time: {total_time - result['download_time']:.2f} seconds\n"
            f"Download time: {result['download_time']:.2f} seconds\n"
            f"File size: {result['file_size']} bytes\n"
            f"Students selected: {result['selected_count']}\n"
            f"Speed: {result['file_size'] / result['download_time'] / 1024:.2f} KB/s (download)\n"
            f"Speed: {result['selected_count'] / total_time:.2f} students/second (overall)",
            name="Performance Metrics",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # Assertions - focusing on performance
        assert total_time < 30, f"Export took too long: {total_time:.2f} seconds"
        assert result["download_time"] < 10, f"Download took too long: {result['download_time']:.2f} seconds"
        assert result["file_downloaded"], "File was not downloaded successfully"