"""
Billing and Shopping Cart Module
Handles cart management and bill generation
"""
from typing import List, Dict, Optional
from datetime import datetime
import json

class ShoppingCart:
    def __init__(self):
        """Initialize shopping cart"""
        self.items = {}  # {product_id: {details}}
        self.created_at = datetime.now()

    def add_item(self, product: Dict, quantity: int = 1) -> bool:
        """
        Add item to cart
        Args:
            product: Product dictionary with id, name, price, etc
            quantity: Quantity to add
        Returns:
            Success status
        """
        try:
            product_id = product['product_id']
            
            if product_id in self.items:
                # Increase quantity if item already exists
                self.items[product_id]['quantity'] += quantity
                print(f"✅ Updated quantity for {product['name']}")
            else:
                # Add new item
                self.items[product_id] = {
                    'product_id': product_id,
                    'name': product['name'],
                    'category': product['category'],
                    'price': product['price'],
                    'quantity': quantity,
                    'added_at': datetime.now()
                }
                print(f"✅ Added {product['name']} to cart")
            
            return True
        except Exception as e:
            print(f"❌ Error adding item: {e}")
            return False

    def remove_item(self, product_id: int) -> bool:
        """Remove item from cart"""
        try:
            if product_id in self.items:
                del self.items[product_id]
                print(f"✅ Removed product {product_id} from cart")
                return True
            return False
        except Exception as e:
            print(f"❌ Error removing item: {e}")
            return False

    def update_quantity(self, product_id: int, quantity: int) -> bool:
        """Update item quantity"""
        try:
            if product_id in self.items:
                if quantity <= 0:
                    return self.remove_item(product_id)
                self.items[product_id]['quantity'] = quantity
                print(f"✅ Updated quantity for product {product_id}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error updating quantity: {e}")
            return False

    def get_items(self) -> List[Dict]:
        """Get all items in cart"""
        return list(self.items.values())

    def get_item_count(self) -> int:
        """Get total number of unique items"""
        return len(self.items)

    def get_total_quantity(self) -> int:
        """Get total quantity of all items"""
        return sum(item['quantity'] for item in self.items.values())

    def calculate_subtotal(self) -> float:
        """Calculate subtotal"""
        subtotal = 0
        for item in self.items.values():
            subtotal += item['price'] * item['quantity']
        return round(subtotal, 2)

    def clear(self) -> bool:
        """Clear the cart"""
        try:
            self.items.clear()
            self.created_at = datetime.now()
            print("✅ Cart cleared")
            return True
        except Exception as e:
            print(f"❌ Error clearing cart: {e}")
            return False

    def is_empty(self) -> bool:
        """Check if cart is empty"""
        return len(self.items) == 0

    def to_dict(self) -> Dict:
        """Convert cart to dictionary"""
        return {
            'items': self.get_items(),
            'item_count': self.get_item_count(),
            'total_quantity': self.get_total_quantity(),
            'subtotal': self.calculate_subtotal(),
            'created_at': self.created_at.isoformat()
        }


class BillingSystem:
    def __init__(self, db_manager):
        """
        Initialize billing system
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.cart = ShoppingCart()

    def add_to_cart(self, product: Dict) -> bool:
        """Add detected product to cart"""
        return self.cart.add_item(product, quantity=1)

    def get_cart(self) -> Dict:
        """Get current cart"""
        return self.cart.to_dict()

    def calculate_bill(self, tax_rate: float = 0.0, discount: float = 0.0) -> Dict:
        """
        Calculate bill details
        Args:
            tax_rate: Tax percentage (0-1)
            discount: Flat discount amount
        Returns:
            Bill details
        """
        try:
            subtotal = self.cart.calculate_subtotal()
            tax = round(subtotal * tax_rate, 2)
            total = round(subtotal + tax - discount, 2)
            
            bill_data = {
                'items': self.cart.get_items(),
                'item_count': self.cart.get_item_count(),
                'total_quantity': self.cart.get_total_quantity(),
                'subtotal': subtotal,
                'tax': tax,
                'tax_rate': tax_rate,
                'discount': discount,
                'total': total,
                'created_at': datetime.now().isoformat()
            }
            
            return bill_data
        except Exception as e:
            print(f"❌ Error calculating bill: {e}")
            return {}

    def generate_bill(self, tax_rate: float = 0.0, discount: float = 0.0, 
                     payment_method: str = "Cash") -> Optional[int]:
        """
        Generate and save bill to database
        Args:
            tax_rate: Tax percentage
            discount: Discount amount
            payment_method: Payment method (Cash, Card, etc)
        Returns:
            Bill ID or None
        """
        try:
            if self.cart.is_empty():
                print("❌ Cannot generate bill: Cart is empty")
                return None
            
            bill_data = self.calculate_bill(tax_rate, discount)
            
            # Save to database
            bill_id = self.db_manager.create_bill(
                items=bill_data['items'],
                subtotal=bill_data['subtotal'],
                tax=bill_data['tax'],
                discount=discount,
                payment_method=payment_method
            )
            
            if bill_id:
                print(f"✅ Bill generated successfully (Bill ID: {bill_id})")
                self.cart.clear()
                return bill_id
            return None
        except Exception as e:
            print(f"❌ Error generating bill: {e}")
            return None

    def get_invoice_text(self, bill_id: int, store_name: str = "Smart Store") -> str:
        """Generate invoice text"""
        try:
            bill = self.db_manager.get_bill(bill_id)
            if not bill:
                return ""
            
            invoice = f"""
{'='*50}
{store_name.center(50)}
{'='*50}

BILL NUMBER: {bill['bill_number']}
DATE & TIME: {bill['created_at']}
PAYMENT METHOD: {bill['payment_method']}

{'-'*50}
ITEMS:
{'-'*50}
"""
            
            for item in bill['items']:
                invoice += f"""
{item['product_name']:<30}
  Qty: {item['quantity']} × ₹{item['unit_price']:.2f} = ₹{item['total_price']:.2f}
"""
            
            invoice += f"""
{'-'*50}
Subtotal:                    ₹{bill['subtotal']:.2f}
Tax:                         ₹{bill['tax']:.2f}
Discount:                    ₹{bill['discount']:.2f}
{'-'*50}
TOTAL AMOUNT:                ₹{bill['total']:.2f}
{'='*50}

Thank you for shopping!
Please visit again.

{'='*50}
"""
            return invoice
        except Exception as e:
            print(f"❌ Error generating invoice: {e}")
            return ""

    def clear_cart(self) -> bool:
        """Clear the cart"""
        return self.cart.clear()
