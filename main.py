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
import tkinter as tk
from tkinter import messagebox
import time
import datetime
import sys

# Constants
SECONDS_TO_WAIT = 5                                 # Wait up to 5 seconds for new page to load
MINUTES_TO_SECONDS = 60                             # 60 seconds/minute

# Global Variables
schedulerURL = "https://resources.msoe.edu/sched/"  # URL to MSOE Scheduler page
textFieldClassName = "form-control"                 # HTML textarea class name
textFieldID = "wishlist-wishlist"                   # HTML textarea ID
submitButtonClass = "msoe-submit-button"            # Submit element class
checkboxClass = "fs-checkbox-element"               # Class name of checkbox

# Create an Options object for Chrome
options = Options()

# Add an argument to suppress logging messages below the level of WARNING (log level 3)
options.add_argument("--log-level=3")

# Create a Service object for ChromeDriver, installing it automatically if necessary
service = Service(ChromeDriverManager().install())

# Create a WebDriver object for Chrome, using the specified service and options
driver = webdriver.Chrome(service=service, options=options)


def pop_up_alert(message):
    """
    Display a pop-up alert with the given message.

    Parameters:
    - message (str): The message to be displayed in the pop-up alert.

    Returns:
    None
    """
    try: 
        root = tk.Tk()                                      # Create a new Tkinter window
        root.after(SECONDS_TO_WAIT* 1000, root.destroy)     # Wait five seconds then destroy window
        messagebox.showinfo("Class Availability Alert", message) # Display a message box with the title "Class Availability Alert" and the content specified by the variable "message"
        root.mainloop()                                          # Add mainloop to display the pop-up and wait for user interaction
    except KeyboardInterrupt:
        print("\nExiting program.")
        
def enter_class(coursePrefix, courseCode, sectionNumber):
    """
    Enters the class information into the scheduler webpage and submits the form.

    Args:
        coursePrefix (str): The prefix of the course (e.g., "CS", "MATH").
        courseCode (str): The code of the course (e.g., "101", "202").
        sectionNumber (str): The section number of the course (e.g., "001", "002").

    Returns:
        None
    """
    # Go to the Webpage
    driver.get(schedulerURL) 
    
    # Find the text field
    textField = driver.find_element(By.CLASS_NAME, textFieldClassName)

    # Clear textfield
    textField.clear()    

    # Type in course
    textField.send_keys(coursePrefix + " " + courseCode +" "+ sectionNumber + " " + Keys.ENTER)

    # Click Submit button to redirect to available classes
    submitButton = driver.find_element(By.CLASS_NAME, submitButtonClass)
    submitButton.send_keys(Keys.ENTER)

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
    print("1. Enter the course prefix, course code, and THREE-DIGIT section number for each class you want to check.")
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

    Raises:
        NoSuchElementException: If the class is not offered this semester.
        TimeoutException: If the operation times out.
        Exception: If an unexpected error occurs.
    """
    try:
        enter_class(coursePrefix, courseCode, sectionNumber)

        # Wait up to SECONDS_TO_WAIT seconds for the section-table tag to be present
        section_table = WebDriverWait(driver, SECONDS_TO_WAIT).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'section-table'))
        )

        # Find the tbody tag inside the section-table
        tbody = section_table.find_element(By.TAG_NAME, 'tbody')
        
        # Find all <tr> elements within the <tbody>
        rows = tbody.find_elements(By.TAG_NAME, 'tr')
        
        # Check if the tbody tag is empty
        if not rows:  # Check if rows is empty
            message = f'Class {coursePrefix} {courseCode} {sectionNumber} Is not available this semester. Exiting Program!'
            print(message)
            pop_up_alert(message)
            sys.exit()
        else:
            for row in rows:
                if sectionNumber in row.text:
                    
                    # Find the checkbox in the row
                    checkbox = row.find_element(By.CLASS_NAME, checkboxClass)

                    # Check if the checkbox is checked
                    if checkbox.is_selected():
                        message = f'Class {coursePrefix} {courseCode} {sectionNumber} IS available! SCHEDULE NOW!!!!'
                        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}: {message}")
                        pop_up_alert(message)
                    else:
                        message = f'Class {coursePrefix} {courseCode} {sectionNumber} NOT available'
                        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}: {message}")
                        pop_up_alert(message)
                    break

    except KeyboardInterrupt:
        print("\nExiting program.")
    except NoSuchElementException:
        message = "That class is not offered this semester"
        print(message)
        pop_up_alert(message)
        sys.exit()
    except TimeoutException:
        print("The operation timed out.")
        sys.exit()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit()

def check_schedule_availability():
    """
    Checks the availability of classes in the schedule.

    This function prompts the user to enter the course information for each class in the schedule,
    including the course prefix, course code, and section number. It then prompts the user to enter
    the check interval in seconds or minutes. The function continuously checks the availability of
    each class at the specified interval until the program is interrupted by the user.

    Returns:
        None
    """
    print_help_menu()
    classes = input("Enter the course prefix, course code, and section number for each class, separated by commas: ").split(',')
    for class_info in classes:
        args = class_info.split()
        if len(args) != 3 or not args[2].isdigit() or len(args[2]) != 3:
            print("Invalid class information. Please enter the course prefix, course code, and a three-digit section number for each class.")
            return
    check_interval_sec = input("Enter the check interval in seconds (-s) or minutes (-m): ").split()
    if len(check_interval_sec) != 2 or check_interval_sec[0] not in ['-s', '-m']:
        print("Invalid check interval. Please enter the check interval in seconds (-s) or minutes (-m).")
        return
    else:
        if check_interval_sec[0] == '-s':
            check_interval_sec = int(check_interval_sec[1])
        elif check_interval_sec[0] == '-m':
            check_interval_sec = int(check_interval_sec[1]) * MINUTES_TO_SECONDS
    try:
        while True:
            for class_info in classes:
                coursePrefix, courseCode, sectionNumber = class_info.split()
                check_class_availability(coursePrefix, courseCode, sectionNumber)
            time.sleep(check_interval_sec)
    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        driver.quit()

check_schedule_availability()