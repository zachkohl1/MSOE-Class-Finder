"""
main.py

This script provides a GUI application to check the availability of classes at MSOE using Selenium for web automation.
It includes functionalities to add, edit, and remove classes, set check intervals, and display the status of class availability checks.
"""
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from plyer import notification
import time
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from queue import Queue

# Constants
SECONDS_TO_WAIT = 5
MINUTES_TO_SECONDS = 60

# Global Variables
SCHEDULER_URL = "https://resources.msoe.edu/sched/"
TEXT_FIELD_CLASS_NAME = "form-control"
CHECKBOX_CLASS = "fs-checkbox-element"
SUBMIT_BUTTON_CLASS = "msoe-submit-button"
PATH_TO_DRIVER = "chromedriver.exe"

# Create an Options object for Chrome
options = Options()
options.add_argument("--log-level=3")
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Create a Service object for ChromeDriver, installing it automatically if necessary
service = Service(PATH_TO_DRIVER)

# Create a WebDriver object for Chrome, using the specified service and options
driver = webdriver.Chrome(service=service, options=options)

driver.minimize_window()

# Create a queue for notifications
notification_queue = Queue()

def pop_up_alert(message):
    """
    Add a notification to the queue.

    Parameters:
    - message: The notification message to display.
    """
    notification_queue.put(message)

def notification_worker():
    """
    Process notifications from the queue.
    """
    while True:
        message = notification_queue.get()
        notification.notify(
            title="Class Available!",
            message=message,
            timeout=1  # Set a very short timeout (1 second)
        )
        time.sleep(1.1)  # Wait slightly longer than the timeout before processing the next notification
        notification_queue.task_done()

# Start the notification worker thread
threading.Thread(target=notification_worker, daemon=True).start()

def enter_class(coursePrefix, courseCode, sectionNumber):
    """
    Enters the class information into the scheduler webpage and submits the form.

    Parameters:
    - coursePrefix: The prefix of the course (e.g., "CPE").
    - courseCode: The code of the course (e.g., "4610").
    - sectionNumber: The section number of the course (e.g., "111").
    """
    driver.get(SCHEDULER_URL)
    textField = driver.find_element(By.CLASS_NAME, TEXT_FIELD_CLASS_NAME)
    textField.clear()
    textField.send_keys(f"{coursePrefix} {courseCode} {sectionNumber} {Keys.ENTER}")
    submitButton = driver.find_element(By.CLASS_NAME, SUBMIT_BUTTON_CLASS)
    submitButton.send_keys(Keys.ENTER)

def check_class_availability(coursePrefix, courseCode, sectionNumber):
    """
    Checks the availability of a class on the MSOE Scheduler page.

    Parameters:
    - coursePrefix: The prefix of the course (e.g., "CPE").
    - courseCode: The code of the course (e.g., "4610").
    - sectionNumber: The section number of the course (e.g., "111").
    """
    try:
        driver.get(SCHEDULER_URL)
        enter_class(coursePrefix, courseCode, sectionNumber)
        
        # Wait for either the checkbox or an error message
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f".{CHECKBOX_CLASS}, .flash-error"))
            )
        except TimeoutException:
            return False, f'Timeout: Class {coursePrefix} {courseCode} {sectionNumber} page did not load properly'
        
        # Check if an error message is present
        error_message = driver.find_elements(By.CLASS_NAME, "flash-error")
        if error_message:
            error_text = error_message[0].text
            if "unknown or not offered" in error_text:
                unknown_courses = error_message[0].find_elements(By.TAG_NAME, "li")
                for course in unknown_courses:
                    if f"{coursePrefix}-{courseCode}" in course.text:
                        return False, f'Class {coursePrefix} {courseCode} {sectionNumber} is unknown or not offered for the selected semester'
            return False, f'Error for {coursePrefix} {courseCode} {sectionNumber}: {error_text}'
        
        # If no error, look for the checkbox
        try:
            checkbox = driver.find_element(By.CSS_SELECTOR, f'input[name="courses[{coursePrefix}-{courseCode}][{sectionNumber}]"]')
        except NoSuchElementException:
            return False, f'Could not find section number {sectionNumber} for class {coursePrefix} {courseCode} {sectionNumber}' 
        
        if checkbox.is_selected():
            return True, f'Class {coursePrefix} {courseCode} {sectionNumber} IS available!'
        else:
            return False, f'Class {coursePrefix} {courseCode} {sectionNumber} NOT available'
    except NoSuchElementException as e:
        return False, f'Element not found for {coursePrefix} {courseCode} {sectionNumber}: {str(e)}'
    except TimeoutException as e:
        return False, f'Timeout occurred for {coursePrefix} {courseCode} {sectionNumber}: {str(e)}'
    except StaleElementReferenceException as e:
        return False, f'Stale element for {coursePrefix} {courseCode} {sectionNumber}: {str(e)}'
    except WebDriverException as e:
        return False, f'WebDriver error for {coursePrefix} {courseCode} {sectionNumber}: {str(e)}'
    except Exception as e:
        return False, f'Unexpected error for {coursePrefix} {courseCode} {sectionNumber}: {str(e)}'
class ClassCheckerApp:
    """
    A class representing a Class Availability Checker application.
    Attributes:
    - master: The master window of the application.
    - classes: A list of classes to check availability for.
    - check_interval: The interval (in seconds) between availability checks.
    - checking: A boolean indicating whether availability checks are currently running.
    Methods:
    - __init__(self, master): Initializes the ClassCheckerApp instance.
    - set_placeholder(self, entry, placeholder): Sets a placeholder text for an entry widget.
    - clear_placeholder(self, event, placeholder): Clears the placeholder text when an entry widget is focused.
    - restore_placeholder(self, event, placeholder): Restores the placeholder text when an entry widget loses focus.
    - create_class_entry_frame(self): Creates and places the widgets for adding a class.
    - create_class_list_frame(self): Creates and places the widgets for displaying the class list.
    - create_interval_frame(self): Creates and places the widgets for setting the check interval.
    - create_status_frame(self): Creates and places the widgets for displaying the status.
    - add_class(self): Adds a class to the class list.
    - clear_entry_fields(self): Clears the entry fields for adding a class.
    - edit_class(self): Opens a window for editing a selected class.
    - remove_class(self): Removes a selected class from the class list.
    - start_checking(self): Starts checking the availability of classes.
    - check_schedule_availability(self): Checks the availability of classes at regular intervals.
    - stop_checking(self): Stops checking the availability of classes.
    """
    def __init__(self, master):
        """
        Initialize the ClassCheckerApp with the main window.

        Parameters:
        - master: The main window of the application.
        """
        self.master = master
        master.title("Class Availability Checker")
        master.geometry("700x500")

        self.classes = []
        self.check_interval = 60
        self.checking = False

        # Create and place widgets
        self.create_class_entry_frame()
        self.create_class_list_frame()
        self.create_interval_frame()
        self.create_status_frame()

    def set_placeholder(self, entry, placeholder):
        """
        Set a placeholder text in an entry widget.

        Parameters:
        - entry: The entry widget.
        - placeholder: The placeholder text.
        """
        entry.insert(0, placeholder)
        entry.config(foreground='grey')
        entry.bind("<FocusIn>", lambda event: self.clear_placeholder(event, placeholder))
        entry.bind("<FocusOut>", lambda event: self.restore_placeholder(event, placeholder))

    def clear_placeholder(self, event, placeholder):
        """
        Clear the placeholder text when the entry widget gains focus.

        Parameters:
        - event: The focus event.
        - placeholder: The placeholder text.
        """
        if event.widget.get() == placeholder:
            event.widget.delete(0, tk.END)
            event.widget.config(foreground='black')

    def restore_placeholder(self, event, placeholder):
        """
        Restore the placeholder text when the entry widget loses focus.

        Parameters:
        - event: The focus event.
        - placeholder: The placeholder text.
        """
        if not event.widget.get():
            event.widget.insert(0, placeholder)
            event.widget.config(foreground='grey')

    def create_class_entry_frame(self):
        """
        Create the frame for entering class information.
        """
        entry_frame = ttk.LabelFrame(self.master, text="Add Class")
        entry_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(entry_frame, text="Course Prefix:").grid(row=0, column=0, padx=5, pady=5)
        self.prefix_entry = ttk.Entry(entry_frame, width=10)
        self.prefix_entry.grid(row=0, column=1, padx=5, pady=5)
        self.set_placeholder(self.prefix_entry, "CPE")

        ttk.Label(entry_frame, text="Course Number:").grid(row=0, column=2, padx=5, pady=5)
        self.number_entry = ttk.Entry(entry_frame, width=10)
        self.number_entry.grid(row=0, column=3, padx=5, pady=5)
        self.set_placeholder(self.number_entry, "4610")

        ttk.Label(entry_frame, text="Section:").grid(row=0, column=4, padx=5, pady=5)
        self.section_entry = ttk.Entry(entry_frame, width=10)
        self.section_entry.grid(row=0, column=5, padx=5, pady=5)
        self.set_placeholder(self.section_entry, "111")

        self.add_button = ttk.Button(entry_frame, text="Add Class", command=self.add_class)
        self.add_button.grid(row=0, column=6, padx=5, pady=5)
   
    def create_class_list_frame(self):
        """
        Create the frame for displaying the list of classes.
        """
        list_frame = ttk.LabelFrame(self.master, text="Class List")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.class_tree = ttk.Treeview(list_frame, columns=("Prefix", "Number", "Section"), show="headings")
        self.class_tree.heading("Prefix", text="Prefix")
        self.class_tree.heading("Number", text="Number")
        self.class_tree.heading("Section", text="Section")
        self.class_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.class_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.class_tree.configure(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(list_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.edit_button = ttk.Button(button_frame, text="Edit", command=self.edit_class)
        self.edit_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.remove_button = ttk.Button(button_frame, text="Remove", command=self.remove_class)
        self.remove_button.pack(side=tk.LEFT, padx=5, pady=5)

    def create_interval_frame(self):
        """
        Create the frame for setting the check interval.
        """
        interval_frame = ttk.LabelFrame(self.master, text="Check Interval")
        interval_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(interval_frame, text="Check interval (seconds):").pack(side=tk.LEFT, padx=5)
        self.interval_entry = ttk.Entry(interval_frame, width=10)
        self.interval_entry.insert(0, "60")
        self.interval_entry.pack(side=tk.LEFT, padx=5)

        self.start_button = ttk.Button(interval_frame, text="Start Checking", command=self.start_checking)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(interval_frame, text="Stop Checking", command=self.stop_checking)
        self.stop_button.pack(side=tk.LEFT, padx=5)

    def create_status_frame(self):
        """
        Create the frame for displaying the status of the checking process.
        """
        status_frame = ttk.LabelFrame(self.master, text="Status")
        status_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.status_text = tk.Text(status_frame, wrap=tk.WORD, width=70, height=10)
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.configure(yscrollcommand=scrollbar.set)

    def add_class(self):
        """
        Add a class to the list of classes to be checked.
        """
        prefix = self.prefix_entry.get().strip().upper()
        number = self.number_entry.get().strip()
        section = self.section_entry.get().strip()

        if prefix and number and section:
            class_info = f"{prefix} {number} {section}"
            self.classes.append(class_info)
            self.class_tree.insert("", tk.END, values=(prefix, number, section))
            self.clear_entry_fields()
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    def clear_entry_fields(self):
        """
        Clear the entry fields for class information.
        """
        self.prefix_entry.delete(0, tk.END)
        self.number_entry.delete(0, tk.END)
        self.section_entry.delete(0, tk.END)

    def edit_class(self):
        """
        Edit the selected class in the list of classes.
        """
        selected_item = self.class_tree.selection()
        if selected_item:
            item = selected_item[0]
            values = self.class_tree.item(item, "values")
            
            edit_window = tk.Toplevel(self.master)
            edit_window.title("Edit Class")

            ttk.Label(edit_window, text="Course Prefix:").grid(row=0, column=0, padx=5, pady=5)
            prefix_entry = ttk.Entry(edit_window, width=10)
            prefix_entry.insert(0, values[0])
            prefix_entry.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(edit_window, text="Course Number:").grid(row=1, column=0, padx=5, pady=5)
            number_entry = ttk.Entry(edit_window, width=10)
            number_entry.insert(0, values[1])
            number_entry.grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(edit_window, text="Section:").grid(row=2, column=0, padx=5, pady=5)
            section_entry = ttk.Entry(edit_window, width=10)
            section_entry.insert(0, values[2])
            section_entry.grid(row=2, column=1, padx=5, pady=5)

            def save_changes():
                """
                Save the changes made to the class information.
                """
                new_prefix = prefix_entry.get().strip().upper()
                new_number = number_entry.get().strip()
                new_section = section_entry.get().strip()

                if new_prefix and new_number and new_section:
                    new_class_info = f"{new_prefix} {new_number} {new_section}"
                    index = self.classes.index(f"{values[0]} {values[1]} {values[2]}")
                    self.classes[index] = new_class_info
                    self.class_tree.item(item, values=(new_prefix, new_number, new_section))
                    edit_window.destroy()
                else:
                    messagebox.showerror("Error", "Please fill in all fields.")

            ttk.Button(edit_window, text="Save", command=save_changes).grid(row=3, column=0, columnspan=2, pady=10)

    def remove_class(self):
        """
        Remove the selected class from the list of classes.
        """
        selected_item = self.class_tree.selection()
        if selected_item:
            item = selected_item[0]
            values = self.class_tree.item(item, "values")
            class_info = f"{values[0]} {values[1]} {values[2]}"
            self.classes.remove(class_info)
            self.class_tree.delete(item)

    def start_checking(self):
        """
        Start the process of checking class availability.
        """
        if self.checking:
            messagebox.showinfo("Info", "Checking is already in progress.")
            return

        try:
            self.check_interval = int(self.interval_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid interval. Please enter a number.")
            return

        if not self.classes:
            messagebox.showerror("Error", "Please add at least one class to check.")
            return

        self.checking = True
        self.disable_buttons()
        threading.Thread(target=self.check_schedule_availability, daemon=True).start()

    def check_schedule_availability(self):
        """
        Check the availability of classes in the schedule.
        This method continuously checks the availability of classes in the schedule. It iterates over each class in the schedule and calls the `check_class_availability` function to determine if the class is available. The availability status and a status message are displayed in a text widget. If a class is available, a pop-up alert is shown.
        The method uses a precise sleep method to ensure that the checking interval is maintained. It calculates the elapsed time for each iteration and determines the sleep time based on the desired check interval.
        Parameters:
        - None
        Returns:
        - None
        """
        while self.checking:
            start_time = time.time()
            
            for class_info in self.classes:
                coursePrefix, courseCode, sectionNumber = class_info.split()
                is_available, status_message = check_class_availability(coursePrefix, courseCode, sectionNumber)
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
                self.status_text.insert(tk.END, f"{timestamp}: {status_message}\n")
                self.status_text.see(tk.END)
                if is_available:
                    pop_up_alert(status_message)
            
            elapsed_time = time.time() - start_time
            sleep_time = max(0, self.check_interval - elapsed_time)
            
            # Use a more precise sleep method
            end_time = start_time + self.check_interval
            while time.time() < end_time:
                remaining = end_time - time.time()
                if remaining > 0:
                    time.sleep(min(remaining, 0.1))  # Sleep in small increments

    def stop_checking(self):
        """
        Stops the checking process.

        This method sets the 'checking' attribute to False, enabling the buttons and displaying an information message.

        Parameters:
            self (object): The instance of the class.

        Returns:
            None
        """
        self.checking = False
        self.enable_buttons()
        messagebox.showinfo("Info", "Checking has been stopped.")

    def disable_buttons(self):
        """
        Disables all buttons and entry fields in the GUI.
        """
        self.add_button.config(state="disabled")
        self.edit_button.config(state="disabled")
        self.remove_button.config(state="disabled")
        self.start_button.config(state="disabled")
        self.interval_entry.config(state="disabled")
        self.prefix_entry.config(state="disabled")
        self.number_entry.config(state="disabled")
        self.section_entry.config(state="disabled")

    def enable_buttons(self):
        """
        Enable all buttons and entry fields in the GUI.

        This method sets the state of all buttons and entry fields to "normal",
        allowing the user to interact with them.

        Parameters:
        - None

        Returns:
        - None
        """
        self.add_button.config(state="normal")
        self.edit_button.config(state="normal")
        self.remove_button.config(state="normal")
        self.start_button.config(state="normal")
        self.interval_entry.config(state="normal")
        self.prefix_entry.config(state="normal")
        self.number_entry.config(state="normal")
        self.section_entry.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClassCheckerApp(root)
    root.mainloop()

    try:
        driver.close()
        driver.quit()
    except Exception as e:
        print(f"Error closing the driver: {e}")