# Community Registration - Quick Usage Guide

## Overview

This project processes Excel files containing community and caretaker information, then creates them in AWS AppSync using GraphQL mutations.

## Setup (One-time)

1. **Configure environment variables in `env.local`:**
   ```bash
   APPSYNC_API_URL=https://your-api-id.appsync-api.us-east-1.amazonaws.com/graphql
   AWS_REGION=us-east-1
   COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX  # REQUIRED: for user registration and authentication
   COGNITO_CLIENT_ID=your-app-client-id  # REQUIRED: for authentication
   COGNITO_IDENTITY_POOL_ID=us-east-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  # Optional: for Identity Pool features
   ```
   
   **Important**: 
   - `COGNITO_USER_POOL_ID` is **required** for user registration and authentication
   - `COGNITO_CLIENT_ID` is **required** for authentication (get this from Cognito Console → User Pools → Your Pool → App clients)
   - `COGNITO_IDENTITY_POOL_ID` is optional (only needed if using Cognito Identity Pool features)
   - When you run the script, it will prompt for your username and password to authenticate with Cognito
   - The App Client must have `USER_PASSWORD_AUTH` authentication flow enabled

2. **Configure AWS credentials** (choose one method):
   - **Option A:** Use AWS CLI: `aws configure`
   - **Option B:** Add to `env.local`:
     ```bash
     AWS_ACCESS_KEY_ID=your_access_key
     AWS_SECRET_ACCESS_KEY=your_secret_key
     ```

3. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

## Processing Registration Data

### Step 1: Prepare Your Excel File

Your Excel file must have two sheets:

**Sheet 1: "Community Info"**
- Required columns: Name, Contact Phone Number, Contact Email
- Optional columns: Street, City, State, Country, Zip Code, No. Resident, No. Users

**Sheet 2: "Users"**
- Required columns: First Name, Last Name, Email
- Optional column: CommunityId

### Step 2: Run the Processor

```bash
# Basic usage
python process_registration.py path/to/your/file.xlsx
```

### Step 3: Review Results

The script will:
1. Read all communities from "Community Info" sheet (must be exactly one community)
2. Create the community via `createCommunity` mutation
3. Create a Cognito group for the community (required)
4. Read all users from "Users" sheet
5. Create each user via `createCommunityCaretaker` mutation
6. Verify each user was created correctly (round-trip check)
7. Add users to Cognito and assign to community group (required)
8. Update Excel file with the created `communityId` in the Users sheet
9. Display a summary of created records

**Cognito Integration (Required):**
- Automatically creates a Cognito group per community
- Registers users in Cognito User Pool (required for login)
- Sends invitation emails with temporary passwords
- Users must verify their email addresses (not auto-verified)
- Users are assigned to their community's Cognito group
- **If any Cognito operation fails, the entire process will fail** - users cannot login without proper Cognito registration

## Example Output

```
============================================================
Community Registration Processor
============================================================
File: sample_registration.xlsx
API URL: https://your-api-id.appsync-api.us-east-1.amazonaws.com/graphql
Region: us-east-1
============================================================
Reading data from Excel file...
Found 2 communities and 3 caretakers to create

============================================================
Creating Communities...
============================================================

[1/2] Creating community: Sunrise Senior Living
  ✓ Successfully created with ID: abc123

[2/2] Creating community: Golden Years Community
  ✓ Successfully created with ID: def456

============================================================
Creating Caretakers...
============================================================

[1/3] Creating caretaker: John Doe
  ✓ Successfully created with ID: user001

[2/3] Creating caretaker: Jane Smith
  ✓ Successfully created with ID: user002

[3/3] Creating caretaker: Michael Johnson
  ✓ Successfully created with ID: user003

============================================================
SUMMARY
============================================================

Communities:
  Total: 2
  Created: 2
  Failed: 0

Caretakers:
  Total: 3
  Created: 3
  Failed: 0

============================================================
Processing complete!
============================================================
```

## Testing with Sample Data

Create a sample Excel file for testing:

```bash
python create_sample_data.py
```

This creates `sample_registration.xlsx` with:
- 2 sample communities (Sunrise Senior Living, Golden Years Community)
- 3 sample caretakers (John Doe, Jane Smith, Michael Johnson)

You can then test the processor:

```bash
python process_registration.py sample_registration.xlsx
```

## GraphQL Mutations Used

### createCommunity

Maps Excel data to `CreateCommunityInput`:
```graphql
input CreateCommunityInput {
  name: String!                    # From "Name"
  phoneNumber: String!             # From "Contact Phone Number"
  email: String!                   # From "Contact Email"
  street: String                   # From "Street"
  city: String                     # From "City"
  state: String                    # From "State"
  country: String                  # From "Country"
  postalCode: String               # From "Zip Code"
  residentLimit: Int!              # From "No. Resident" (default: 100)
  caretakerLimit: Int!             # From "No. Users" (default: 10)
}
```

### createCommunityCaretaker

Maps Excel data to `CreateCaretakerInput`:
```graphql
input CreateCaretakerInput {
  firstName: String!               # From "First Name"
  lastName: String!                # From "Last Name"
  email: String!                   # From "Email"
  communityId: ID                  # From "CommunityId"
}
```

## Troubleshooting

### Error: "APPSYNC_API_URL must be set"
- Make sure `env.local` file exists and contains `APPSYNC_API_URL`

### Error: AWS authentication failed / Unable to parse JWT token
- **If using IAM authentication**: 
  - Verify AWS credentials are configured correctly
  - Check that your AppSync API has IAM authentication enabled
  - Ensure your IAM user/role has `appsync:GraphQL` permission
  - If IAM auth is not enabled, use API Key authentication instead
- **If using API Key authentication**:
  - Set `APPSYNC_API_KEY` in `env.local`
  - Ensure API Key authentication is enabled on your AppSync API
  - Verify the API key is correct and not expired
- **To check your AppSync authentication settings**:
  - Go to AWS Console → AppSync → Your API → Settings
  - Check which authentication methods are enabled
  - Enable IAM or API Key authentication if needed

### Error: File not found
- Verify the Excel file path is correct
- Use absolute path if relative path doesn't work

### Error: GraphQL validation failed
- Check that required fields are present in Excel file
- Verify Excel column names match expected format

### Error: Multiple communities found
- The Excel file must contain exactly one community in the "Community Info" sheet
- Remove extra community rows or split into separate files

### Error: COGNITO_USER_POOL_ID is required
- `COGNITO_USER_POOL_ID` must be set in `env.local`
- Cognito is required for user authentication - the process will fail without it
- Add `COGNITO_USER_POOL_ID=your-pool-id` to your `env.local` file

### Error: Cognito group creation failed
- Failed to create or retrieve the Cognito group for the community
- Check AWS permissions for Cognito operations
- Verify the `COGNITO_USER_POOL_ID` is correct
- The process will fail since users cannot be assigned to groups

### Error: Cognito user registration failed
- User was created in GraphQL but failed to register in Cognito
- User will not be able to login without Cognito registration
- The process will fail to ensure data consistency

### Warning: Verification failed
- A caretaker was created but not found in the system during verification
- This may indicate a synchronization issue - verify manually

## Advanced Usage

### Using in Your Own Scripts

```python
from process_registration import create_appsync_client, create_community, create_caretaker

# Create client
client = create_appsync_client()

# Create a community
community_data = {
    'name': 'My Community',
    'phoneNumber': '+1-555-1234',
    'email': 'contact@mycommunity.com',
    'residentLimit': 100,
    'caretakerLimit': 10
}
result = create_community(client, community_data)
print(f"Created community with ID: {result['id']}")

# Create a caretaker (uses createCommunityCaretaker mutation)
caretaker_data = {
    'firstName': 'John',
    'lastName': 'Doe',
    'email': 'john@example.com',
    'communityId': result['id']
}
result = create_caretaker(client, caretaker_data)
print(f"Created caretaker with ID: {result['id']}")
```

## Support

For issues or questions, refer to:
- GraphQL schema: `types/schema.graphql`
- Example code: `example_graphql.py`
- Main documentation: `README.md`

