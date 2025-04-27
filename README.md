
# Selenium Web Scraping Project

This project demonstrates how to use Selenium for web scraping with Microsoft Edge. The goal is to automate the process of interacting with a webpage, opening new windows, and scraping content from them.

## Setup Instructions

Follow these steps to set up and run the project:

### 1. Create a Virtual Environment
First, create a virtual environment to keep your dependencies isolated.

```bash
python -m venv .env
```

### 2. Activate the Virtual Environment
Activate the virtual environment.

- **Windows:**
  ```bash
  .env\Scripts\activate
  ```

- **Mac/Linux:**
  ```bash
  source .env/bin/activate
  ```

### 3. Install Required Dependencies
Once the virtual environment is active, install the required packages listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4. Download Edge WebDriver
Download the correct version of the Microsoft Edge WebDriver that matches your current Edge browser version:

[Download Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH)

Extract the `msedgedriver.exe` to the root directory of the project.

### 5. Running the Script
To run the script directly in Python:

```bash
python enquiry-scraping-selenium.py
```

### 6. Creating a Distributable Executable
If you'd like to create a standalone executable for the script, run the following command:

```bash
pyinstaller --onefile --add-binary "msedgedriver.exe;." enquiry-scraping-selenium.py
```

This will generate an executable file that includes the script and WebDriver, so it can be run on other machines without needing to install Python or Selenium.

## Notes
- Ensure that the version of `msedgedriver.exe` matches the installed Microsoft Edge version.
- This project was tested with Python 3.x and works best when using the appropriate versions of dependencies.
