import sys
import random
from datetime import datetime, timedelta
from db_utils import execute_query
from create_test_order import create_test_order
from decimal import Decimal

def simulate_complete_delivery():
    print("Simulating a complete delivery...")

    try:
        # Step 1: Create a test order
        print("Creating test order...")
        order_id, order_number = create_test_order()
        
        if not order_id:
            print("Failed to create order. Aborting.")
            return
            
        # Step 2: Get a random delivery person
        delivery_personnel = execute_query("SELECT delivery_person_id, name FROM delivery_personnel")
        if not delivery_personnel:
            print("No delivery personnel found in database.")
            return
            
        delivery_person = random.choice(delivery_personnel)
        delivery_person_id = delivery_person['delivery_person_id']
        delivery_person_name = delivery_person['name']
        
        print(f"Selected delivery person: {delivery_person_name} (ID: {delivery_person_id})")
        
        # Step 3: Assign the order to delivery person and update status
        assign_query = """
        UPDATE orders 
        SET delivery_status = 'On Delivery', 
            delivery_person_id = %s,
            assigned_time = NOW()
        WHERE order_id = %s
        """
        result = execute_query(assign_query, (delivery_person_id, order_id), fetch=False)
        
        if result is None:
            print("Failed to assign delivery person to order.")
            return
            
        print(f"Order #{order_number} assigned to {delivery_person_name}")
        
        # Step 4: Mark the order as delivered with actual delivery time
        print("Marking order as delivered...")
        # Create delivery time 30-60 min after order time
        actual_delivery_time = datetime.now() + timedelta(minutes=random.randint(30, 60))
        
        complete_query = """
        UPDATE orders 
        SET delivery_status = 'Delivered',
            actual_delivery_time = %s,
            payment_status = 'Paid'
        WHERE order_id = %s
        """
        result = execute_query(complete_query, (actual_delivery_time, order_id), fetch=False)
        
        if result is None:
            print("Failed to mark order as delivered.")
            return
            
        print(f"Order #{order_number} marked as delivered at {actual_delivery_time}")
        print("Delivery simulation completed successfully!")
        
        # Step 5: Add a rating for the order
        rating_query = """
        INSERT INTO ratings (
            customer_id, order_id, restaurant_id, delivery_person_id,
            food_rating, delivery_rating, comment, rating_date
        ) 
        SELECT 
            o.customer_id, 
            o.order_id, 
            o.restaurant_id, 
            o.delivery_person_id,
            %s, %s, %s, NOW()
        FROM orders o
        WHERE o.order_id = %s
        """
        
        food_rating = random.randint(3, 5)
        delivery_rating = random.randint(3, 5)
        comments = [
            "Great food and quick delivery!",
            "Food was delicious, delivery was on time.",
            "Excellent service, will order again.",
            "Good experience overall.",
            "Food was hot and delivery person was friendly."
        ]
        
        rating_params = (food_rating, delivery_rating, random.choice(comments), order_id)
        execute_query(rating_query, rating_params, fetch=False)
        
        print(f"Added ratings: Food: {food_rating}/5, Delivery: {delivery_rating}/5")
        print("\nOrder details for verification:")
        
        # Get complete order details
        order_details = execute_query("""
            SELECT o.*, r.name as restaurant_name, c.name as customer_name, d.name as delivery_person_name
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.restaurant_id
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN delivery_personnel d ON o.delivery_person_id = d.delivery_person_id
            WHERE o.order_id = %s
        """, (order_id,))
        
        if order_details:
            o = order_details[0]
            print(f"Order ID: {o['order_id']}")
            print(f"Order Number: {o['order_number']}")
            print(f"Restaurant: {o['restaurant_name']}")
            print(f"Customer: {o['customer_name']}")
            print(f"Delivery Person: {o['delivery_person_name']}")
            print(f"Status: {o['delivery_status']}")
            print(f"Order Time: {o['order_time']}")
            print(f"Actual Delivery Time: {o['actual_delivery_time']}")
            print(f"Total Amount: {float(o['total_amount']):.2f} AED")
        
        return order_id
        
    except Exception as e:
        print(f"Error simulating delivery: {e}")
        return None

if __name__ == "__main__":
    simulate_complete_delivery() 