"""
Furniture Stock Management Application (CLI)

This application allows managing furniture stock with features:
- Add new stock items
- Allocate (reduce) quantity from existing stock items
- Generate simple stock reports
- Data is persisted locally to a JSON file between runs

Run the script and follow the menu prompts to interact with the app.

Author: Raymond Tawiah Amegah
Date: 2024
"""

import json
import os
import sys
from typing import List, Dict, Optional

STORAGE_FILENAME = "furniture_stock_data.json"

class StockManager:
    """
    Manages the furniture stock items, including persistence to a file.

    Attributes:
        stock_items (List[Dict]): List of stock items, each with 'id' (int), 'name' (str), and 'quantity' (int).
    """
    def __init__(self, storage_file: str = STORAGE_FILENAME):
        """
        Initializes the StockManager and loads data from storage file if exists.

        Args:
            storage_file (str): Path to JSON file used for persistent storage.
        """
        self.storage_file = storage_file
        self.stock_items: List[Dict] = []
        self.load_stock()

    def load_stock(self):
        """Load stock data from the JSON storage file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Validate data structure
                    if isinstance(data, list):
                        self.stock_items = data
                    else:
                        print("Warning: Invalid data format in storage file. Starting with empty stock.")
                        self.stock_items = []
            except (json.JSONDecodeError, IOError):
                print("Warning: Failed to read storage file. Starting with empty stock.")
                self.stock_items = []
        else:
            self.stock_items = []

    def save_stock(self):
        """Save current stock data to the JSON storage file."""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.stock_items, f, indent=2)
        except IOError as e:
            print(f"Error: Failed to save stock data - {e}")

    def _generate_next_id(self) -> int:
        """Generate the next unique integer ID for a new stock item."""
        if not self.stock_items:
            return 1
        max_id = max(item['id'] for item in self.stock_items)
        return max_id + 1

    def add_stock(self, name: str, quantity: int):
        """
        Add new stock item or increase quantity if item already exists.

        Args:
            name (str): Furniture item name.
            quantity (int): Quantity to add (must be positive).
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        # Check if item already exists (case insensitive)
        for item in self.stock_items:
            if item['name'].lower() == name.lower():
                item['quantity'] += quantity
                print(f"Updated existing item '{item['name']}' quantity to {item['quantity']}.")
                self.save_stock()
                return
        # Add new item
        new_item = {
            'id': self._generate_next_id(),
            'name': name,
            'quantity': quantity
        }
        self.stock_items.append(new_item)
        print(f"Added new item '{name}' with quantity {quantity}.")
        self.save_stock()

    def allocate_stock(self, item_id: int, quantity: int) -> bool:
        """
        Allocate (reduce) stock quantity from an existing item.

        Args:
            item_id (int): ID of the stock item to allocate from.
            quantity (int): Quantity to allocate (must be positive).

        Returns:
            bool: True if allocation successful, False if insufficient stock or item not found.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        for item in self.stock_items:
            if item['id'] == item_id:
                if item['quantity'] >= quantity:
                    item['quantity'] -= quantity
                    print(f"Allocated {quantity} units from '{item['name']}'. Remaining: {item['quantity']}")
                    self.save_stock()
                    return True
                else:
                    print(f"Error: Insufficient stock. '{item['name']}' has only {item['quantity']} units.")
                    return False
        print(f"Error: Item with ID {item_id} not found.")
        return False

    def get_report(self) -> Dict[str, any]:
        """
        Generate a summary report of the stock.

        Returns:
            Dict[str, any]: Report containing the total distinct items, total quantity, and list of items.
        """
        total_distinct = len(self.stock_items)
        total_quantity = sum(item['quantity'] for item in self.stock_items)
        items_copy = [item.copy() for item in self.stock_items]  # shallow copy for safety
        return {
            'total_distinct_items': total_distinct,
            'total_quantity': total_quantity,
            'items': items_copy
        }

    def find_item_by_id(self, item_id: int) -> Optional[Dict]:
        """
        Find a stock item by its ID.

        Args:
            item_id (int): ID of the item.

        Returns:
            Dict or None: The stock item dictionary if found, else None.
        """
        for item in self.stock_items:
            if item['id'] == item_id:
                return item
        return None


def clear_console():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    """Pause execution until user presses Enter."""
    input("\nPress Enter to continue...")

def main():
    """Main command-line interface loop."""
    manager = StockManager()

    while True:
        clear_console()
        print("=== Furniture Stock Management ===\n")
        print("Select an option:")
        print("1. Add New Stock")
        print("2. Allocate Stock")
        print("3. View Reports")
        print("4. View All Stock Items")
        print("5. Exit\n")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            clear_console()
            print("--- Add New Stock ---")
            name = input("Enter furniture name: ").strip()
            if not name:
                print("Error: Name cannot be empty.")
                pause()
                continue
            quantity_str = input("Enter quantity to add: ").strip()
            if not quantity_str.isdigit():
                print("Error: Quantity must be a positive integer.")
                pause()
                continue
            quantity = int(quantity_str)
            try:
                manager.add_stock(name, quantity)
            except ValueError as e:
                print(f"Error: {e}")
            pause()

        elif choice == '2':
            clear_console()
            print("--- Allocate Stock ---")
            if not manager.stock_items:
                print("No stock items available to allocate.")
                pause()
                continue
            
            print("Available stock items:")
            for item in manager.stock_items:
                print(f"ID: {item['id']} | Name: {item['name']} | Quantity: {item['quantity']}")
            id_str = input("Enter the ID of the item to allocate from: ").strip()
            if not id_str.isdigit():
                print("Error: ID must be a positive integer.")
                pause()
                continue
            item_id = int(id_str)
            quantity_str = input("Enter quantity to allocate: ").strip()
            if not quantity_str.isdigit():
                print("Error: Quantity must be a positive integer.")
                pause()
                continue
            quantity = int(quantity_str)

            try:
                success = manager.allocate_stock(item_id, quantity)
                if not success:
                    print("Allocation failed.")
            except ValueError as e:
                print(f"Error: {e}")
            pause()

        elif choice == '3':
            clear_console()
            print("--- Stock Report ---")
            report = manager.get_report()
            print(f"Total distinct items: {report['total_distinct_items']}")
            print(f"Total quantity in stock: {report['total_quantity']}")
            print("\nDetailed Stock Items:")
            for item in report['items']:
                print(f"ID: {item['id']} | Name: {item['name']} | Quantity: {item['quantity']}")
            pause()

        elif choice == '4':
            clear_console()
            print("--- All Stock Items ---")
            if not manager.stock_items:
                print("No stock items found.")
            else:
                for item in manager.stock_items:
                    print(f"ID: {item['id']} | Name: {item['name']} | Quantity: {item['quantity']}")
            pause()

        elif choice == '5':
            print("Exiting application. Goodbye!")
            sys.exit(0)

        else:
            print("Invalid choice. Please enter a number between 1 and 5.")
            pause()


if __name__ == "__main__":
    main()
