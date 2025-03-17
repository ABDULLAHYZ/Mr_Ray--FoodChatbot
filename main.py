from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import db_helper
import generic_helper
import logging


app = FastAPI()
inprogress_orders = {}

# Configure logging
logging.basicConfig(level=logging.DEBUG)


@app.post("/")
async def handle_request(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
        logging.debug(f"Received request: {payload}")

        intent = payload['queryResult']['intent']['displayName']
        parameters = payload['queryResult']['parameters']
        output_contexts = payload['queryResult'].get('outputContexts', [])

        if not output_contexts:
            return JSONResponse(content={"fulfillmentText": "Session not found. Please start a new order."})

        session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

        intent_handler_dict = {
            'order.add - context: ongoing-order': add_to_order,
            'order.remove - context: ongoing-order': remove_from_order,
            'track.order - context: ongoing-tracking': track_order
        }

        if intent == 'order.complete - context: ongoing-order':
            return await complete_order(parameters, session_id, background_tasks)

        if intent in intent_handler_dict:
            return intent_handler_dict[intent](parameters, session_id)

        return JSONResponse(content={"fulfillmentText": "I didn't understand that request."})

    except KeyError as e:
        logging.error(f"KeyError: {e}")
        return JSONResponse(content={"fulfillmentText": f"KeyError: {e}"})

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return JSONResponse(content={"fulfillmentText": "An unexpected error occurred. Please try again later."})


@app.get("/")
async def root():
    return {"message": "Welcome to the chatbot API!"}


# -------------------------
# Order Processing in Background
# -------------------------
def process_order(order: dict):
    save_to_db(order)  # Runs in the background


from fastapi import BackgroundTasks


async def complete_order(parameters: dict, session_id: str, background_tasks: BackgroundTasks):
    if session_id not in inprogress_orders:
        return JSONResponse(
            content={"fulfillmentText": "I'm having trouble finding your order. Please place a new order."})

    order = inprogress_orders[session_id]

    # Insert order into the database and get the order ID
    order_id = db_helper.insert_order(order)
    db_helper.insert_order_tracking(order_id, "in progress")  # Add tracking

    background_tasks.add_task(process_order, order)  # Background processing
    del inprogress_orders[session_id]

    response = {
        "fulfillmentText": f"Your order is placed successfully! Order ID: {order_id}. Tracking has started.",
        "outputContexts": [
            {
                "name": f"projects/ray-bot-faei/agent/sessions/{session_id}/contexts/ongoing-order",
                "lifespanCount": 5,
                "parameters": {
                    "order_id": order_id,
                    "food-item": list(order.keys()),
                    "quantity": list(order.values())
                }
            }
        ]
    }

    return JSONResponse(content=response)


# -------------------------
# Save Order to Database
# -------------------------
def save_to_db(order: dict):
    try:
        order_id = db_helper.get_next_order_id()  # Get a new order ID

        if order_id is None:
            return {"error": "Failed to create order!"}

        for food_item, quantity in order.items():
            item_id = db_helper.get_item_id(food_item.strip())
            if item_id is None:
                return {"error": f"Food item '{food_item}' not found!"}

            rcode = db_helper.insert_order(food_item, quantity)
            if rcode == -1:
                return {"error": f"Failed to insert {food_item} into order!"}

        # ✅ Fix: Ensure order tracking is inserted
        db_helper.insert_order_tracking(order_id, "in progress")

        return {"success": f"Order {order_id} processed!"}

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {"error": "Internal Server Error!"}


# -------------------------
# Order Management Functions
# -------------------------
def add_to_order(parameters: dict, session_id: str):
    food_items = parameters.get("food-item", [])
    quantities = parameters.get("number", [])

    if len(food_items) != len(quantities):
        return JSONResponse(content={"fulfillmentText": "Please specify food items and quantities clearly."})

    new_food_dict = dict(zip(food_items, quantities))

    if session_id in inprogress_orders:
        inprogress_orders[session_id].update(new_food_dict)
    else:
        inprogress_orders[session_id] = new_food_dict

    order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
    return JSONResponse(content={"fulfillmentText": f"So far, you have: {order_str}. Do you need anything else?"})


def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(
            content={"fulfillmentText": "I'm having trouble finding your order. Please place a new order."})

    food_items = parameters.get("food-item", [])
    current_order = inprogress_orders[session_id]

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    fulfillment_text = ""
    if removed_items:
        fulfillment_text += f"Removed {', '.join(removed_items)} from your order!"
    if no_such_items:
        fulfillment_text += f" Your current order does not contain {', '.join(no_such_items)}."
    if not current_order:
        fulfillment_text += " Your order is now empty!"
        del inprogress_orders[session_id]
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f" Here is what remains in your order: {order_str}."

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def track_order(parameters: dict, session_id: str):
    item_id = int(parameters.get('item_id', -1))

    if item_id == -1:
        return JSONResponse(content={"fulfillmentText": "Invalid item ID provided."})

    order_status = db_helper.get_order_status(item_id)
    if order_status:
        return JSONResponse(content={"fulfillmentText": f"The order status for item ID {item_id} is: {order_status}."})

    return JSONResponse(content={"fulfillmentText": f"No order found with item ID {item_id}."})
