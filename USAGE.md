# Community Registration - Quick Usage Guide

## Overview

This project processes Excel files containing community and caretaker information, then creates them in AWS AppSync using GraphQL mutations.

## Setup (One-time)

1. **Configure environment variables in `env.local`:**

   The configuration file uses INI-style sections for DEV and PRD environments:
   
   ```ini
   [PRD]
   APPSYNC_API_URL=https://your-prod-api.appsync-api.us-east-1.amazonaws.com/graphql
   COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
   COGNITO_IDENTITY_POOL_ID=us-east-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   COGNITO_CLIENT_ID=your-prod-app-client-id
   
   [DEV]
   APPSYNC_API_URL=https://your-dev-api.appsync-api.us-east-1.amazonaws.com/graphql
   COGNITO_USER_POOL_ID=us-east-1_YYYYYYYYY
   COGNITO_IDENTITY_POOL_ID=us-east-1:yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy
   COGNITO_CLIENT_ID=your-dev-app-client-id
   AWS_PROFILE=your-aws-profile  # Optional: for --iam authentication
   ```
   
   **Important**: 
   - `COGNITO_USER_POOL_ID` is **required** for user registration and authentication
   - `COGNITO_CLIENT_ID` is **required** for Cognito JWT authentication (default mode)
   - `COGNITO_IDENTITY_POOL_ID` is optional (only needed if using Cognito Identity Pool features)
   - `AWS_PROFILE` is optional - specifies which profile from `~/.aws/credentials` to use with `--iam` flag
   - When you run the script (without `--iam`), it will prompt for your username and password to authenticate with Cognito
   - The App Client must have `USER_PASSWORD_AUTH` authentication flow enabled

2. **Configure AWS credentials** (for `--iam` authentication):
   
   The `--iam` flag reads credentials from `~/.aws/credentials`:
   ```bash
   # Configure default profile
   aws configure
   
   # Or configure a named profile
   aws configure --profile myprofile
   ```
   
   Then optionally add to `env.local` to use a specific profile:
   ```ini
   AWS_PROFILE=myprofile
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
# Interactive mode - will prompt for environment selection (DEV or PRD)
python process_registration.py path/to/your/file.xlsx

# Specify environment directly via command line
python process_registration.py path/to/your/file.xlsx --env DEV
python process_registration.py path/to/your/file.xlsx --env PRD

# Short form
python process_registration.py path/to/your/file.xlsx -e DEV
```

**Environment Selection:**
- If no `--env` argument is provided, you'll be prompted to choose between DEV and PRD
- **Production Warning**: When PRD is selected, you'll see a prominent warning and must type "yes" to confirm
- This safety feature prevents accidental modifications to production data

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
ENVIRONMENT SELECTION
============================================================

Available environments:
  1. DEV  - Development environment
  2. PRD  - Production environment

Select environment (1 for DEV, 2 for PRD): 1

  ✓ Selected: DEV (Development)
  ✓ Configuration loaded for DEV

============================================================
Community Registration Processor
============================================================
Environment: DEV
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

### Error: "Environment 'XXX' not found in env.local"
- Make sure `env.local` file exists and contains `[DEV]` and `[PRD]` sections
- Check that the section names are spelled correctly (case-sensitive)
- Ensure the file uses INI format with `[SECTION]` headers

### Error: "APPSYNC_API_URL must be set"
- Make sure `env.local` file exists and contains `APPSYNC_API_URL` in the selected environment section

### Error: UnauthorizedException / Unauthorized
This error means authentication succeeded but authorization failed:

1. **Check Cognito groups**: Run with `--verbose` to see JWT claims. Look for `cognito:groups`. 
   If it shows `None`, your user may not be in the required Cognito group for the operation.

2. **Try different auth methods**:
   ```bash
   # Try IAM authentication instead of Cognito JWT
   python process_registration.py data.xlsx --env DEV --iam --verbose
   
   # Try adding Bearer prefix to Authorization header
   python process_registration.py data.xlsx --env DEV --bearer --verbose
   ```

3. **Check AppSync authorization rules**:
   - Go to AWS Console → AppSync → Your API → Schema
   - Look for `@auth` directives on the mutation (e.g., `createCommunity`)
   - Verify your user has the required permissions/group membership

4. **Compare with AppSync Console**:
   - Copy the GraphQL query/variables from the `--verbose` output
   - Paste into AppSync Console → Queries
   - Try running with different auth methods in the console

### Error: AWS authentication failed / Unable to parse JWT token
- **If using Cognito JWT (default)**:
  - Verify `COGNITO_USER_POOL_ID` and `COGNITO_CLIENT_ID` are correct
  - Check that your AppSync API has Cognito User Pool authentication enabled
  - Ensure the App Client has `USER_PASSWORD_AUTH` flow enabled
  
- **If using IAM authentication (--iam flag)**:
  - Verify AWS credentials exist in `~/.aws/credentials`
  - Check `AWS_PROFILE` in `env.local` if using a non-default profile
  - Ensure your IAM user/role has `appsync:GraphQL` permission
  - Verify your AppSync API has IAM authentication enabled

- **If using API Key authentication**:
  - Set `APPSYNC_API_KEY` in `env.local`
  - Ensure API Key authentication is enabled on your AppSync API
  - Verify the API key is correct and not expired

- **To check your AppSync authentication settings**:
  - Go to AWS Console → AppSync → Your API → Settings
  - Check which authentication methods are enabled

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

### Command Line Options

```bash
# Show help
python process_registration.py --help

# Available options:
#   file              Path to Excel file (required)
#   --env, -e         Environment to use: DEV or PRD
#   --verbose, -v     Enable verbose output for debugging
#   --iam             Use IAM authentication instead of Cognito JWT
#   --bearer          Add "Bearer" prefix to Authorization header

# Examples:
python process_registration.py data.xlsx                    # Interactive env selection
python process_registration.py data.xlsx --env DEV          # Use DEV environment
python process_registration.py data.xlsx -e PRD -v          # PRD with verbose output
python process_registration.py data.xlsx -e DEV --iam       # Use IAM auth from ~/.aws/credentials
python process_registration.py data.xlsx -e DEV --bearer    # Try Bearer prefix for auth
```

### Authentication Methods

#### Cognito JWT (Default)
The default authentication method. Prompts for username/password at runtime:
```bash
python process_registration.py data.xlsx --env DEV
```

#### IAM Authentication
Uses AWS credentials from `~/.aws/credentials`. Useful if your AppSync API uses IAM auth:
```bash
python process_registration.py data.xlsx --env DEV --iam
```

To use a specific AWS profile, add to your `env.local`:
```ini
[DEV]
APPSYNC_API_URL=https://your-api.appsync-api.us-east-1.amazonaws.com/graphql
AWS_PROFILE=your-profile-name
```

### Debugging GraphQL Errors

Use `--verbose` to see detailed information:
```bash
python process_registration.py data.xlsx --env DEV --verbose
```

This shows:
- Authentication method and credentials being used
- JWT claims (user ID, email, Cognito groups)
- Full GraphQL queries and variables (can be copied to AppSync Console)
- Detailed error messages

When a GraphQL operation fails, the script automatically prints the query and variables in a format you can copy directly to the AppSync Console to test manually.

### Using in Your Own Scripts

```python
from process_registration import (
    load_environment_config,
    create_appsync_client,
    create_community,
    create_caretaker
)

# Load environment configuration first
load_environment_config('DEV')  # or 'PRD'

# Create client (uses loaded configuration)
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

