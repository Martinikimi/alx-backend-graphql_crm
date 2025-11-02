from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """
    Cron job function that logs a heartbeat message every 5 minutes
    to confirm the CRM application's health.
    """
    try:
        # Format: DD/MM/YYYY-HH:MM:SS
        timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
        message = f"{timestamp} CRM is alive"
        
        # Log to file (append mode)
        with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
            log_file.write(message + '\n')
        
        # Optional: Verify GraphQL endpoint is responsive using gql
        try:
            # Set up GraphQL transport and client
            transport = RequestsHTTPTransport(
                url="http://localhost:8000/graphql",
                verify=True,
                retries=3,
            )
            
            client = Client(transport=transport, fetch_schema_from_transport=True)
            
            # Query the GraphQL hello field to verify endpoint responsiveness
            query = gql("""
                query {
                    hello
                }
            """)
            
            result = client.execute(query)
            
            if 'hello' in result:
                with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
                    log_file.write(f"{timestamp} GraphQL endpoint is responsive: {result['hello']}\n")
            else:
                with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
                    log_file.write(f"{timestamp} GraphQL endpoint responded without hello field\n")
                    
        except Exception as e:
            with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
                log_file.write(f"{timestamp} GraphQL endpoint check failed: {str(e)}\n")
        
    except Exception as e:
        # If file writing fails, this will be visible in cron logs
        print(f"Heartbeat logging failed: {e}")

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime

def update_low_stock():
    """
    Cron job function that runs every 12 hours to update low-stock products
    """
    try:
        # Set up GraphQL transport and client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # GraphQL mutation to update low-stock products
        mutation = gql("""
            mutation UpdateLowStockProducts {
                updateLowStockProducts {
                    success
                    message
                    updatedProducts {
                        id
                        name
                        stock
                    }
                }
            }
        """)
        
        # Execute the mutation
        result = client.execute(mutation)
        
        mutation_result = result.get('updateLowStockProducts', {})
        
        # Log the results
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            if mutation_result.get('success'):
                updated_products = mutation_result.get('updatedProducts', [])
                log_file.write(f"[{timestamp}] {mutation_result.get('message')}\n")
                log_file.write(f"[{timestamp}] Updated {len(updated_products)} products:\n")
                
                for product in updated_products:
                    product_name = product.get('name', 'Unknown')
                    new_stock = product.get('stock', 0)
                    log_file.write(f"[{timestamp}] - {product_name}: New stock level: {new_stock}\n")
            else:
                log_file.write(f"[{timestamp}] Failed: {mutation_result.get('message')}\n")
        
        print("Low stock update completed!")
        
    except Exception as e:
        error_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error in low stock update: {str(e)}\n"
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            log_file.write(error_msg)
        print(f"Error: {e}")
