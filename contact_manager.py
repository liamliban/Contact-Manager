import json
import re
import sys

import pymysql


class Contact:
    """Contact Class"""

    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = self.normalize_phone(phone)

    @staticmethod
    def normalize_phone(phone):
        """Normalize phone number to +1-XXX-XXX-XXXX format"""
        # Remove any non-digit characters
        digits = re.sub(r"\D", "", phone)

        # Ensure we have 10 digits (assuming US format)
        if len(digits) == 10:
            return f"+1-{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == "1":
            return f"+1-{digits[1:4]}-{digits[4:7]}-{digits[7:]}"
        else:
            # Return original if we can't normalize
            return phone


class ContactManager:
    """Class to manage contacts in MySQL database"""

    def __init__(
        self, host="localhost", user="root", password="", db_name="contact_database"
    ):
        try:
            # Connect to MySQL server
            self.connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )

            # Create database if it doesn't exist
            with self.connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")

            # Connect to the database
            self.connection.select_db(db_name)

            # Create contacts table if it doesn't exist
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS contacts (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(100) NOT NULL UNIQUE,
                        phone VARCHAR(20) NOT NULL,
                        INDEX (name)
                    )
                """
                )
                self.connection.commit()

            print("Successfully connected to MySQL database")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            sys.exit(1)

    def __del__(self):
        """Close the database connection"""
        if hasattr(self, "connection"):
            self.connection.close()

    def add_contacts_from_json(self, json_file):
        """Add contacts from JSON file"""
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
                contacts = data.get("contacts", [])

            print(f"Found {len(contacts)} contacts in JSON file")

            successful_imports = 0

            for contact_data in contacts:
                contact = Contact(
                    contact_data.get("name"),
                    contact_data.get("email"),
                    contact_data.get("phone"),
                )
                result = self.add_contact(contact)
                if result is not None:
                    successful_imports += 1

            print(f"Successfully imported {successful_imports} contacts")
            return successful_imports
        except FileNotFoundError:
            print(f"JSON file {json_file} not found")
            return 0
        except json.JSONDecodeError:
            print(f"Error parsing JSON file {json_file}")
            return 0
        except Exception as e:
            print(f"Error importing contacts: {e}")
            return 0

    def add_contact(self, contact):
        """Add a new contact to the database"""
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO contacts (name, email, phone) VALUES (%s, %s, %s)"
                cursor.execute(sql, (contact.name, contact.email, contact.phone))
                self.connection.commit()
                return cursor.lastrowid
        except pymysql.err.IntegrityError as e:
            if "Duplicate entry" in str(e):
                print(f"Contact with email {contact.email} already exists")
            else:
                print(f"Database integrity error: {e}")
            return None
        except Exception as e:
            print(f"Error adding contact: {e}")
            return None

    def get_all_contacts(self):
        """Retrieve all contacts from the database"""
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT name, email, phone FROM contacts ORDER BY name"
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving contacts: {e}")
            return []

    def find_contact(self, query_type, query_value):
        """Find a contact by name or email"""
        try:
            if query_type not in ["name", "email"]:
                print("Invalid query type. Use 'name' or 'email'")
                return None

            with self.connection.cursor() as cursor:
                sql = f"SELECT name, email, phone FROM contacts WHERE {query_type} = %s"
                cursor.execute(sql, (query_value,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error finding contact: {e}")
            return None

    def update_phone(self, query_type, query_value, new_phone):
        """Update phone number for a specific contact"""
        try:
            if query_type not in ["name", "email"]:
                print("Invalid query type. Use 'name' or 'email'")
                return False

            # Normalize the phone number
            normalized_phone = Contact.normalize_phone(new_phone)

            with self.connection.cursor() as cursor:
                sql = f"UPDATE contacts SET phone = %s WHERE {query_type} = %s"
                result = cursor.execute(sql, (normalized_phone, query_value))
                self.connection.commit()

                if result == 0:
                    print(f"No contact found with {query_type}: {query_value}")
                    return False
                return True
        except Exception as e:
            print(f"Error updating contact: {e}")
            return False

    def delete_contact(self, query_type, query_value):
        """Delete a contact by name or email"""
        try:
            if query_type not in ["name", "email"]:
                print("Invalid query type. Use 'name' or 'email'")
                return False

            with self.connection.cursor() as cursor:
                sql = f"DELETE FROM contacts WHERE {query_type} = %s"
                result = cursor.execute(sql, (query_value,))
                self.connection.commit()

                if result == 0:
                    print(f"No contact found with {query_type}: {query_value}")
                    return False
                return True
        except Exception as e:
            print(f"Error deleting contact: {e}")
            return False


# Main menu
def display_menu():
    """Display the main menu"""
    print("\n==== Contact Manager ====")
    print("1. Import contacts from JSON file")
    print("2. Add a new contact")
    print("3. Show all contacts")
    print("4. Find a contact")
    print("5. Update phone number")
    print("6. Delete a contact")
    print("7. Exit")
    return input("Enter your choice (1-7): ")


def main():
    """TO RUN MY CODE PLEASE INPUT THE CORRECT DETAILS BELOW"""
    manager = ContactManager(
        host="localhost",
        user="root",
        password="",
        db_name="contact_database",
    )

    while True:
        choice = display_menu()

        # 1. Import contact from JSON File
        if choice == "1":
            json_file = (
                input("Enter JSON file path (default: contact_list.json): ")
                or "contact_list.json"
            )
            manager.add_contacts_from_json(json_file)

        # 2. Add a new contact
        elif choice == "2":
            name = input("Enter contact name: ")
            email = input("Enter contact email: ")
            phone = input("Enter contact phone: ")

            contact = Contact(name, email, phone)
            result = manager.add_contact(contact)

            if result:
                print(f"Contact {name} added successfully")
            else:
                print("Failed to add contact")

        # 3. Show all ocntact
        elif choice == "3":
            contacts = manager.get_all_contacts()
            if contacts:
                print("\n==== All Contacts ====")
                for i, contact in enumerate(contacts, 1):
                    print(f"{i}. Name: {contact['name']}")
                    print(f"   Email: {contact['email']}")
                    print(f"   Phone: {contact['phone']}")
                    print("-------------------")
            else:
                print("No contacts found")

        # 4. Find a contact
        elif choice == "4":
            query_type = input("Search by (name/email): ").lower()
            if query_type not in ["name", "email"]:
                print("Invalid option. Please choose 'name' or 'email'")
                continue

            query_value = input(f"Enter {query_type}: ")
            contact = manager.find_contact(query_type, query_value)

            if contact:
                print("\n==== Contact Found ====")
                print(f"Name: {contact['name']}")
                print(f"Email: {contact['email']}")
                print(f"Phone: {contact['phone']}")
            else:
                print(f"No contact found with {query_type}: {query_value}")

        # 5. Update phone number
        elif choice == "5":
            query_type = input("Find contact by (name/email): ").lower()
            if query_type not in ["name", "email"]:
                print("Invalid option. Please choose 'name' or 'email'")
                continue

            query_value = input(f"Enter {query_type}: ")
            new_phone = input("Enter new phone number: ")

            success = manager.update_phone(query_type, query_value, new_phone)
            if success:
                print(f"Phone number updated successfully for {query_value}")
            else:
                print(f"Failed to update phone number")

        # 6. Delete a contact
        elif choice == "6":
            query_type = input("Delete contact by (name/email): ").lower()
            if query_type not in ["name", "email"]:
                print("Invalid option. Please choose 'name' or 'email'")
                continue

            query_value = input(f"Enter {query_type}: ")
            confirm = input(
                f"Are you sure you want to delete contact with {query_type} '{query_value}'? (y/n): "
            )

            if confirm.lower() == "y":
                success = manager.delete_contact(query_type, query_value)
                if success:
                    print(
                        f"Contact with {query_type} '{query_value}' deleted successfully"
                    )
                else:
                    print(f"Failed to delete contact")
            else:
                print("Deletion cancelled")

        # 7. Exit
        elif choice == "7":
            print("Exiting Contact Manager. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
