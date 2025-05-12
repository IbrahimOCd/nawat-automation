# tests/test_common.py
import pytest
import time

def test_successful_login(logged_in_page):
    """Test that login is successful and main navbar is displayed"""
    # Make sure we're fully loaded
    time.sleep(2)
    
    # Verify main components are visible
    assert logged_in_page.is_visible(".o_main_navbar")
    assert logged_in_page.is_visible(".o_content")
    
    # Take screenshot after verifying success
    logged_in_page.screenshot(path="reports/screenshots/post_login_verification.png")
    
def test_module_navigation(logged_in_page):
    """Test that all modules are accessible from the main menu"""
    modules = [
        "Accès", "Finance", "Planification", "Communication", 
        "Vie scolaire", "Transport", "Préinscription", "Discussion"
    ]
    
    for module in modules:
        # Click on module in sidebar using the working selector
        logged_in_page.click(f"//span[@class='nav-title text-truncate ms-3' and @title='{module}']")
        
        # Wait for page and data to load
        logged_in_page.wait_for_selector(".o_action", state="visible", timeout=10000)
        time.sleep(3)  # Additional wait for data
        
        # Take a screenshot for verification after data has loaded
        logged_in_page.screenshot(path=f"reports/screenshots/navigation_{module}.png")
        
        # Verify some content has loaded
        assert logged_in_page.is_visible("//div[contains(@class,'o_action_manager')]")