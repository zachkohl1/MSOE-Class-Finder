# MSOE Class Availability Checker

## Description
This program checks the availability of classes at MSOE at regular intervals and displays desktop notifications to alert the user about the availability status of the classes. The user can specify the classes to check and the check interval. The script uses Selenium to interact with the class scheduling website and the plyer library to display desktop notifications.

## Dependencies
This script relies on the following Python libraries and tools:

1. **Python**: Ensure you have Python 3.6+ installed and updated.
2. **Selenium**: Install with pip install selenium (version 4.11.0 or later recommended for Selenium Manager support).
3. **win10toast**: Install with pip install win10toast for Windows-native toast notifications (Windows 10/11 only).
4. **Tkinter**: Comes bundled with Python; no separate installation required.
5. **Chrome Browser**: Selenium uses your installed Chrome browser. ChromeDriver is automatically managed by Selenium Manager, so no manual download is needed.

## Installation
`pip install selenium`
`pip install win10toast`

## Usage
1. Clone the Repository: `git clone https://github.com/zachkohl1/MSOE-Class-Finder`
2. Navigate to the directory
3. Run the program: `python3 main.py

