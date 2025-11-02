#!/usr/bin/env python3

import requests
from datetime import datetime, timedelta
import json

def send_order_reminders():
    # GraphQL endpoint
    url = "http://localhost:8000/graphql"
    
    # Calculate date 7 days ago
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # GraphQL query to get pending orders from the last 7 days
    query = """
    query GetRecentOrders {
        orders(orderDate_Gte: "%s") {
            id
            orderDate
            customer {
                email
            }
            status
        }
    }
    """ % one_week_ago
    
    try:
        # Send GraphQL request
        response = requests.post(url, json={'query': query})
        response.raise_for_status()
        
        data = response.json()
        
        if 'errors' in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        
        orders = data.get('data', {}).get('orders', [])
        
        # Log the results
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] Processing {len(orders)} recent orders\n")
            
            for order in orders:
                order_id = order.get('id')
                customer_email = order.get('customer', {}).get('email', 'N/A')
                order_date = order.get('orderDate', 'N/A')
                status = order.get('status', 'N/A')
                
                log_entry = f"[{timestamp}] Order ID: {order_id}, Customer Email: {customer_email}, Order Date: {order_date}, Status: {status}\n"
                log_file.write(log_entry)
        
        print("Order reminders processed!")
        
    except requests.exceptions.RequestException as e:
        error_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Request failed: {str(e)}\n"
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(error_msg)
        print(f"Error: {e}")
    except Exception as e:
        error_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error: {str(e)}\n"
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(error_msg)
        print(f"Error: {e}")

if __name__ == "__main__":
    send_order_reminders()
