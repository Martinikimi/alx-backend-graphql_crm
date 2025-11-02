#!/usr/bin/env python3

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta

def send_order_reminders():
    # GraphQL transport
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )
    
    # Create GraphQL client
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # Calculate date 7 days ago
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # GraphQL query to get pending orders from the last 7 days
    query = gql("""
    query GetRecentOrders($orderDateGte: String!) {
        orders(orderDate_Gte: $orderDateGte) {
            id
            orderDate
            customer {
                email
            }
            status
        }
    }
    """)
    
    try:
        # Execute GraphQL query with variables
        variables = {"orderDateGte": one_week_ago}
        result = client.execute(query, variable_values=variables)
        
        orders = result.get('orders', [])
        
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
        
    except Exception as e:
        error_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error: {str(e)}\n"
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(error_msg)
        print(f"Error: {e}")

if __name__ == "__main__":
    send_order_reminders()
