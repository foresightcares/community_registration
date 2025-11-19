"""
Process Community Registration Excel file and create communities and caretakers via GraphQL
"""

import os
import openpyxl
from dotenv import load_dotenv
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from requests_aws4auth import AWS4Auth
import boto3
from typing import Dict, List, Optional

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


def read_community_data(file_path: str) -> List[Dict]:
    """
    Read community data from Excel file
    
    Args:
        file_path: Path to the Excel file
    
    Returns:
        List of community data dictionaries
    """
    wb = openpyxl.load_workbook(file_path)
    ws = wb['Community Info']
    
    communities = []
    headers = [cell.value for cell in ws[1]]
    
    # Map Excel column names to GraphQL input field names
    field_mapping = {
        'Name': 'name',
        'Contact Phone Number': 'phoneNumber',
        'Contact Email': 'email',
        'Street': 'street',
        'City': 'city',
        'State': 'state',
        'Country': 'country',
        'Zip Code': 'postalCode',
        'No. Resident': 'residentLimit',
        'No. Users': 'caretakerLimit',
    }
    
    for row in ws.iter_rows(min_row=2, values_only=True):
        # Skip empty rows
        if not any(row):
            continue
        
        community = {}
        for idx, header in enumerate(headers):
            if header in field_mapping and row[idx] is not None:
                field_name = field_mapping[header]
                value = row[idx]
                
                # Convert numeric fields to int
                if field_name in ['residentLimit', 'caretakerLimit']:
                    value = int(value)
                
                community[field_name] = value
        
        # Only add if required fields are present
        if community.get('name') and community.get('phoneNumber') and community.get('email'):
            # Set defaults for required fields if not provided
            if 'residentLimit' not in community:
                community['residentLimit'] = 100
            if 'caretakerLimit' not in community:
                community['caretakerLimit'] = 10
            
            communities.append(community)
    
    return communities


def read_caretaker_data(file_path: str) -> List[Dict]:
    """
    Read caretaker data from Excel file
    
    Args:
        file_path: Path to the Excel file
    
    Returns:
        List of caretaker data dictionaries
    """
    wb = openpyxl.load_workbook(file_path)
    ws = wb['Users']
    
    caretakers = []
    headers = [cell.value for cell in ws[1]]
    
    # Map Excel column names to GraphQL input field names
    field_mapping = {
        'First Name': 'firstName',
        'Last Name': 'lastName',
        'Email': 'email',
        'CommunityId': 'communityId',
    }
    
    for row in ws.iter_rows(min_row=2, values_only=True):
        # Skip empty rows
        if not any(row):
            continue
        
        caretaker = {}
        for idx, header in enumerate(headers):
            if header in field_mapping and row[idx] is not None:
                field_name = field_mapping[header]
                caretaker[field_name] = row[idx]
        
        # Only add if required fields are present
        if (caretaker.get('firstName') and 
            caretaker.get('lastName') and 
            caretaker.get('email')):
            caretakers.append(caretaker)
    
    return caretakers


def create_community(client: Client, community_data: Dict) -> Optional[Dict]:
    """
    Create a community using GraphQL mutation
    
    Args:
        client: GraphQL client
        community_data: Community data dictionary
    
    Returns:
        Created community data or None if failed
    """
    mutation = gql("""
        mutation CreateCommunity($input: CreateCommunityInput!) {
            createCommunity(input: $input) {
                id
                name
                street
                city
                state
                country
                postalCode
                phoneNumber
                email
                residentLimit
                caretakerLimit
                isActive
                createdAt
                updatedAt
            }
        }
    """)
    
    try:
        result = client.execute(mutation, variable_values={'input': community_data})
        return result['createCommunity']
    except Exception as e:
        print(f"Error creating community '{community_data.get('name')}': {str(e)}")
        return None


def create_caretaker(client: Client, caretaker_data: Dict, use_community_caretaker: bool = False) -> Optional[Dict]:
    """
    Create a caretaker using GraphQL mutation
    
    Args:
        client: GraphQL client
        caretaker_data: Caretaker data dictionary
        use_community_caretaker: If True, use createCommunityCaretaker mutation
    
    Returns:
        Created caretaker data or None if failed
    """
    mutation_name = 'createCommunityCaretaker' if use_community_caretaker else 'createCaretaker'
    
    mutation = gql(f"""
        mutation CreateCaretaker($input: CreateCaretakerInput!) {{
            {mutation_name}(input: $input) {{
                id
                communityId
                firstName
                lastName
                email
                role
                isActive
                createdAt
                updatedAt
            }}
        }}
    """)
    
    try:
        result = client.execute(mutation, variable_values={'input': caretaker_data})
        return result[mutation_name]
    except Exception as e:
        print(f"Error creating caretaker '{caretaker_data.get('firstName')} {caretaker_data.get('lastName')}': {str(e)}")
        return None


def process_excel_file(file_path: str, use_community_caretaker: bool = False) -> Dict:
    """
    Process the entire Excel file and create communities and caretakers
    
    Args:
        file_path: Path to the Excel file
        use_community_caretaker: If True, use createCommunityCaretaker mutation
    
    Returns:
        Dictionary with summary of created records
    """
    # Create GraphQL client
    client = create_appsync_client()
    
    # Read data from Excel
    print("Reading data from Excel file...")
    communities = read_community_data(file_path)
    caretakers = read_caretaker_data(file_path)
    
    print(f"Found {len(communities)} communities and {len(caretakers)} caretakers to create")
    
    # Create communities
    created_communities = []
    community_id_map = {}  # Map community name to ID for later use
    
    print("\n" + "="*60)
    print("Creating Communities...")
    print("="*60)
    
    for idx, community_data in enumerate(communities, 1):
        print(f"\n[{idx}/{len(communities)}] Creating community: {community_data.get('name')}")
        result = create_community(client, community_data)
        
        if result:
            created_communities.append(result)
            community_id_map[community_data.get('name')] = result['id']
            print(f"  ✓ Successfully created with ID: {result['id']}")
        else:
            print(f"  ✗ Failed to create")
    
    # Create caretakers
    created_caretakers = []
    
    print("\n" + "="*60)
    print("Creating Caretakers...")
    print("="*60)
    
    for idx, caretaker_data in enumerate(caretakers, 1):
        print(f"\n[{idx}/{len(caretakers)}] Creating caretaker: {caretaker_data.get('firstName')} {caretaker_data.get('lastName')}")
        result = create_caretaker(client, caretaker_data, use_community_caretaker)
        
        if result:
            created_caretakers.append(result)
            print(f"  ✓ Successfully created with ID: {result['id']}")
        else:
            print(f"  ✗ Failed to create")
    
    # Summary
    summary = {
        'communities': {
            'total': len(communities),
            'created': len(created_communities),
            'failed': len(communities) - len(created_communities),
            'data': created_communities
        },
        'caretakers': {
            'total': len(caretakers),
            'created': len(created_caretakers),
            'failed': len(caretakers) - len(created_caretakers),
            'data': created_caretakers
        }
    }
    
    return summary


def main():
    """Main function to process registration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process Community Registration Excel file')
    parser.add_argument('file', help='Path to Excel file')
    parser.add_argument('--community-caretaker', action='store_true',
                       help='Use createCommunityCaretaker mutation instead of createCaretaker')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found")
        return
    
    print("="*60)
    print("Community Registration Processor")
    print("="*60)
    print(f"File: {args.file}")
    print(f"API URL: {os.getenv('APPSYNC_API_URL')}")
    print(f"Region: {os.getenv('AWS_REGION', 'us-east-1')}")
    print("="*60)
    
    try:
        summary = process_excel_file(args.file, args.community_caretaker)
        
        # Print summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"\nCommunities:")
        print(f"  Total: {summary['communities']['total']}")
        print(f"  Created: {summary['communities']['created']}")
        print(f"  Failed: {summary['communities']['failed']}")
        
        print(f"\nCaretakers:")
        print(f"  Total: {summary['caretakers']['total']}")
        print(f"  Created: {summary['caretakers']['created']}")
        print(f"  Failed: {summary['caretakers']['failed']}")
        
        print("\n" + "="*60)
        print("Processing complete!")
        print("="*60)
        
    except Exception as e:
        print(f"\nError processing file: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

