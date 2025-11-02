from datetime import datetime
import requests
import json

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
        
        # Optional: Verify GraphQL endpoint is responsive
        try:
            # Query the GraphQL hello field to verify endpoint responsiveness
            url = "http://localhost:8000/graphql"
            query = {
                "query": "query { hello }"
            }
            
            response = requests.post(url, json=query, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'hello' in data['data']:
                    with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
                        log_file.write(f"{timestamp} GraphQL endpoint is responsive: {data['data']['hello']}\n")
                else:
                    with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
                        log_file.write(f"{timestamp} GraphQL endpoint responded with errors\n")
            else:
                with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
                    log_file.write(f"{timestamp} GraphQL endpoint returned status code: {response.status_code}\n")
                    
        except requests.exceptions.RequestException as e:
            with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
                log_file.write(f"{timestamp} GraphQL endpoint check failed: {str(e)}\n")
        
    except Exception as e:
        # If file writing fails, this will be visible in cron logs
        print(f"Heartbeat logging failed: {e}")
