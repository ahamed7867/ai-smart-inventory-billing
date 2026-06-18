"""
Database Manager for AI Smart Inventory System
Handles all SQLite database operations
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import json

class DatabaseManager:
    def __init__(self, db_path: str = "database/inventory.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.initialize_database()

    def connect(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()
            print(f"✅ Connected to database: {self.db_path}")
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            raise

    def initialize_database(self):
        """Create all required tables"""
        try:
            # Products Table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL,
                    image_path TEXT,
                    class_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Inventory Log Table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    previous_stock INTEGER,
                    new_stock INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                )
            ''')

            # Bills Table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS bills (
                    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_number TEXT UNIQUE NOT NULL,
                    subtotal REAL NOT NULL,
                    tax REAL NOT NULL,
                    discount REAL NOT NULL,
                    total REAL NOT NULL,
                    items_count INTEGER NOT NULL,
                    payment_method TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Bill Items Table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS bill_items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    total_price REAL NOT NULL,
                    FOREIGN KEY (bill_id) REFERENCES bills(bill_id),
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                )
            ''')

            # Admin Users Table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')

            # Sales Analytics Table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales_analytics (
                    analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    total_sold INTEGER NOT NULL,
                    total_revenue REAL NOT NULL,
                    date DATE NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products(product_id),
                    UNIQUE(product_id, date)
                )
            ''')

            self.conn.commit()
            print("✅ Database tables initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            raise

    # ==================== PRODUCT OPERATIONS ====================

    def add_product(self, name: str, category: str, price: float, stock: int, 
                   class_name: str, image_path: str = None) -> int:
        """Add a new product to the database"""
        try:
            self.cursor.execute('''
                INSERT INTO products (name, category, price, stock, class_name, image_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, category, price, stock, class_name, image_path))
            self.conn.commit()
            product_id = self.cursor.lastrowid
            print(f"✅ Product added: {name} (ID: {product_id})")
            return product_id
        except sqlite3.IntegrityError:
            print(f"❌ Product '{name}' already exists")
            return None
        except Exception as e:
            print(f"❌ Error adding product: {e}")
            return None

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get product details by ID"""
        try:
            self.cursor.execute('''
                SELECT * FROM products WHERE product_id = ?
            ''', (product_id,))
            row = self.cursor.fetchone()
            if row:
                return {
                    'product_id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'price': row[3],
                    'stock': row[4],
                    'image_path': row[5],
                    'class_name': row[6]
                }
            return None
        except Exception as e:
            print(f"❌ Error fetching product: {e}")
            return None

    def get_product_by_name(self, name: str) -> Optional[Dict]:
        """Get product details by name"""
        try:
            self.cursor.execute('''
                SELECT * FROM products WHERE name = ?
            ''', (name,))
            row = self.cursor.fetchone()
            if row:
                return {
                    'product_id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'price': row[3],
                    'stock': row[4],
                    'image_path': row[5],
                    'class_name': row[6]
                }
            return None
        except Exception as e:
            print(f"❌ Error fetching product: {e}")
            return None

    def get_product_by_class(self, class_name: str) -> Optional[Dict]:
        """Get product by YOLO class name"""
        try:
            self.cursor.execute('''
                SELECT * FROM products WHERE class_name = ?
            ''', (class_name,))
            row = self.cursor.fetchone()
            if row:
                return {
                    'product_id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'price': row[3],
                    'stock': row[4],
                    'image_path': row[5],
                    'class_name': row[6]
                }
            return None
        except Exception as e:
            print(f"❌ Error fetching product by class: {e}")
            return None

    def get_all_products(self) -> List[Dict]:
        """Get all products"""
        try:
            self.cursor.execute('SELECT * FROM products')
            rows = self.cursor.fetchall()
            products = []
            for row in rows:
                products.append({
                    'product_id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'price': row[3],
                    'stock': row[4],
                    'image_path': row[5],
                    'class_name': row[6]
                })
            return products
        except Exception as e:
            print(f"❌ Error fetching all products: {e}")
            return []

    def update_product(self, product_id: int, **kwargs) -> bool:
        """Update product details"""
        try:
            allowed_fields = ['name', 'category', 'price', 'stock', 'image_path', 'class_name']
            updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not updates:
                return False

            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [product_id]

            self.cursor.execute(f'''
                UPDATE products SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
                WHERE product_id = ?
            ''', values)
            self.conn.commit()
            print(f"✅ Product {product_id} updated")
            return True
        except Exception as e:
            print(f"❌ Error updating product: {e}")
            return False

    def update_stock(self, product_id: int, quantity: int, action: str = "sale") -> bool:
        """Update product stock and log the action"""
        try:
            product = self.get_product_by_id(product_id)
            if not product:
                print(f"❌ Product not found")
                return False

            previous_stock = product['stock']
            new_stock = previous_stock - quantity

            if action == "sale" and new_stock < 0:
                print(f"❌ Insufficient stock for product {product_id}")
                return False

            # Update stock
            self.cursor.execute('''
                UPDATE products SET stock = ? WHERE product_id = ?
            ''', (new_stock, product_id))

            # Log the action
            self.cursor.execute('''
                INSERT INTO inventory_log (product_id, action, quantity, previous_stock, new_stock)
                VALUES (?, ?, ?, ?, ?)
            ''', (product_id, action, quantity, previous_stock, new_stock))

            self.conn.commit()
            print(f"✅ Stock updated for product {product_id}: {previous_stock} → {new_stock}")
            return True
        except Exception as e:
            print(f"❌ Error updating stock: {e}")
            return False

    def delete_product(self, product_id: int) -> bool:
        """Delete product"""
        try:
            self.cursor.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
            self.conn.commit()
            print(f"✅ Product {product_id} deleted")
            return True
        except Exception as e:
            print(f"❌ Error deleting product: {e}")
            return False

    def get_low_stock_products(self, threshold: int = 5) -> List[Dict]:
        """Get products with low stock"""
        try:
            self.cursor.execute('''
                SELECT * FROM products WHERE stock <= ?
            ''', (threshold,))
            rows = self.cursor.fetchall()
            products = []
            for row in rows:
                products.append({
                    'product_id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'price': row[3],
                    'stock': row[4],
                    'image_path': row[5],
                    'class_name': row[6]
                })
            return products
        except Exception as e:
            print(f"❌ Error fetching low stock products: {e}")
            return []

    # ==================== BILLING OPERATIONS ====================

    def create_bill(self, items: List[Dict], subtotal: float, tax: float, 
                   discount: float, payment_method: str = "Cash") -> Optional[int]:
        """Create a new bill"""
        try:
            total = subtotal + tax - discount
            bill_number = f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            self.cursor.execute('''
                INSERT INTO bills (bill_number, subtotal, tax, discount, total, items_count, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (bill_number, subtotal, tax, discount, total, len(items), payment_method))

            bill_id = self.cursor.lastrowid

            # Add bill items
            for item in items:
                self.cursor.execute('''
                    INSERT INTO bill_items (bill_id, product_id, quantity, unit_price, total_price)
                    VALUES (?, ?, ?, ?, ?)
                ''', (bill_id, item['product_id'], item['quantity'], item['unit_price'], item['total_price']))

                # Update product stock
                self.update_stock(item['product_id'], item['quantity'], action='sale')

            self.conn.commit()
            print(f"✅ Bill created: {bill_number} (ID: {bill_id})")
            return bill_id
        except Exception as e:
            print(f"❌ Error creating bill: {e}")
            self.conn.rollback()
            return None

    def get_bill(self, bill_id: int) -> Optional[Dict]:
        """Get bill details"""
        try:
            self.cursor.execute('''
                SELECT * FROM bills WHERE bill_id = ?
            ''', (bill_id,))
            row = self.cursor.fetchone()
            if row:
                bill_data = {
                    'bill_id': row[0],
                    'bill_number': row[1],
                    'subtotal': row[2],
                    'tax': row[3],
                    'discount': row[4],
                    'total': row[5],
                    'items_count': row[6],
                    'payment_method': row[7],
                    'created_at': row[8]
                }

                # Get bill items
                self.cursor.execute('''
                    SELECT bi.*, p.name FROM bill_items bi 
                    JOIN products p ON bi.product_id = p.product_id 
                    WHERE bi.bill_id = ?
                ''', (bill_id,))
                items = self.cursor.fetchall()
                bill_data['items'] = [
                    {
                        'item_id': item[0],
                        'product_id': item[2],
                        'quantity': item[3],
                        'unit_price': item[4],
                        'total_price': item[5],
                        'product_name': item[6]
                    }
                    for item in items
                ]
                return bill_data
            return None
        except Exception as e:
            print(f"❌ Error fetching bill: {e}")
            return None

    def get_all_bills(self, limit: int = 100) -> List[Dict]:
        """Get all bills"""
        try:
            self.cursor.execute('''
                SELECT * FROM bills ORDER BY created_at DESC LIMIT ?
            ''', (limit,))
            rows = self.cursor.fetchall()
            bills = []
            for row in rows:
                bills.append({
                    'bill_id': row[0],
                    'bill_number': row[1],
                    'subtotal': row[2],
                    'tax': row[3],
                    'discount': row[4],
                    'total': row[5],
                    'items_count': row[6],
                    'payment_method': row[7],
                    'created_at': row[8]
                })
            return bills
        except Exception as e:
            print(f"❌ Error fetching bills: {e}")
            return []

    def get_sales_by_date(self, date_str: str) -> List[Dict]:
        """Get all sales from a specific date"""
        try:
            self.cursor.execute('''
                SELECT * FROM bills WHERE DATE(created_at) = ? ORDER BY created_at DESC
            ''', (date_str,))
            rows = self.cursor.fetchall()
            bills = []
            for row in rows:
                bills.append({
                    'bill_id': row[0],
                    'bill_number': row[1],
                    'subtotal': row[2],
                    'tax': row[3],
                    'discount': row[4],
                    'total': row[5],
                    'items_count': row[6],
                    'payment_method': row[7],
                    'created_at': row[8]
                })
            return bills
        except Exception as e:
            print(f"❌ Error fetching sales: {e}")
            return []

    # ==================== ANALYTICS OPERATIONS ====================

    def update_sales_analytics(self, product_id: int, quantity: int, revenue: float, date: str):
        """Update sales analytics"""
        try:
            self.cursor.execute('''
                INSERT INTO sales_analytics (product_id, total_sold, total_revenue, date)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(product_id, date) DO UPDATE SET
                total_sold = total_sold + ?,
                total_revenue = total_revenue + ?
            ''', (product_id, quantity, revenue, date, quantity, revenue))
            self.conn.commit()
        except Exception as e:
            print(f"❌ Error updating analytics: {e}")

    def get_sales_analytics(self, date: str = None) -> List[Dict]:
        """Get sales analytics"""
        try:
            if date:
                self.cursor.execute('''
                    SELECT sa.*, p.name FROM sales_analytics sa
                    JOIN products p ON sa.product_id = p.product_id
                    WHERE sa.date = ?
                ''', (date,))
            else:
                self.cursor.execute('''
                    SELECT sa.*, p.name FROM sales_analytics sa
                    JOIN products p ON sa.product_id = p.product_id
                    ORDER BY sa.date DESC
                ''')
            rows = self.cursor.fetchall()
            analytics = []
            for row in rows:
                analytics.append({
                    'analytics_id': row[0],
                    'product_id': row[1],
                    'total_sold': row[2],
                    'total_revenue': row[3],
                    'date': row[4],
                    'product_name': row[5]
                })
            return analytics
        except Exception as e:
            print(f"❌ Error fetching analytics: {e}")
            return []

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✅ Database connection closed")

    def __del__(self):
        """Destructor to close connection"""
        self.close()
