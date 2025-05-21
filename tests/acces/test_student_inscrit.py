# tests/test_student_inscrit.py
import pytest
import time
import os
import allure
from pages.login_page import LoginPage
from pages.access.school_card.student_inscrit_page import StudentInscritPage

@pytest.fixture
def student_page(logged_in_page):
    """Setup the student enrollment page after login"""
    with allure.step("Navigate to the student enrollment page"):
        # We're using the logged_in_page fixture from conftest.py which gives us a logged-in page
        student_page = StudentInscritPage(logged_in_page)
        student_page.navigate_from_login()  # Navigate through menus instead of direct URL
        
        # Take screenshot and attach to Allure
        screenshot_path = "reports/screenshots/student_page_setup.png"
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        logged_in_page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, name="Student Page Setup", attachment_type=allure.attachment_type.PNG)
        
        return student_page


@allure.feature("Student Enrollment")
@allure.story("Enrolled Students")
def test_enrolled_students_visible(student_page):
    """Test that enrolled students are visible and marked correctly across all pages"""
    with allure.step("Get all enrolled students across all pages"):
        # Get all enrolled students across all pages
        total_enrolled, all_enrolled_students = student_page.get_all_enrolled_students()
        
        # Attach summary to Allure
        allure.attach(f"Total enrolled students: {total_enrolled}", name="Enrolled Count", attachment_type=allure.attachment_type.TEXT)
    
    with allure.step("Verify we found enrolled students"):
        # Verify we found enrolled students
        assert total_enrolled > 0, "No enrolled students found across all pages"
    
    with allure.step("Verify the count is reasonable"):
        # Check if the number is reasonable (should be less than or equal to total students)
        total_students = student_page.get_total_students_count()
        allure.attach(f"Total students: {total_students}", name="Total Students", attachment_type=allure.attachment_type.TEXT)
        assert total_enrolled <= total_students, f"Found more enrolled students ({total_enrolled}) than total students ({total_students})"
    
    with allure.step("Generate report of enrolled students"):
        # Create detailed report
        stdout = f"Total students visible: {total_students}\n"
        stdout += f"Enrolled students count: {total_enrolled}\n\n"
        
        # Add sample of enrolled students
        sample_size = min(10, len(all_enrolled_students))
        for idx, student in enumerate(all_enrolled_students[:sample_size]):
            stdout += f"Enrolled student {idx+1}: {student['name']} - {student['class']}\n"
        
        if len(all_enrolled_students) > sample_size:
            stdout += f"... and {len(all_enrolled_students) - sample_size} more\n"
        
        # Attach the report to Allure
        allure.attach(stdout, name="Enrolled Students Report", attachment_type=allure.attachment_type.TEXT)
        
        # Also print to console for the HTML report
        print(stdout)
        
        # Take screenshot of the final page
        screenshot_path = "reports/screenshots/enrolled_students_final.png"
        student_page.page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, name="Enrolled Students - Final View", attachment_type=allure.attachment_type.PNG)


@allure.feature("Student Enrollment")
@allure.story("Student Search")
def test_search_student(student_page):
    """Test searching for a specific student"""
    with allure.step("Get student information for search"):
        # Get student info to find a name to search for
        students = student_page.get_students_info()
        allure.attach(f"Found {len(students)} students to search from", name="Search Base", attachment_type=allure.attachment_type.TEXT)
    
    if len(students) > 0:
        with allure.step("Select search term from student names"):
            # Take the first student name to search
            first_student = students[0]
            search_name = first_student["name"].split()[0]  # Use just the first word of the name
            allure.attach(f"Search term selected: '{search_name}'", name="Search Term", attachment_type=allure.attachment_type.TEXT)
            
            # Take screenshot before search
            screenshot_path = "reports/screenshots/before_search.png"
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            student_page.page.screenshot(path=screenshot_path)
            allure.attach.file(screenshot_path, name="Before Search", attachment_type=allure.attachment_type.PNG)
        
        with allure.step(f"Perform search for '{search_name}'"):
            # Perform the search
            student_page.search_student(search_name)
            
            # Take screenshot after search
            screenshot_path = f"reports/screenshots/search_results_{search_name}.png"
            student_page.page.screenshot(path=screenshot_path)
            allure.attach.file(screenshot_path, name=f"Search Results for '{search_name}'", attachment_type=allure.attachment_type.PNG)
        
        with allure.step("Verify search results"):
            # Verify search results
            search_results = student_page.get_students_info()
            allure.attach(f"Found {len(search_results)} results for search term '{search_name}'", name="Search Results Count", attachment_type=allure.attachment_type.TEXT)
            
            # Verify at least one result contains our search term
            found = any(search_name in student["name"] for student in search_results)
            assert found, f"Search for '{search_name}' failed to find matching students"
            
            # List matching results
            matching_students = [student["name"] for student in search_results if search_name in student["name"]]
            allure.attach("\n".join(matching_students), name="Matching Students", attachment_type=allure.attachment_type.TEXT)
    else:
        with allure.step("Skip search test - no students available"):
            allure.attach("No students available to search for", name="Search Skip Reason", attachment_type=allure.attachment_type.TEXT)
            pytest.skip("No students available to search for")