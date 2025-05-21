# conftest.py
import pytest
import json
import os
from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage

def is_jenkins():
    """Check if running in Jenkins environment"""
    return any([
        os.getenv('JENKINS_URL'),
        os.getenv('CI') == 'true',
        os.getenv('JENKINS_BUILD') == 'true',
        os.getenv('BUILD_NUMBER'),
        'jenkins' in os.getenv('USER', '').lower(),
        'build' in os.getenv('USER', '').lower()
    ])

def is_headless_forced():
    """Check if headless mode is forced by environment"""
    return any([
        is_jenkins(),
        os.getenv('HEADLESS') == 'true',
        os.getenv('CI') == 'true'
    ])

# Load test configuration
@pytest.fixture(scope="session")
def config():
    try:
        with open('data/config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            # Convert string 'False'/'True' to boolean if needed
            if isinstance(config_data.get("headless"), str):
                config_data["headless"] = config_data["headless"].lower() == 'true'
            
            # Force headless in Jenkins regardless of config
            if is_headless_forced():
                config_data["headless"] = True
                print("🏗️  Jenkins/CI environment detected - forcing headless mode")
            
            return config_data
    except FileNotFoundError:
        # Default config if file not found
        default_config = {
            "base_url": "https://dev.nawat.ma",
            "username": "ecole.e2a",
            "password": "1@ayouris2",
            "headless": True,  
            "slow_mo": 0
        }
        
        # Force headless in Jenkins
        if is_headless_forced():
            default_config["headless"] = True
            
        return default_config

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Enhanced browser context with Jenkins optimizations"""
    jenkins_optimized_args = {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
        "ignore_https_errors": True,
        "accept_downloads": True,
        "has_touch": False,
        "is_mobile": False,
        "locale": "en-US",
        "permissions": [],
        "color_scheme": "light",
        "reduced_motion": "reduce",
        "bypass_csp": True,
    }
    
    if is_jenkins():
        # Additional Jenkins optimizations
        jenkins_optimized_args.update({
            "timeout": 15000,  # 15 second timeout
            "navigation_timeout": 20000,  # 20 second navigation timeout
        })
        print("🔧 Applied Jenkins browser context optimizations")
    
    return jenkins_optimized_args

@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Jenkins-optimized browser launch arguments"""
    base_args = [
        "--disable-dev-shm-usage",
        "--disable-extensions", 
        "--disable-gpu",
        "--disable-background-timer-throttling",
        "--disable-renderer-backgrounding",
        "--disable-features=TranslateUI",
        "--disable-ipc-flooding-protection",
        "--no-first-run",
        "--no-default-browser-check",
    ]
    
    if is_jenkins():
        # Additional Jenkins-specific flags for stability
        jenkins_args = [
            "--no-sandbox",
            "--disable-background-networking",
            "--disable-default-apps",
            "--disable-sync",
            "--metrics-recording-only",
            "--safebrowsing-disable-auto-update",
            "--disable-web-security",
            "--single-process",  # Better for Jenkins stability
        ]
        base_args.extend(jenkins_args)
        print(f"🚀 Applied {len(jenkins_args)} Jenkins browser optimizations")
    
    return {"args": base_args}

@pytest.fixture(scope="session")
def browser(config, browser_type_launch_args):
    with sync_playwright() as playwright:
        # Ensure headless is a boolean and force in Jenkins
        headless_value = config.get("headless")
        if isinstance(headless_value, str):
            headless_value = headless_value.lower() == 'true'
        
        # Always headless in Jenkins
        if is_jenkins():
            headless_value = True

        # Get slow_mo setting but reduce in Jenkins for speed
        slow_mo = config.get("slow_mo", 0)
        if is_jenkins() and slow_mo > 0:
            slow_mo = 0  # No slow motion in Jenkins
            print("⚡ Disabled slow motion for Jenkins performance")

        print(f"🌐 Launching browser (headless: {headless_value}, Jenkins: {is_jenkins()})")
        
        browser = playwright.chromium.launch(
            headless=headless_value,
            slow_mo=slow_mo,
            **browser_type_launch_args
        )
        yield browser
        browser.close()

@pytest.fixture
def page(browser, config):
    context = browser.new_context()
    page = context.new_page()
    
    # Jenkins-specific page optimizations
    if is_jenkins():
        # Set faster timeouts for Jenkins
        page.set_default_timeout(15000)  # 15 seconds
        page.set_default_navigation_timeout(20000)  # 20 seconds
    else:
        # Standard timeouts for local development
        page.set_default_timeout(30000)  # 30 seconds
        page.set_default_navigation_timeout(60000)  # 60 seconds

    # Ensure screenshots directory exists
    os.makedirs("reports/screenshots", exist_ok=True)

    yield page
    context.close()

@pytest.fixture
def logged_in_page(page, config):
    """Enhanced login fixture with Jenkins optimizations"""
    print(f"🔐 Attempting login (Jenkins mode: {is_jenkins()})...")
    
    login_page = LoginPage(page)
    
    # Navigate with environment-appropriate timeout
    try:
        login_page.navigate()
    except Exception as e:
        print(f"❌ Navigation failed: {e}")
        if not is_jenkins():  # Only screenshot in non-Jenkins to save time
            page.screenshot(path="reports/screenshots/navigation_failure.png")
        pytest.fail(f"Failed to navigate to login page: {e}")

    # Perform login
    success = login_page.login(
        config.get("username", "ecole.e2a"),
        config.get("password", "1@ayouris2")
    )

    if not success:
        # Take screenshot for debugging (but not in Jenkins to save time)
        error = login_page.get_error_message() or "Unknown error (possible timeout)"
        
        if not is_jenkins():
            page.screenshot(path="reports/screenshots/login_failure.png")
            print("📸 Login failure screenshot saved")
        
        print(f"❌ Login failed: {error}")
        pytest.fail(f"Login failed: {error}")

    # Success screenshot only in non-Jenkins environments
    if not is_jenkins():
        page.screenshot(path="reports/screenshots/successful_login.png")
        print("📸 Successful login screenshot saved")
    
    print("✅ Login successful")
    yield page

@pytest.fixture(autouse=True)
def test_environment_setup():
    """Automatic test environment configuration"""
    if is_jenkins():
        print("🏗️  Jenkins environment detected - optimizing for CI/CD")
        # Set environment variables for test optimization
        os.environ["FAST_MODE"] = "true"
        os.environ["REDUCED_WAITS"] = "true"
        os.environ["MINIMAL_SCREENSHOTS"] = "true"
        os.environ["ALLOW_DATA_MISMATCHES"] = "true"
        
        # Print Jenkins info
        build_number = os.getenv('BUILD_NUMBER', 'Unknown')
        node_name = os.getenv('NODE_NAME', 'Unknown')
        print(f"📊 Build: {build_number} | Node: {node_name}")
    else:
        print("💻 Local development environment detected")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Enhanced error reporting with Jenkins context"""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call":
        if rep.failed and is_jenkins():
            # Add Jenkins-specific failure information
            jenkins_info = (
                f"Jenkins Environment Details:\n"
                f"  Build Number: {os.getenv('BUILD_NUMBER', 'Unknown')}\n"
                f"  Node Name: {os.getenv('NODE_NAME', 'Unknown')}\n"
                f"  Workspace: {os.getenv('WORKSPACE', 'Unknown')}\n"
                f"  Build URL: {os.getenv('BUILD_URL', 'Unknown')}"
            )
            
            if hasattr(rep.longrepr, 'addsection'):
                rep.longrepr.addsection("Jenkins Build Info", jenkins_info)
        
        elif rep.passed and is_jenkins():
            print(f"✅ {item.name} passed in Jenkins")

def pytest_configure(config):
    """Configure pytest for different environments"""
    if is_jenkins():
        print("🔧 Configuring pytest for Jenkins environment...")
        
        # Add custom markers
        config.addinivalue_line("markers", "jenkins: mark test as Jenkins-optimized")
        config.addinivalue_line("markers", "slow: mark test as slow (may be skipped in Jenkins)")
        
        # Adjust verbosity for Jenkins
        if config.option.verbose > 1:
            config.option.verbose = 1  # Reduce verbosity in Jenkins
            
        print("⚙️  Jenkins pytest configuration applied")
    else:
        print("🔧 Configuring pytest for local development...")

def pytest_collection_modifyitems(config, items):
    """Modify test collection based on environment"""
    if is_jenkins():
        print(f"📋 Collected {len(items)} tests for Jenkins execution")
        
        # Add Jenkins marker to all tests
        jenkins_marker = pytest.mark.jenkins
        for item in items:
            item.add_marker(jenkins_marker)
            
        print("🏷️  Added Jenkins marker to all tests")

@pytest.fixture
def jenkins_info():
    """Provide Jenkins build information to tests"""
    if is_jenkins():
        return {
            "build_number": os.getenv('BUILD_NUMBER'),
            "node_name": os.getenv('NODE_NAME'), 
            "workspace": os.getenv('WORKSPACE'),
            "build_url": os.getenv('BUILD_URL'),
            "is_jenkins": True
        }
    else:
        return {"is_jenkins": False}