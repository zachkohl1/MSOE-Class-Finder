# MSOE Class Availability Checker

## Description
This script checks the availability of classes at MSOE at regular intervals. The user can specify the classes to check and the check interval. The script uses Selenium to interact with the class scheduling website.

## Usage
Run the script and follow the prompts to enter the classes and check interval. Enter the course prefix, course code, and section number for each class you want to check. If checking multiple classes, separate each class with a comma. Then, enter the check interval in seconds or minutes. For example, `-s 30` for 30 seconds or `-m 5` for 5 minutes.

## Dependencies
This script uses the Selenium Python library and ChromeDriver. Make sure to:

1. Install and update Python with `sudo apt-get install python3`
2. Install the Selenium Python library with `pip install selenium`
3. Download the correct version of ChromeDriver based on your installed version of Chrome from [here](https://googlechromelabs.github.io/chrome-for-testing/) and add it to your system's PATH.