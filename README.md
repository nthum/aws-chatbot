# AWS Chatbot

A natural language chatbot using LangChain that can answer questions about AWS resources. The chatbot uses OpenAI's GPT models along with custom AWS tools to query S3, EC2, and IAM services.

## Features

The chatbot can answer questions like:

**S3:**
- List your buckets
- See what's inside a bucket
- Find which buckets are public

**EC2:**
- Show all your instances
- Check instance types/sizes

**IAM:**
- List all users
- See what permissions someone has

## Requirements

- Python 3.8 or newer
- An OpenAI API key
- AWS credentials if you want to use it for real, or just use `--mock` mode 

## Getting Started

### Installation

```bash
cd aws_chatbot
python -m venv .venv
source .venv/bin/activate  
pip install -r requirements.txt
```

Edit `.env` and add your credentials:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   
   # Only needed for chatbot.py (real AWS):
   AWS_ACCESS_KEY_ID=your-aws-access-key-id
   AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
   AWS_DEFAULT_REGION=us-east-1
   ```

### Running it

#### Quick Start with Mock AWS
```bash
python chatbot.py --mock
```

**Use it with your actual AWS:**
```bash
python chatbot.py
```

## Example Questions

```
list all s3 buckets
what ec2 instances do I have?
show me all iam users
which s3 buckets are public?
what permissions does `santa` have?
```

Type `exit` when you're done.

## Files

- `chatbot.py` - It's the main script
- `agent.py` - Sets up the LangChain agent
- `aws_tools.py` - All the AWS operations
- `aws_setup.py` - Creates the fake AWS environment for mock mode

The chatbot is environment-agnostic - it doesn't know whether it's using real or mock AWS. The `aws_setup.py` module handles environment configuration using a context manager pattern.

We can add more tools to `aws_tools.py`

## How to add more aws tools

1. Make an input schema (or use `pass` if it doesn't need parameters)
2. Create a tool class with a `_run` method that does the actual work
3. Add it to the list in `get_aws_tools()`

## Dependencies

- **langchain**: Framework for building agents
- **langchain-openai**: OpenAI integration
- **boto3**: AWS SDK for Python
- **moto**: AWS service mocking

## Sample Output

See `SAMPLE_OUTPUT.md` for detailed example interactions.