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
