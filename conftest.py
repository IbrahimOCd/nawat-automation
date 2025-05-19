# conftest.py
import pytest
import json
import os
import time
from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage

# Load test configuration
@pytest.fixture(scope="session")
def config():
    try:
        with open('data/config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            # Convert string 'False'/'True' to boolean if needed
            if isinstance(config_data.get("headless"), str):
                config_data["headless"] = config_data["headless"].lower() == 'true'
            return config_data
    except FileNotFoundError:
        # Default config if file not found
        return {
            "base_url": "https://dev.nawat.ma",
            "username": "ecole.e2a",
            "password": "1@ayouris2",
            "headless": False 
        }

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1366, "height": 768},  # CHANGED: Smaller viewport for speed
        "java_script_enabled": True,
        "bypass_csp": True, 
        "ignore_https_errors": True
    }

@pytest.fixture(scope="session")
def browser(config):
    with sync_playwright() as playwright:
        headless_value = config.get("headless", True)  # Default to headless
        if isinstance(headless_value, str):
            headless_value = headless_value.lower() == 'true'
        
        # CHANGED: Remove slow_mo completely for speed
        browser = playwright.chromium.launch(
            headless=headless_value,
            args=[
                "--disable-extensions",
                "--disable-dev-shm-usage", 
                "--disable-gpu",
                "--no-sandbox",
                # ADDED: Performance args
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials"
            ]
        )
        yield browser
        browser.close()

# Create a session-scoped authenticated context for faster tests
@pytest.fixture(scope="session")
def authenticated_context(browser, config):
    # Create a context
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True
    )
    
    # Create a page for login
    page = context.new_page()
    
    # Perform login
    login_page = LoginPage(page)
    login_page.navigate()
    
    success = login_page.login(
        config.get("username", "ecole.e2a"),
        config.get("password", "1@ayouris2")
    )
    
    if not success:
        # Take a screenshot of the failure
        os.makedirs("reports/screenshots", exist_ok=True)
        page.screenshot(path="reports/screenshots/session_login_failure.png")
        pytest.fail("Failed to create authenticated session")
    
    # Wait for the app to be fully loaded before using this context
    try:
        page.wait_for_selector("//div[contains(@class,'o_home_menu')]", timeout=15000)
    except:
        page.screenshot(path="reports/screenshots/session_load_failure.png")
    
    # Close the page but keep the authenticated context
    page.close()
    
    yield context
    context.close()

# Regular page fixture (use only when needed)
@pytest.fixture
def page(browser, config):
    context = browser.new_context()
    page = context.new_page()
    
    # Ensure screenshots directory exists
    os.makedirs("reports/screenshots", exist_ok=True)
    
    yield page
    context.close()

# Main fixture for tests - uses the authenticated context
@pytest.fixture
def logged_in_page(authenticated_context):
    # Create a new page in the authenticated context
    page = authenticated_context.new_page()
    
    # Go to the app URL
    page.goto("https://dev.nawat.ma/web", wait_until="domcontentloaded")
    
    # Wait for initial load
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except:
        pass  # Continue even if timeout
    
    yield page
    page.close()

# Add a fixture for maximizing test parallelization
@pytest.fixture(scope="session", autouse=True)
def configure_xdist():
    """Configure pytest-xdist for better parallel execution if available."""
    return