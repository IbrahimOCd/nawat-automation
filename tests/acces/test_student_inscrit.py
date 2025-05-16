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
@allure.story("Navigation")
def test_navigation_to_student_page(logged_in_page):
    """Test navigation from login to student enrollment page"""
    with allure.step("Create student page object"):
        # Start with a fresh logged-in page
        student_page = StudentInscritPage(logged_in_page)
    
    with allure.step("Navigate through the menus to student page"):
        # Navigate through the menus
        student_page.navigate_from_login()
        
        # Take screenshot and attach to Allure
        screenshot_path = "reports/screenshots/navigation_complete.png"
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        student_page.page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, name="Navigation Complete", attachment_type=allure.attachment_type.PNG)
    
    with allure.step("Verify student page is displayed"):
        # Verify we reached the student page
        is_displayed = student_page.is_student_page_displayed()
        allure.attach(f"Student page displayed: {is_displayed}", name="Page Display Verification", attachment_type=allure.attachment_type.TEXT)
        assert is_displayed, "Failed to navigate to student enrollment page"

@allure.feature("Student Enrollment")
@allure.story("Student Display")
def test_student_page_displays_students(student_page):
    """Test that the student enrollment page shows student cards"""
    with allure.step("Verify student cards are displayed"):
        # Verify student cards are displayed
        visible_count = student_page.get_visible_students_count()
        allure.attach(f"Visible student count: {visible_count}", name="Visible Students", attachment_type=allure.attachment_type.TEXT)
        assert visible_count > 0, "No student cards visible on the page"
    
    with allure.step("Verify total student count"):
        # Verify total count
        total_count = student_page.get_total_students_count()
        allure.attach(f"Total student count: {total_count}", name="Total Students", attachment_type=allure.attachment_type.TEXT)
        assert total_count >= visible_count, "Total student count issue"
    
    with allure.step("Take screenshot of student cards"):
        # Take screenshot of student cards
        screenshot_path = "reports/screenshots/student_cards.png"
        student_page.page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, name="Student Cards", attachment_type=allure.attachment_type.PNG)

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
@allure.story("Pagination")
def test_pagination(student_page):
    """Test navigation between pages of students"""
    with allure.step("Get information from the first page"):
        # Get information from the first page
        first_page_count = student_page.get_visible_students_count()
        allure.attach(f"First page student count: {first_page_count}", name="First Page Count", attachment_type=allure.attachment_type.TEXT)
        
        # Take screenshot of first page
        screenshot_path = "reports/screenshots/pagination_first_page.png"
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        student_page.page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, name="Pagination - First Page", attachment_type=allure.attachment_type.PNG)
    
    # Only test pagination if we have a reasonable number of students
    if first_page_count > 5:
        with allure.step("Get first page student information"):
            # Get the first student name on the first page
            first_page_students = student_page.get_students_info()
            first_student_name = first_page_students[0]["name"] if first_page_students else "Unknown"
            allure.attach(f"First page first student: {first_student_name}", name="First Page First Student", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("Navigate to the next page"):
            # Navigate to the next page if possible
            has_next_page = student_page.navigate_to_next_page()
            allure.attach(f"Next page available: {has_next_page}", name="Next Page Check", attachment_type=allure.attachment_type.TEXT)
        
        if has_next_page:
            with allure.step("Verify second page shows different students"):
                # Get the first student name on the second page
                second_page_students = student_page.get_students_info()
                second_student_name = second_page_students[0]["name"] if second_page_students else "Unknown"
                allure.attach(f"Second page first student: {second_student_name}", name="Second Page First Student", attachment_type=allure.attachment_type.TEXT)
                
                # Verify the pages are different
                assert first_student_name != second_student_name, "Next page navigation failed or showed same students"
                
                # Take screenshot of the second page
                screenshot_path = "reports/screenshots/pagination_second_page.png"
                student_page.page.screenshot(path=screenshot_path)
                allure.attach.file(screenshot_path, name="Pagination - Second Page", attachment_type=allure.attachment_type.PNG)
            
            with allure.step("Navigate back to the first page"):
                # Navigate back to the first page
                student_page.navigate_to_previous_page()
                
                # Verify we're back on the first page
                back_to_first = student_page.get_students_info()
                back_first_name = back_to_first[0]["name"] if back_to_first else "Unknown"
                allure.attach(f"Back to first page first student: {back_first_name}", name="Back To First Page Check", attachment_type=allure.attachment_type.TEXT)
                
                assert first_student_name == back_first_name, "Navigation back to first page failed"
                
                # Take screenshot of returning to first page
                screenshot_path = "reports/screenshots/pagination_back_to_first.png"
                student_page.page.screenshot(path=screenshot_path)
                allure.attach.file(screenshot_path, name="Pagination - Back To First Page", attachment_type=allure.attachment_type.PNG)
        else:
            with allure.step("Skip pagination test - only one page available"):
                allure.attach("Unable to navigate to next page, may only have one page of students", name="Pagination Skip Reason", attachment_type=allure.attachment_type.TEXT)
                pytest.skip("Unable to navigate to next page, may only have one page of students")
    else:
        with allure.step("Skip pagination test - too few students"):
            allure.attach(f"Too few students ({first_page_count}) to test pagination effectively", name="Pagination Skip Reason", attachment_type=allure.attachment_type.TEXT)
            pytest.skip("Too few students to test pagination effectively")

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