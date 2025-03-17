import mysql.connector

# Global connection object
global cnx

# Establish connection to the Mr_Ray database
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="Mr_Ray"
)

# Function to insert an order item into the orders table
def insert_order(food_item, quantity):
    try:
        cursor = cnx.cursor()

        # Get a new order_id
        order_id = get_next_order_id()
        if order_id is None:
            print("ERROR: Could not generate order ID!")
            return -1

        # Fetch item_id and price from database
        cursor.execute("SELECT item_id, price FROM food_items WHERE LOWER(name) = LOWER(%s)", (food_item,))
        result = cursor.fetchone()

        if not result:
            print(f"ERROR: Food item '{food_item}' not found in database!")
            return -1

        item_id, price = result
        total_price = price * quantity

        # Insert order with the correct order_id
        insert_query = "INSERT INTO orders (order_id, item_id, quantity, total_price) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (order_id, item_id, quantity, total_price))

        cnx.commit()
        cursor.close()

        print(f"Order {order_id} inserted successfully! Item: {food_item}, Quantity: {quantity}, Total: ${total_price}")
        return order_id

    except mysql.connector.Error as err:
        print(f"Error inserting order: {err}")
        cnx.rollback()
        return -1


# Function to insert a record into the order_tracking table
def insert_order_tracking(order_id, status):
    try:
        cursor = cnx.cursor()
        print(f"DEBUG: Attempting to insert tracking for Order ID {order_id} with status '{status}'")  # Debug

        insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
        cursor.execute(insert_query, (order_id, status))
        cnx.commit()
        cursor.close()

        print("✅ DEBUG: Order tracking inserted successfully!")  # Debug

    except mysql.connector.Error as err:
        print(f"❌ ERROR inserting order tracking: {err}")  # Debug error
        cnx.rollback()


# Function to get total order price from the orders table
def get_total_order_price(order_id):
    try:
        cursor = cnx.cursor()
        query = "SELECT SUM(total_price) FROM orders WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()[0]
        cursor.close()

        return result if result else 0  # Return 0 if no order is found

    except mysql.connector.Error as err:
        print(f"Error fetching total order price: {err}")
        return None


# Function to get the next available order_id from the orders table
def get_next_order_id():
    try:
        cursor = cnx.cursor()
        query = "SELECT COALESCE(MAX(order_id), 0) + 1 FROM orders"
        cursor.execute(query)
        result = cursor.fetchone()[0]
        cursor.close()
        return result
    except mysql.connector.Error as err:
        print(f"Error fetching next order ID: {err}")
        return None

# Function to fetch the order status from the order_tracking table
def get_order_status(order_id):
    try:
        cursor = cnx.cursor()
        query = "SELECT status FROM order_tracking WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    except mysql.connector.Error as err:
        print(f"Error fetching order status: {err}")
        return None

# Function to update menu items in the food_items table
def update_menu_item(food_name, price):
    try:
        cursor = cnx.cursor()
        query = "UPDATE food_items SET price = %s WHERE name = %s"
        cursor.execute(query, (price, food_name))
        cnx.commit()
        cursor.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error updating menu item: {err}")
        cnx.rollback()
        return False

def get_next_item_id():
    try:
        cursor = cnx.cursor()
        query = "SELECT IFNULL(MAX(item_id), 0) + 1 FROM food_items"
        cursor.execute(query)
        result = cursor.fetchone()[0]
        cursor.close()
        return result
    except mysql.connector.Error as err:
        print(f"Error fetching next item ID: {err}")
        return None

def get_item_id(food_item):
    try:
        cursor = cnx.cursor()
        query = "SELECT item_id FROM food_items WHERE LOWER(name) = LOWER(%s)"
        cursor.execute(query, (food_item,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            print(f"DEBUG: Found item_id for {food_item} -> {result[0]}")
            return result[0]
        else:
            print(f"ERROR: No item_id found for {food_item} in food_items table!")
            return None

    except mysql.connector.Error as err:
        print(f"Error fetching item_id: {err}")
        return None



if __name__ == "__main__":
    print(f"Next available order ID: {get_next_order_id()}")

