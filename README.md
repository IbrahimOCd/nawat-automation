`## Setup Instructions

1. Clone the repository
2. Create a Python virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `.\venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Install Playwright browsers: `playwright install`

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_common.py

# Run with visible browser
pytest --headed
