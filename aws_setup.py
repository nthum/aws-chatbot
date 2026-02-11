from moto import mock_aws
import boto3
import os

class AWSEnvironment:
    def __init__(self, use_moto=True):
        self.use_moto = use_moto
        self.mock_decorator = None
        
    def __enter__(self):
        if self.use_moto:
            self.mock_decorator = mock_aws()
            self.mock_decorator.__enter__()
            setup_mock_aws_resources()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.mock_decorator:
            self.mock_decorator.__exit__(exc_type, exc_val, exc_tb)

# Set
def setup_mock_aws_resources():
    """
    Setup mock AWS resources.
    Creates S3 buckets, EC2 instances, and IAM users with sample data.
    """

    print("Setting up mock AWS environment...")

    # Setup S3 buckets
    _setup_s3_resources()

    # Setup EC2 instances
    _setup_ec2_resources()

    # Setup IAM users
    _setup_iam_resources()

    print("Mock AWS environment setup completed.\n")

def _setup_s3_resources():
    """Setup mock S3 buckets and objects."""
    s3 = boto3.client('s3', region_name='us-east-1')

    # Create mock S3 buckets
    bucket_names = ['test-bucket-1', 'test-bucket-2', 'test-bucket-3','test-bucket-4']
    
    for bucket_name in bucket_names:
        s3.create_bucket(Bucket=bucket_name)
        s3.put_bucket_acl(Bucket=bucket_name, ACL='public-read')

    s3.put_object(Bucket=bucket_names[0], Key='text_test_data.txt', Body='This is a sample file.')
    s3.put_object(Bucket=bucket_names[1], Key='csv_test_data.csv', Body='id,name\n1,John\n2,Doe')
    s3.put_object(Bucket=bucket_names[2], Key='images/logo.png', Body='PNG data' * 100)
    s3.put_object(Bucket=bucket_names[3], Key='json_test_data.json', Body='{"key": "value"}')

    # Create private bucket
    s3.create_bucket(Bucket='private-backups')
    s3.put_public_access_block(
        Bucket='private-backups',
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )
    s3.put_object(
        Bucket='private-backups',
        Key='backup-2024-12.tar.gz',
        Body=b'backup data' * 10000
    )

def _setup_ec2_resources():
    """Setup mock EC2 instances."""
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    ec2 = boto3.client('ec2', region_name='us-east-1')

    # Create VPC and subnet
    vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
    subnet = ec2.create_subnet(
        VpcId=vpc['Vpc']['VpcId'],
        CidrBlock='10.0.1.0/24'
    )

    # Create mock EC2 instances
    ec2.run_instances(
        ImageId='test-12345678',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        SubnetId=subnet['Subnet']['SubnetId'],
        PrivateIpAddress='10.0.1.5',
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [
                {'Key': 'Name', 'Value': 'Web Server 1'},
                {'Key': 'Environment', 'Value': 'Production'}
            ]
        }]
    )

    # Create another Web Server instance
    ec2.run_instances(
        ImageId='test-12345678',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        SubnetId=subnet['Subnet']['SubnetId'],
        PrivateIpAddress='10.0.1.6',
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [
                {'Key': 'Name', 'Value': 'Web Server 2'},
                {'Key': 'Environment', 'Value': 'UAT'}
            ]
        }]
    )

    # Create Database Server instance
    ec2.run_instances(
        ImageId='test-87654321',
        MinCount=1,
        MaxCount=1,
        InstanceType='m5.large',
        SubnetId=subnet['Subnet']['SubnetId'],
        PrivateIpAddress='10.0.1.10',
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [
                {'Key': 'Name', 'Value': 'Database Server'},
                {'Key': 'Environment', 'Value': 'Production'}
            ]
        }]
    )

def _setup_iam_resources():
    """Setup mock IAM users and policies."""
    iam = boto3.client('iam', region_name='us-east-1')

    # Create mock IAM users
    users = ['grinch', 'santa', 'max']
    for user in users:
        iam.create_user(UserName=user)
    
    # Create custom policies
    admin_policy = iam.create_policy(
        PolicyName='AdministratorAccessPolicy',
        PolicyDocument='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"*","Resource":"*"}]}'
    )
    readonly_policy = iam.create_policy(
        PolicyName='ReadOnlyAccessPolicy',
        PolicyDocument='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["s3:Get*","s3:List*","ec2:Describe*"],"Resource":"*"}]}'
    )
    
    # Attach policies to users
    iam.attach_user_policy(
        UserName='santa',
        PolicyArn=admin_policy['Policy']['Arn']
    )
    iam.attach_user_policy(
        UserName='grinch',
        PolicyArn=readonly_policy['Policy']['Arn']
    )

    # Add inline EC2 describe policy
    iam.put_user_policy(
        UserName='santa',
        PolicyName='EC2Describe',
        PolicyDocument='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"ec2:Describe*","Resource":"*"}]}'
    )

    # Create group and add user
    iam.create_group(GroupName='Developers')
    iam.add_user_to_group(UserName='santa', GroupName='Developers')

    # Attach CloudWatch policy to group
    group_policy = iam.create_policy(
        PolicyName='CloudWatchReadOnly',
        PolicyDocument='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["cloudwatch:Describe*","cloudwatch:Get*","cloudwatch:List*"],"Resource":"*"}]}'
    )
    iam.attach_group_policy(
        GroupName='Developers',
        PolicyArn=group_policy['Policy']['Arn']
    )
