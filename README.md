# MSOE Class Availability Checker

## Description
This program checks the availability of classes at MSOE at regular intervals and displays desktop notifications to alert the user about the availability status of the classes. The user can specify the classes to check and the check interval. The script uses Selenium to interact with the class scheduling website and the plyer library to display desktop notifications.

## Usage
Run the program and follow the prompts to enter the classes and check interval. Enter the course prefix, course code, and section number for each class you want to check. If checking multiple classes, separate each class with a comma. Then, enter the check interval in seconds or minutes. For example, `-s 30` for 30 seconds or `-m 5` for 5 minutes.

## Dependencies
This script uses the Selenium and plyer Python libraries and ChromeDriver. Make sure to:

1. Install and update Python
2. Install webdrivers for Selenium with `pip install webdriver-manager`
3. Install the Selenium Python library with `pip install selenium`
4. Install the plyer Python library with `pip install plyer`
5. Download the correct version of ChromeDriver based on your installed version of Chrome from [here](https://googlechromelabs.github.io/chrome-for-testing/) and add it to your system's PATH.
