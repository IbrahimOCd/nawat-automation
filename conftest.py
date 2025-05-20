# conftest.py
import pytest
import json
import os
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
            "headless": True,  
            "slow_mo": 0
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
        # Ensure headless is a boolean
        headless_value = config.get("headless")
        if isinstance(headless_value, str):
            headless_value = headless_value.lower() == 'true'

        browser = playwright.chromium.launch(
            headless=headless_value
        )
        yield browser
        browser.close()

@pytest.fixture
def page(browser, config):
    context = browser.new_context()
    page = context.new_page()

    # Ensure screenshots directory exists
    os.makedirs("reports/screenshots", exist_ok=True)

    yield page
    context.close()

@pytest.fixture
def logged_in_page(page, config):
    login_page = LoginPage(page)
    login_page.navigate()

    success = login_page.login(
        config.get("username", "ecole.e2a"),
        config.get("password", "1@ayouris2")
    )

    if not success:
        # Take a screenshot of the failure
        page.screenshot(path="reports/screenshots/login_failure.png")
        error = login_page.get_error_message() or "Unknown error (possible timeout)"
        pytest.fail(f"Login failed: {error}")

    # Take a screenshot of successful login
    page.screenshot(path="reports/screenshots/successful_login.png")
    yield page