# conftest.py
import pytest
import json
from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage

# Load test configuration
@pytest.fixture(scope="session")
def config():
    try:
        with open('data/config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Default config if file not found
        return {
            "base_url": "https://dev.nawat.ma",
            "username": "admin",
            "password": "123456",
            "headless": False,
            "slow_mo": 50
        }

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
    }

@pytest.fixture(scope="session")
def browser(config):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=config.get("headless", False),
            slow_mo=config.get("slow_mo", 50)
        )
        yield browser
        browser.close()

@pytest.fixture
def page(browser, config):
    context = browser.new_context()
    page = context.new_page()
    yield page
    # Take screenshot on failure
    context.close()

@pytest.fixture
def logged_in_page(page, config):
    login_page = LoginPage(page)
    login_page.navigate()
    
    success = login_page.login(
        config.get("username", "admin"),
        config.get("password", "123456")
    )
    
    if not success:
        # Take a screenshot of the failure
        page.screenshot(path="reports/screenshots/login_failure.png")
        error = login_page.get_error_message() or "Unknown error (possible timeout)"
        pytest.fail(f"Login failed: {error}")
    
    # Take a screenshot of successful login
    page.screenshot(path="reports/screenshots/successful_login.png")
    yield page