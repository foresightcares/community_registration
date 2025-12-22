# Community Registration - AWS GraphQL

This project uses AWS AppSync GraphQL API for community registration management.

## Environment Setup

The environment is managed using `uv` and Python virtual environment.

### Prerequisites

- Python 3.9+
- `uv` package manager
- AWS credentials configured

### Installation

1. Activate the virtual environment:
```bash
source .venv/bin/activate
```

2. Install dependencies (already done):
```bash
uv pip install -r requirements.txt
```

### Installed Packages

- **boto3**: AWS SDK for Python
- **gql**: GraphQL client library
- **requests-aws4auth**: AWS authentication for requests
- **openpyxl**: Excel file processing
- **python-dotenv**: Load environment variables from files

## AWS Configuration

### Configuration File: `env.local`

All project configuration is managed through the `env.local` file using INI-style sections for different environments.

The file supports two environment sections:
- `[DEV]` - Development environment configuration
- `[PRD]` - Production environment configuration

**Example `env.local` format:**

```ini
[PRD]
APPSYNC_API_URL=https://your-prod-api.appsync-api.us-east-1.amazonaws.com/graphql
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
COGNITO_IDENTITY_POOL_ID=us-east-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
COGNITO_CLIENT_ID=your-prod-client-id

[DEV]
APPSYNC_API_URL=https://your-dev-api.appsync-api.us-east-1.amazonaws.com/graphql
COGNITO_USER_POOL_ID=us-east-1_YYYYYYYYY
COGNITO_IDENTITY_POOL_ID=us-east-1:yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy
COGNITO_CLIENT_ID=your-dev-client-id
```

**Configuration variables for each environment:**

1. **APPSYNC_API_URL** - Set your AWS AppSync GraphQL endpoint
2. **AWS_REGION** - Set your AWS region (default: us-east-1)
3. **COGNITO_USER_POOL_ID** - **REQUIRED**: Set your AWS Cognito User Pool ID for user registration and authentication
4. **COGNITO_CLIENT_ID** - **REQUIRED**: Set your Cognito User Pool App Client ID for authentication
5. **COGNITO_IDENTITY_POOL_ID** - (Optional) Set your Cognito Identity Pool ID if using Identity Pool features
6. **APPSYNC_API_KEY** - (Optional) API Key for AppSync if using API Key authentication instead of Cognito JWT

### AWS Credentials Setup

You have two options for AWS credentials:

#### Option 1: AWS Credentials File (Recommended)

Create or edit `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

Create or edit `~/.aws/config`:
```ini
[default]
region = us-east-1
```

#### Option 2: Environment Variables in `env.local`

Uncomment and set the following in `env.local`:
```bash
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
```

## Usage

The project loads configuration from `env.local` based on the selected environment (DEV or PRD).

### Quick Start

1. **Edit `env.local`** - Configure both DEV and PRD sections with appropriate values:
   ```ini
   [DEV]
   APPSYNC_API_URL=https://your-dev-api.appsync-api.us-east-1.amazonaws.com/graphql
   COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
   COGNITO_CLIENT_ID=your-dev-client-id
   
   [PRD]
   APPSYNC_API_URL=https://your-prod-api.appsync-api.us-east-1.amazonaws.com/graphql
   COGNITO_USER_POOL_ID=us-east-1_YYYYYYYYY
   COGNITO_CLIENT_ID=your-prod-client-id
   ```

2. **Run the example script:**
   ```bash
   source .venv/bin/activate
   python example_graphql.py
   ```

### Using in Your Code

All functions automatically read from `env.local`:

```python
from example_graphql import create_appsync_client

# Client automatically uses env.local configuration
client = create_appsync_client()

# Or override with specific values
client = create_appsync_client(
    api_url="https://custom-api.appsync-api.us-east-1.amazonaws.com/graphql",
    region="us-west-2"
)
```

See `example_graphql.py` for complete examples of:
- Connecting to AWS AppSync with environment variables
- Executing GraphQL queries
- Executing GraphQL mutations

## Project Structure

```
.
├── .venv/                          # Virtual environment (managed by uv)
├── input_sample/                   # Sample input files
│   └── Community_Registration.xlsx
├── types/                          # GraphQL schema
│   └── schema.graphql
├── example_graphql.py              # Example GraphQL usage
├── process_registration.py         # Main processor for Excel files
├── create_sample_data.py           # Generate sample Excel data
├── requirements.txt                # Python dependencies
├── env.local                       # Environment variables (configure this!)
└── README.md                       # This file
```

## Processing Registration Data

### Quick Start

1. **Prepare your Excel file** following the format in `input_sample/Community_Registration.xlsx`:
   - **Community Info sheet**: Community details
   - **Users sheet**: Caretaker/user details

2. **Run the processor:**
   ```bash
   source .venv/bin/activate
   
   # Interactive mode - prompts for environment selection
   python process_registration.py input_sample/Community_Registration.xlsx
   
   # Or specify environment directly
   python process_registration.py input_sample/Community_Registration.xlsx --env DEV
   python process_registration.py input_sample/Community_Registration.xlsx --env PRD
   
   # Use IAM authentication (from ~/.aws/credentials) instead of Cognito JWT
   python process_registration.py input_sample/Community_Registration.xlsx --env DEV --iam
   
   # Enable verbose output for debugging
   python process_registration.py input_sample/Community_Registration.xlsx --env DEV --verbose
   ```
   
   The processor uses `createCommunityCaretaker` mutation for all caretaker creation.
   
   **Command Line Options:**
   - `--env, -e`: Environment to use (DEV or PRD). If not specified, prompts for selection.
   - `--iam`: Use IAM authentication from `~/.aws/credentials` instead of Cognito JWT
   - `--bearer`: Add "Bearer" prefix to Authorization header (troubleshooting option)
   - `--verbose, -v`: Enable verbose output showing auth details and GraphQL queries
   
   **Environment Selection:**
   - If no `--env` argument is provided, you'll be prompted to select DEV or PRD
   - When selecting PRD (Production), you'll see a warning and must type "yes" to confirm
   - This helps prevent accidental modifications to production data
   
   **Cognito Integration (Required):**
   - Cognito integration is **required** for user authentication
   - The system will:
     - Create a Cognito group for each community
     - Add caretakers to Cognito User Pool after GraphQL creation
     - Automatically send invitation emails with temporary passwords
     - Assign users to their community's Cognito group
   - Users must verify their email addresses (email_verified is set to false)
   - **If any Cognito operation fails, the entire process will fail** since users cannot login without Cognito registration

### Excel File Format

#### Community Info Sheet
| Column | Required | Type | GraphQL Field |
|--------|----------|------|---------------|
| Name | Yes | String | name |
| Contact Phone Number | Yes | String | phoneNumber |
| Contact Email | Yes | String | email |
| Street | No | String | street |
| City | No | String | city |
| State | No | String | state |
| Country | No | String | country |
| Zip Code | No | String | postalCode |
| No. Resident | No | Integer | residentLimit (default: 100) |
| No. Users | No | Integer | caretakerLimit (default: 10) |
| CommunityId | No | String | (output only) |

#### Users Sheet
| Column | Required | Type | GraphQL Field |
|--------|----------|------|---------------|
| First Name | Yes | String | firstName |
| Last Name | Yes | String | lastName |
| Email | Yes | String | email |
| CommunityId | No | String | communityId |

### Creating Sample Data

Generate a sample Excel file with test data:

```bash
source .venv/bin/activate
python create_sample_data.py
```

This creates `sample_registration.xlsx` with example communities and caretakers.

## Next Steps

1. **Edit `env.local`** - Update `APPSYNC_API_URL` with your actual AWS AppSync endpoint
2. **Configure AWS credentials** - Use `~/.aws/credentials` or add them to `env.local`
3. **Prepare your Excel file** - Follow the format described above
4. **Run the processor** - Use `process_registration.py` to create communities and caretakers
5. **Customize as needed** - Modify the GraphQL operations in the scripts based on your schema

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APPSYNC_API_URL` | Yes | - | AWS AppSync GraphQL endpoint URL |
| `AWS_REGION` | No | `us-east-1` | AWS region for your AppSync API |
| `COGNITO_USER_POOL_ID` | **Yes** | - | AWS Cognito User Pool ID for user registration and authentication |
| `COGNITO_CLIENT_ID` | **Yes**¹ | - | Cognito User Pool App Client ID for authentication |
| `COGNITO_IDENTITY_POOL_ID` | No | - | Cognito Identity Pool ID (optional, for Identity Pool features) |
| `APPSYNC_API_KEY` | No | - | API Key for AppSync (if using API Key authentication) |
| `AWS_PROFILE` | No | `default` | AWS profile name from `~/.aws/credentials` (used with `--iam` flag) |

¹ Required only when using Cognito JWT authentication (default). Not required when using `--iam` flag.

### AWS Credentials for IAM Authentication

When using the `--iam` flag, credentials are read from `~/.aws/credentials`:

```ini
# ~/.aws/credentials
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY

[myprofile]
aws_access_key_id = ANOTHER_ACCESS_KEY
aws_secret_access_key = ANOTHER_SECRET_KEY
```

To use a specific profile, add to your `env.local`:
```ini
[DEV]
APPSYNC_API_URL=https://your-api.appsync-api.us-east-1.amazonaws.com/graphql
AWS_PROFILE=myprofile
```

### AppSync Authentication

The script supports multiple authentication methods:

#### 1. Cognito JWT Authentication (Default)
- Prompts for username and password at runtime
- Authenticates with Cognito User Pool using the specified App Client ID
- Uses JWT token in Authorization header for all GraphQL requests
- Requires `COGNITO_USER_POOL_ID` and `COGNITO_CLIENT_ID` to be set
- Your AppSync API must have Cognito User Pool authentication enabled
- The App Client must have `USER_PASSWORD_AUTH` flow enabled

```bash
# Default - uses Cognito JWT authentication
python process_registration.py input.xlsx --env DEV
```

#### 2. IAM Authentication (--iam flag)
- Uses AWS credentials from `~/.aws/credentials`
- Specify a profile with `AWS_PROFILE` in env.local, or uses `default` profile
- Uses AWS Signature V4 for request signing
- Requires IAM authentication to be enabled on your AppSync API

```bash
# Use IAM authentication from ~/.aws/credentials
python process_registration.py input.xlsx --env DEV --iam
```

To use a specific AWS profile, add to your env.local:
```ini
[DEV]
APPSYNC_API_URL=https://your-api.appsync-api.us-east-1.amazonaws.com/graphql
AWS_PROFILE=your-profile-name
```

#### 3. API Key Authentication
- Set `APPSYNC_API_KEY` in `env.local` to use API Key instead
- Requires API Key authentication to be enabled on your AppSync API

#### Authentication Debugging

Use `--verbose` to see detailed authentication information:
```bash
python process_registration.py input.xlsx --env DEV --verbose
```

This shows:
- Which authentication method is being used
- JWT claims (for Cognito auth): user ID, email, groups, token issuer
- AWS credentials info (for IAM auth): profile, access key prefix

If you get `UnauthorizedException` errors, try the `--bearer` flag which adds "Bearer" prefix to the Authorization header:
```bash
python process_registration.py input.xlsx --env DEV --bearer --verbose
```

**Note**: The script will prompt you for username and password when you run it (unless using `--iam`). This authenticates you with Cognito User Pool to get a JWT token that's used for all GraphQL operations.

### Cognito Integration (Required)

Cognito integration is **mandatory** for user authentication. The system will fail if Cognito operations cannot be completed, as users cannot login without proper Cognito registration.

The system automatically:

1. **Creates Cognito Groups**: One group per community (named `community-{communityId}`)
2. **Registers Users**: Adds caretakers to Cognito User Pool after GraphQL creation
3. **Sends Invitations**: Automatically sends invitation emails with temporary passwords
4. **Assigns to Groups**: Assigns each user to their community's Cognito group
5. **Email Verification**: Sets `email_verified` to `false` - users must verify their email addresses

**Important Notes**:
- The system uses email addresses as usernames in Cognito
- Users will receive invitation emails and must verify their email addresses before they can fully access the system
- **If any Cognito operation fails (group creation, user registration, etc.), the entire process will terminate with an error**
- This ensures data consistency - users are only created if they can successfully authenticate

