## Contact-Manager
Implement a program using Python to store and manage a simple contact list in a MongoDB or MySQL Database. The program should get contact information from a given JSON file and then allow the user to perform various operations on the data.

## Project Overview
This implementation provides a complete contact management system with:
- Database storage (MySQL)
- JSON import functionality
- Contact CRUD operations
- Phone number normalization
- Error handling and validation

## Prerequisites
Before running the application, ensure you have:
1. Python 3.x installed
2. MySQL Server running on your system
3. MySQL user credentials ready

## Installation
1. Install required Python packages:
```
brew install mysql
pip install pymysql
```
2. Configure MySQL:
   - Start MySQL server
   - Create a user account (recommended: not root)
   - Grant appropriate permissions

## Configuration
Edit the database connection parameters in the code:
```
manager = ContactManager(
    host="localhost",
    user="your_username",
    password="your_password",
    db_name="contact_database"
)
```
Replace the placeholder values with your actual MySQL credentials.

## Usage
1. Save the code in a file (e.g., `contact_manager.py`)
2. Run the program:
```
python contact_manager.py
```
3. Use the interactive menu to:
   - Import contacts from JSON
   - Add new contacts
   - View all contacts
   - Search contacts
   - Update phone numbers
   - Delete contacts
