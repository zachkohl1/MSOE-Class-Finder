"""
File: main.py
Author: Zach Kohlman
Date: 3/13/2024
Description: This script checks the availability of classes at regular intervals.
             The user can specify the classes to check and the check interval.
             The script uses Selenium to interact with the class scheduling website.
Usage: Run the script and follow the prompts to enter the classes and check interval.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Constants
SECONDS_TO_WAIT = 5                                 # Wait up to 5 seconds for checkbox to load
MINUTES_TO_SECONDS = 60                             # 60 seconds/minute

# Global Variables
schedulerURL = "https://resources.msoe.edu/sched/"  # URL to MSOE Scheduler page
textFieldClassName = "form-control"                 # HTML textarea class name
textFieldID = "wishlist-wishlist"                   # HTML textarea ID
submitButtonClass = "msoe-submit-button"            # Submit element class
checkboxClass = "fs-checkbox-element"               # Class name of checkbox


# Set Chrome options to suppress certificate warnings
options = Options()
options.add_argument("--log-level=3")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def print_help_menu():
    """
    Prints the help menu for the Class Availability Checker script.
    """
    print("\n========================================")
    print("     CLASS AVAILABILITY CHECKER")
    print("========================================\n")
    print("Welcome to the Class Availability Checker!")
    print("This script will check the availability of the classes you specify at regular intervals.")
    print("\nInstructions:")
    print("1. Enter the course prefix, course code, and section number for each class you want to check.")
    print("   Format: PREFIX CODE SECTION, e.g., CSE 1010 001")
    print("   If checking multiple classes, separate each class with a comma.")
    print("2. Enter the check interval in seconds or minutes.")
    print("   Format: -s SECONDS or -m MINUTES, e.g., -s 30 or -m 5")
    print("\nThe script will then check the availability of each class and print the results.")
    print("To stop the script, press Ctrl+C.\n")

def check_class_availability(coursePrefix, courseCode, sectionNumber):
    """
    Checks the availability of a class on the MSOE Scheduler page.

    Args:
        coursePrefix (str): The prefix of the course.
        courseCode (str): The code of the course.
        sectionNumber (str): The section number of the course.

    Returns:
        None
    """
    try:
        # Go to the Webpage
        driver.get(schedulerURL) 

        # Find the text field
        textField = driver.find_element(By.CLASS_NAME, textFieldClassName)

        textField.send_keys(coursePrefix + " " + courseCode +" "+ sectionNumber + " " + Keys.ENTER)

        # Click Submit button to redirect to available classes
        submitButton = driver.find_element(By.CLASS_NAME, submitButtonClass)
        submitButton.send_keys(Keys.ENTER)

        # Wait up to 10 seconds for the checkbox to be present
        checkbox = WebDriverWait(driver, SECONDS_TO_WAIT).until(
            EC.presence_of_element_located((By.CLASS_NAME, checkboxClass))
        )

        # Check if the checkbox is selected
        if checkbox.is_selected():
            print(f'Class {coursePrefix} {courseCode} {sectionNumber} IS available! SCHEDULE NOW!!!!')
        else:
            print(f'Class {coursePrefix} {courseCode} {sectionNumber} NOT available')
    except NoSuchElementException:
        print("The element you're trying to find does not exist.")
    except TimeoutException:
        print("The operation timed out.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def check_schedule_availability():
    """
    Checks the availability of multiple classes at regular intervals.

    Returns:
        None
    """
    # Print menu
    print_help_menu()
    
    # Get user input
    classes = input("Enter the course prefix, course code, and section number for each class, separated by commas: ").split(',')
    
    # Get user input for check interval
    check_inverval_sec = input("Enter the check interval in seconds (-s) or minutes (-m): ").split()
    if len(check_inverval_sec) != 2 or check_inverval_sec[0] not in ['-s', '-m']:
        print("Invalid check interval. Defaulting to 5 minutes.")
        check_inverval_sec = 300
    else:
        if check_inverval_sec[0] == '-s':
            check_inverval_sec = int(check_inverval_sec[1])
        elif check_inverval_sec[0] == '-m':
            check_inverval_sec = int(check_inverval_sec[1]) * MINUTES_TO_SECONDS
        
        
    while True:
        for class_info in classes:
            coursePrefix, courseCode, sectionNumber = class_info.split()
            check_class_availability(coursePrefix, courseCode, sectionNumber)
        
        # Wait for 5 minutes before checking again
        time.sleep(check_inverval_sec)

# Main function
check_schedule_availability()
driver.quit()