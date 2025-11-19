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

All project configuration is managed through the `env.local` file. This file contains:
- AWS region
- AWS AppSync API URL
- Optional AWS credentials (if not using ~/.aws/credentials)
- Optional AWS profile name

**Edit `env.local` and update the following:**

1. **APPSYNC_API_URL** - Set your AWS AppSync GraphQL endpoint
2. **AWS_REGION** - Set your AWS region (default: us-east-1)

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

The project automatically loads configuration from `env.local` using `python-dotenv`.

### Quick Start

1. **Edit `env.local`** - Update your AWS AppSync API URL and region:
   ```bash
   APPSYNC_API_URL=https://your-actual-api-id.appsync-api.us-east-1.amazonaws.com/graphql
   AWS_REGION=us-east-1
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
   python process_registration.py input_sample/Community_Registration.xlsx
   ```

3. **Optional flags:**
   ```bash
   # Use createCommunityCaretaker mutation instead of createCaretaker
   python process_registration.py input_sample/Community_Registration.xlsx --community-caretaker
   ```

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
| `AWS_ACCESS_KEY_ID` | No | - | AWS access key (if not using ~/.aws/credentials) |
| `AWS_SECRET_ACCESS_KEY` | No | - | AWS secret key (if not using ~/.aws/credentials) |
| `AWS_SESSION_TOKEN` | No | - | AWS session token (for temporary credentials) |
| `AWS_PROFILE` | No | `default` | AWS profile name from ~/.aws/credentials |

