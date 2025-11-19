"""
Example script for using AWS AppSync GraphQL API with boto3 and gql
"""

import os
import boto3
from dotenv import load_dotenv
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from requests_aws4auth import AWS4Auth

# Load environment variables from env.local file
load_dotenv('env.local')


def create_appsync_client(api_url: str = None, region: str = None):
    """
    Create an authenticated GraphQL client for AWS AppSync
    
    Args:
        api_url: Your AWS AppSync GraphQL endpoint URL (defaults to env variable)
        region: AWS region (defaults to env variable or 'us-east-1')
    
    Returns:
        GQL Client instance
    """
    # Get configuration from environment variables if not provided
    if api_url is None:
        api_url = os.getenv('APPSYNC_API_URL')
        if not api_url:
            raise ValueError("APPSYNC_API_URL must be set in env.local or passed as parameter")
    
    if region is None:
        region = os.getenv('AWS_REGION', 'us-east-1')
    
    # Get AWS profile if specified
    aws_profile = os.getenv('AWS_PROFILE')
    
    # Get AWS credentials
    session_kwargs = {}
    if aws_profile:
        session_kwargs['profile_name'] = aws_profile
    
    credentials = boto3.Session(**session_kwargs).get_credentials()
    auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        'appsync',
        session_token=credentials.token,
    )
    
    # Create transport with AWS authentication
    transport = RequestsHTTPTransport(
        url=api_url,
        auth=auth,
        use_json=True,
    )
    
    # Create GraphQL client
    client = Client(
        transport=transport,
        fetch_schema_from_transport=True,
    )
    
    return client


def example_query():
    """
    Example GraphQL query - customize this for your specific API
    """
    # Create client (uses environment variables from env.local)
    client = create_appsync_client()
    
    # Example query - customize based on your schema
    query = gql("""
        query GetCommunityRegistrations {
            listRegistrations {
                items {
                    id
                    name
                    email
                }
            }
        }
    """)
    
    # Execute query
    result = client.execute(query)
    print(result)
    
    return result


def example_mutation():
    """
    Example GraphQL mutation - customize this for your specific API
    """
    # Create client (uses environment variables from env.local)
    client = create_appsync_client()
    
    # Example mutation - customize based on your schema
    mutation = gql("""
        mutation CreateRegistration($input: CreateRegistrationInput!) {
            createRegistration(input: $input) {
                id
                name
                email
            }
        }
    """)
    
    # Variables for the mutation
    variables = {
        "input": {
            "name": "John Doe",
            "email": "john@example.com"
        }
    }
    
    # Execute mutation
    result = client.execute(mutation, variable_values=variables)
    print(result)
    
    return result


if __name__ == "__main__":
    print("AWS GraphQL Environment Setup Complete!")
    print("\nConfiguration loaded from env.local:")
    print(f"  AWS Region: {os.getenv('AWS_REGION', 'us-east-1')}")
    print(f"  AppSync API URL: {os.getenv('APPSYNC_API_URL', 'Not set - please configure in env.local')}")
    print(f"  AWS Profile: {os.getenv('AWS_PROFILE', 'default')}")
    print("\nTo use this script:")
    print("1. Update APPSYNC_API_URL in env.local with your AWS AppSync endpoint")
    print("2. Update AWS_REGION in env.local if needed")
    print("3. Customize the queries/mutations based on your GraphQL schema")
    print("4. Ensure AWS credentials are configured (via ~/.aws/credentials or env.local)")
    
    # Uncomment to run examples:
    # example_query()
    # example_mutation()

