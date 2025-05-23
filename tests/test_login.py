# tests/test_login.py - OPTIMIZED COMBINED VERSION
import pytest
import json
import os
import time
import allure
from pages.login_page import LoginPage

def load_test_users():
    """Fast load test users with fallback"""
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

def is_jenkins():
    """Quick Jenkins detection"""
    return any([
        os.getenv('JENKINS_URL'),
        os.getenv('CI') == 'true',
        os.getenv('JENKINS_BUILD') == 'true'
    ])

# COMBINED TEST: Language switching + Invalid login
@allure.feature("Login")
@allure.story("Language Switching & Invalid Login")
@pytest.mark.parametrize("language_code", ["en", "fr", "ar"])
def test_language_switching_with_invalid_login(page, language_code):
    """Test language switching AND invalid login in each language"""
    
    # Load test data
    test_users = load_test_users()
    invalid_user = test_users["invalid_users"][0]  # Use first invalid user
    
    with allure.step(f"Navigate and switch to {language_code}"):
        login_page = LoginPage(page)
        login_page.navigate()
        
        # Take initial screenshot only if not Jenkins
        if not is_jenkins():
            screenshot_path = f"reports/screenshots/login_initial_{language_code}.png"
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            page.screenshot(path=screenshot_path)
            allure.attach.file(screenshot_path, name=f"Login Page - Initial ({language_code})", attachment_type=allure.attachment_type.PNG)
        
        # Switch language
        success = login_page.switch_language(language_code)
        assert success, f"Failed to switch to {language_code}"
        
        # Take language screenshot only if not Jenkins
        if not is_jenkins():
            screenshot_path = f"reports/screenshots/language_{language_code}.png"
            page.screenshot(path=screenshot_path)
            allure.attach.file(screenshot_path, name=f"Login Page - {language_code}", attachment_type=allure.attachment_type.PNG)
    
    with allure.step(f"Verify form elements in {language_code}"):
        # Verify form elements in the chosen language
        verification_results = login_page.verify_login_form_elements()
        
        # Attach verification results to Allure
        allure.attach(str(verification_results), name=f"Form Elements Verification ({language_code})", attachment_type=allure.attachment_type.TEXT)
        
        # Check all verifications passed
        assert all(verification_results.values()), f"Form elements verification failed in {language_code}: {verification_results}"
    
    with allure.step(f"Test invalid login in {language_code}"):
        # Attach test data info
        allure.attach(f"Using invalid credentials: {invalid_user['description']}", name="Test Data", attachment_type=allure.attachment_type.TEXT)
        
        # Attempt login with invalid credentials
        login_success = login_page.login(invalid_user["username"], invalid_user["password"])
        
        # Take screenshot of invalid login result only if not Jenkins
        if not is_jenkins():
            screenshot_path = f"reports/screenshots/invalid_login_result_{language_code}.png"
            page.screenshot(path=screenshot_path)
            allure.attach.file(screenshot_path, name=f"Invalid Login Result ({language_code})", attachment_type=allure.attachment_type.PNG)
        
        # Should not succeed
        assert not login_success, f"Login should fail with invalid credentials in {language_code}"
    
    with allure.step(f"Verify error message in {language_code}"):
        # Verify error message appears
        has_error = login_page.verify_error_message()
        allure.attach(f"Error message verification: {has_error}", name=f"Error Message Check ({language_code})", attachment_type=allure.attachment_type.TEXT)
        assert has_error, f"Error message not displayed properly in {language_code}"
    
    # Summary for this language test
    test_summary = (
        f"LANGUAGE TEST SUMMARY - {language_code.upper()}\n"
        f"Language Switch: {'✓' if success else '✗'}\n"
        f"Form Verification: {'✓' if all(verification_results.values()) else '✗'}\n"
        f"Invalid Login Rejected: {'✓' if not login_success else '✗'}\n"
        f"Error Message Shown: {'✓' if has_error else '✗'}"
    )
    allure.attach(test_summary, name=f"Test Summary ({language_code})", attachment_type=allure.attachment_type.TEXT)
    print(f"Language {language_code} test completed successfully")

# SEPARATE TEST: Valid login only
@allure.feature("Login")
@allure.story("Valid Login")
def test_valid_login(page):
    """Test login with valid credentials"""
    
    start_time = time.time()
    
    with allure.step("Navigate to login page"):
        login_page = LoginPage(page)
        login_page.navigate()
        
        # Take screenshot only if not Jenkins
        if not is_jenkins():
            screenshot_path = "reports/screenshots/login_page_valid.png"
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            page.screenshot(path=screenshot_path)
            allure.attach.file(screenshot_path, name="Login Page - Before Valid Login", attachment_type=allure.attachment_type.PNG)
    
    with allure.step("Get valid test user and perform login"):
        # Get valid test user
        test_users = load_test_users()
        valid_user = test_users["valid_users"][0]  # Use first valid user
        allure.attach(f"Using valid credentials: {valid_user['description']}", name="Test Data", attachment_type=allure.attachment_type.TEXT)
        
        # Perform login
        success = login_page.login(valid_user["username"], valid_user["password"])
        
        # Take screenshot only if not Jenkins
        if not is_jenkins():
            screenshot_path = "reports/screenshots/valid_login_result.png"
            page.screenshot(path=screenshot_path)
            allure.attach.file(screenshot_path, name="Valid Login Result", attachment_type=allure.attachment_type.PNG)
        
        # Should succeed
        assert success, "Login should succeed with valid credentials"
    
    with allure.step("Verify navigation to dashboard"):
        # Verify we're on the dashboard
        is_on_dashboard = login_page.page.is_visible(login_page.MAIN_NAVBAR, timeout=10000)
        allure.attach(f"Main navbar visible: {is_on_dashboard}", name="Dashboard Navigation Check", attachment_type=allure.attachment_type.TEXT)
        assert is_on_dashboard, "Main navbar should be visible after login"
    
    # Performance tracking
    total_time = time.time() - start_time
    login_summary = (
        f"VALID LOGIN SUMMARY\n"
        f"Login Success: {'✓' if success else '✗'}\n"
        f"Dashboard Access: {'✓' if is_on_dashboard else '✗'}\n"
        f"Total Time: {total_time:.1f}s\n"
        f"Performance: {'Fast' if total_time < 10 else 'Slow'}"
    )
    allure.attach(login_summary, name="Valid Login Summary", attachment_type=allure.attachment_type.TEXT)
    print(f"Valid login test completed in {total_time:.1f}s")

    
    # Assertions
    assert success, "Login should succeed"
    assert total_time < 20, f"Login too slow: {total_time:.1f}s"