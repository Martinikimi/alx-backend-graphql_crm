from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime

@shared_task
def generate_crm_report():
    """
    Celery task to generate weekly CRM report using GraphQL queries
    """
    try:
        # Set up GraphQL transport and client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # GraphQL query to fetch CRM statistics
        query = gql("""
            query GetCRMStatistics {
                customers {
                    totalCount
                }
                orders {
                    totalCount
                    totalRevenue
                }
            }
        """)
        
        # Execute the query
        result = client.execute(query)
        
        # Extract data from result
        customers_count = result.get('customers', {}).get('totalCount', 0)
        orders_count = result.get('orders', {}).get('totalCount', 0)
        total_revenue = result.get('orders', {}).get('totalRevenue', 0)
        
        # Format the report
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_message = f"{timestamp} - Report: {customers_count} customers, {orders_count} orders, {total_revenue} revenue"
        
        # Log the report
        with open('/tmp/crm_report_log.txt', 'a') as log_file:
            log_file.write(report_message + '\n')
        
        return f"Report generated: {customers_count} customers, {orders_count} orders, {total_revenue} revenue"
        
    except Exception as e:
        error_msg = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Report generation failed: {str(e)}"
        with open('/tmp/crm_report_log.txt', 'a') as log_file:
            log_file.write(error_msg + '\n')
        return f"Error: {str(e)}"


from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
import requests

@shared_task
def generate_crm_report():
    """
    Celery task to generate weekly CRM report using GraphQL queries
    """
    try:
        # Set up GraphQL transport and client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # GraphQL query to fetch CRM statistics
        query = gql("""
            query GetCRMStatistics {
                customers {
                    totalCount
                }
                orders {
                    totalCount
                    totalRevenue
                }
            }
        """)
        
        # Execute the query
        result = client.execute(query)
        
        # Extract data from result
        customers_count = result.get('customers', {}).get('totalCount', 0)
        orders_count = result.get('orders', {}).get('totalCount', 0)
        total_revenue = result.get('orders', {}).get('totalRevenue', 0)
        
        # Format the report
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_message = f"{timestamp} - Report: {customers_count} customers, {orders_count} orders, {total_revenue} revenue"
        
        # Log the report
        with open('/tmp/crm_report_log.txt', 'a') as log_file:
            log_file.write(report_message + '\n')
        
        return f"Report generated: {customers_count} customers, {orders_count} orders, {total_revenue} revenue"
        
    except Exception as e:
        error_msg = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Report generation failed: {str(e)}"
        with open('/tmp/crm_report_log.txt', 'a') as log_file:
            log_file.write(error_msg + '\n')
        return f"Error: {str(e)}"
