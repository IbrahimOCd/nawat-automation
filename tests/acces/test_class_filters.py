# tests/acces/test_class_filters.py
import pytest
import time
import os
import allure
from pages.access.school_card.class_filter_page import ClassFilterPage

@pytest.fixture
def class_filter_page(logged_in_page):
    """Setup the class filter page after login"""
    class_filter_page = ClassFilterPage(logged_in_page)
    class_filter_page.navigate_from_login()
    class_filter_page.wait_for_page_loaded()
    return class_filter_page

@allure.feature("Student Management")
@allure.story("Class Filtering")
def test_all_classes_filter(class_filter_page):
    """Test filtering students by all available class levels"""
    # First phase: Expand everything in the sidebar
    expanded_items = class_filter_page.expand_all_items()
    
    # Go back to the main view after expanding everything
    class_filter_page.wait_for_page_loaded()
    
    # Second phase: Test classes (items with parentheses)
    # Initialize tracking variables
    classes_tested = []
    classes_with_students = []
    classes_without_students = []
    classes_with_mismatches = {}  # Changed to dictionary to store mismatched students
    
    # Process each item again
    current_index = 1
    max_attempts = 100  # Safety limit
    
    while current_index <= max_attempts:
        try:
            # Get the item
            item, title = class_filter_page.get_sidebar_item(current_index)
            
            # If item doesn't exist, we've reached the end
            if not item:
                break
            
          
            # Only test classes (items with parentheses)
            elif class_filter_page.is_class_item(title):
                # It's a class - click and test students
                class_filter_page.click_sidebar_item(item, title)
                classes_tested.append(title)
                
                # Wait for page to load
                class_filter_page.wait_for_page_loaded()
                
                # Check if there are students
                if class_filter_page.has_students():
                    classes_with_students.append(title)
                    class_filter_page.wait_for_page_loaded()

                    # Verify students match the class
                    success, details = class_filter_page.verify_students_match_class(title)
                    
                    if not success and 'mismatched_students' in details:
                        # Store mismatched students with class
                        classes_with_mismatches[title] = details['mismatched_students']
                else:
                    classes_without_students.append(title)
                
                # Navigate back
                class_filter_page.wait_for_page_loaded()
            else:
                # Not a class - just click and move on
                class_filter_page.click_sidebar_item(item, title)
                
                # Navigate back
                class_filter_page.wait_for_page_loaded()
            
            # Move to the next item
            current_index += 1
        except Exception as e:
            # Log the error
            allure.attach(f"Error processing item at index {current_index}: {str(e)}",
                        name="Process Error",
                        attachment_type=allure.attachment_type.TEXT)
            
            # Try to recover by navigating back
            try:
                            class_filter_page.wait_for_page_loaded()
            except:
                pass
            
            # Move to the next item
            current_index += 1
    
    # Create detailed summary of mismatched students
    mismatched_summary = ""
    for class_name, mismatched in classes_with_mismatches.items():
        mismatched_summary += f"\nClass: {class_name}\n"
        mismatched_summary += f"Total mismatched students: {len(mismatched)}\n"
        mismatched_summary += "Student details:\n"
        
        for student in mismatched:
            mismatched_summary += f"- Student #{student['index']}: {student['name']} (ID: {student['id']})\n"
            mismatched_summary += f"  Expected class: {student['expected_class']}\n"
            mismatched_summary += f"  Actual class: {student['actual_class']}\n"
    
    # Generate summary report
    summary = (f"TEST SUMMARY\n\n" +
              f"Classes Tested ({len(classes_tested)}):\n" +
              f"- {', '.join(classes_tested)}\n\n" +
              f"Classes with Students ({len(classes_with_students)}):\n" +
              f"- {', '.join(classes_with_students)}\n\n" +
              f"Classes without Students ({len(classes_without_students)}):\n" +
              f"- {', '.join(classes_without_students)}\n\n" +
              f"Classes with Mismatched Students ({len(classes_with_mismatches)}):\n" +
              f"- {', '.join(classes_with_mismatches.keys())}")
    
    if mismatched_summary:
        summary += f"\n\nDETAILED MISMATCHES:{mismatched_summary}"
    
    allure.attach(summary, name="Test Summary", attachment_type=allure.attachment_type.TEXT)
    
    # Take a screenshot at the very end
    class_filter_page.page.screenshot(path="reports/screenshots/test_complete.png")
    
    # Assert that there are no mismatches
    if classes_with_mismatches:
        # Create detailed error message with student information
        error_message = f"Found {len(classes_with_mismatches)} classes with mismatched students:\n{mismatched_summary}"
        pytest.fail(error_message)
    
    # Assert that we tested at least some classes
    assert len(classes_tested) > 0, "No classes were tested"
    
    # Assert that we found students in at least some classes
    assert len(classes_with_students) > 0, "No classes with students were found"