# tests/test_login.py
import pytest
import json
import os
import time
import allure
from pages.login_page import LoginPage

def load_test_users():
    """Load test users from JSON file"""
    try:
        with open('data/users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading test users: {str(e)}")
        # Fallback test data
        return {
            "invalid_users": [
                {"username": "wrong_user", "password": "wrong_pass", "description": "Completely invalid credentials"},
                {"username": "ecole.e2a", "password": "wrong_pass", "description": "Valid username, invalid password"},
                {"username": "wrong_user", "password": "1@ayouris2", "description": "Invalid username, valid password"}
            ],
            "valid_users": [
                {"username": "ecole.e2a", "password": "1@ayouris2", "description": "Valid school admin credentials"}
            ]
        }

# Test language switching and UI verification
@allure.feature("Login")
@allure.story("Language Switching")
@pytest.mark.parametrize("language_code", ["en", "fr", "ar"])
def test_language_switching(page, language_code):
    """Test switching between different languages on the login page"""
    with allure.step(f"Navigate to login page"):
        login_page = LoginPage(page)
        login_page.navigate()
        
        # Take screenshot and attach to Allure
        screenshot_path = f"reports/screenshots/login_initial_{language_code}.png"
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, name=f"Login Page - Initial ({language_code})", attachment_type=allure.attachment_type.PNG)
    
    with allure.step(f"Switch language to {language_code}"):
        # Switch language
        success = login_page.switch_language(language_code)
        assert success, f"Failed to switch to {language_code}"
        
        # Take screenshot and attach to Allure
        screenshot_path = f"reports/screenshots/language_{language_code}.png"
        page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, name=f"Login Page - {language_code}", attachment_type=allure.attachment_type.PNG)
    
    with allure.step("Verify login form elements in the selected language"):
        # Verify form elements in the chosen language
        verification_results = login_page.verify_login_form_elements()
        
        # Attach verification results to Allure
        allure.attach(str(verification_results), name="Form Elements Verification Results", attachment_type=allure.attachment_type.TEXT)
        
        # Check all verifications passed
        assert all(verification_results.values()), f"Form elements verification failed: {verification_results}"

# Test invalid login
@allure.feature("Login")
@allure.story("Invalid Login")
@pytest.mark.parametrize("language_code", ["en", "fr", "ar"])
def test_invalid_login(page, language_code):
    """Test login with invalid credentials"""
    with allure.step("Load test user data"):
        # Load test users
        test_users = load_test_users()
        invalid_user = test_users["invalid_users"][0]  # Use first invalid user
        allure.attach(f"Using invalid credentials: {invalid_user['description']}", name="Test Data", attachment_type=allure.attachment_type.TEXT)
    
    with allure.step("Navigate to login page"):
        login_page = LoginPage(page)
        login_page.navigate()
        
        # Take screenshot and attach to Allure
        screenshot_path = f"reports/screenshots/login_page_invalid_{language_code}.png"
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, name=f"Login Page - Before Invalid Login ({language_code})", attachment_type=allure.attachment_type.PNG)
    
    with allure.step(f"Switch language to {language_code}"):
        # Switch language
        success = login_page.switch_language(language_code)
        assert success, f"Failed to switch to {language_code}"
    
    with allure.step("Attempt login with invalid credentials"):
        # Attempt login with invalid credentials
        success = login_page.login(invalid_user["username"], invalid_user["password"])
        
        # Take screenshot and attach to Allure
        screenshot_path = f"reports/screenshots/invalid_login_result_{language_code}.png"
        page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, name=f"Invalid Login Result ({language_code})", attachment_type=allure.attachment_type.PNG)
        
        # Should not succeed
        assert not success, "Login should fail with invalid credentials"
    
    with allure.step("Verify error message"):
        # Verify error message
        has_error = login_page.verify_error_message()
        allure.attach(f"Error message verification: {has_error}", name="Error Message Check", attachment_type=allure.attachment_type.TEXT)
        assert has_error, f"Error message not as expected in {language_code}"

# Test valid login
@allure.feature("Login")
@allure.story("Valid Login")
def test_valid_login(page):
    """Test login with valid credentials"""
    with allure.step("Navigate to login page"):
        login_page = LoginPage(page)
        login_page.navigate()
        
        # Take screenshot and attach to Allure
        screenshot_path = "reports/screenshots/login_page_valid.png"
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, name="Login Page - Before Valid Login", attachment_type=allure.attachment_type.PNG)
    
    with allure.step("Get valid test user"):
        # Get valid test user
        test_users = load_test_users()
        valid_user = test_users["valid_users"][0]  # Use first valid user
        allure.attach(f"Using valid credentials: {valid_user['description']}", name="Test Data", attachment_type=allure.attachment_type.TEXT)
    
    with allure.step("Perform login with valid credentials"):
        # Perform login
        success = login_page.login(valid_user["username"], valid_user["password"])
        
        # Take screenshot and attach to Allure
        screenshot_path = "reports/screenshots/valid_login_result.png"
        page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, name="Valid Login Result", attachment_type=allure.attachment_type.PNG)
        
        # Should succeed
        assert success, "Login should succeed with valid credentials"
    
    with allure.step("Verify navigation to dashboard"):
        # Verify we're on the dashboard
        is_on_dashboard = login_page.page.is_visible(login_page.MAIN_NAVBAR)
        allure.attach(f"Main navbar visible: {is_on_dashboard}", name="Dashboard Navigation Check", attachment_type=allure.attachment_type.TEXT)
        assert is_on_dashboard, "Main navbar should be visible after login"