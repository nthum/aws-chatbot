from langchain.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import boto3
from botocore.exceptions import ClientError
import json

class S3ListBucketsInput(BaseModel):
    """Input for S3 List Buckets Tool."""
    pass

class S3ListBucketsTool(BaseTool):
    name: str = "s3_list_buckets"
    description: str = "List all S3 buckets in the AWS account."
    args_schema: Type[BaseModel] = S3ListBucketsInput

    def _run(self) -> str:
        s3 = boto3.client('s3')
        try:
            response = s3.list_buckets()
            buckets = [bucket['Name'] for bucket in response.get('Buckets', [])]
            return json.dumps(buckets)
        except ClientError as e:
            return f"Error listing S3 buckets: {e}"
        
class S3BucketInput(BaseModel):
    """Input schema for S3 bucket operations."""
    pass

class S3BucketContentsInput(S3BucketInput):
    """Input for S3 Bucket Contents Tool."""
    bucket_name: str = Field(description="The name of the S3 bucket.")

class S3BucketContentsTool(BaseTool):
    name: str = "s3_bucket_contents"
    description: str = "List contents of a specified S3 bucket."
    args_schema: Type[BaseModel] = S3BucketContentsInput

    def _run(self, bucket_name: str) -> str:
        s3 = boto3.client('s3')
        try:
            response = s3.list_objects_v2(Bucket=bucket_name)
            contents = [obj['Key'] for obj in response.get('Contents', [])]
            return json.dumps(contents)
        except ClientError as e:
            return f"Error listing contents of bucket {bucket_name}: {e}"
        
class EC2ListInstancesInput(BaseModel):
    """Input for EC2 List Instances Tool."""
    pass

class EC2ListInstancesTool(BaseTool):
    name: str = "ec2_list_instances"
    description: str = "List all EC2 instances in the AWS account."
    args_schema: Type[BaseModel] = EC2ListInstancesInput

    def _run(self) -> str:
        ec2 = boto3.client('ec2')
        try:
            response = ec2.describe_instances()
            instances = []
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instances.append(instance['InstanceId'])
            return json.dumps(instances)
        except ClientError as e:
            return f"Error listing EC2 instances: {e}"
    
class IAMListUsersInput(BaseModel):
    """Input for IAM List Users Tool."""
    pass

class IAMListUsersTool(BaseTool):
    name: str = "iam_list_users"
    description: str = "List all IAM users in the AWS account."
    args_schema: Type[BaseModel] = IAMListUsersInput

    def _run(self) -> str:
        iam = boto3.client('iam')
        try:
            response = iam.list_users()
            users = [user['UserName'] for user in response.get('Users', [])]
            return json.dumps(users)
        except ClientError as e:
            return f"Error listing IAM users: {e}"
        
class S3PublicBucketsTool(BaseTool):
    name: str = "s3_public_buckets"
    description: str = "List all public S3 buckets in the AWS account."
    args_schema: Type[BaseModel] = S3ListBucketsInput

    def _run(self) -> str:
        s3 = boto3.client('s3')
        public_buckets = []
        try:
            response = s3.list_buckets()
            for bucket in response.get('Buckets', []):
                bucket_name = bucket['Name']
                acl = s3.get_bucket_acl(Bucket=bucket_name)
                for grant in acl.get('Grants', []):
                    if 'URI' in grant.get('Grantee', {}) and 'AllUsers' in grant['Grantee']['URI']:
                        public_buckets.append(bucket_name)
                        break
            return json.dumps(public_buckets)
        except ClientError as e:
            return f"Error listing public S3 buckets: {e}"
        
class EC2InstanceSizeTool(BaseTool):
    name: str = "ec2_instance_size"
    description: str = "Get the size (instance type) of a specified EC2 instance."
    args_schema: Type[BaseModel] = EC2ListInstancesInput

    def _run(self) -> str:
        ec2 = boto3.client('ec2')
        try:
            response = ec2.describe_instances()
            instance_sizes = {}
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instance_id = instance['InstanceId']
                    instance_type = instance['InstanceType']
                    instance_sizes[instance_id] = instance_type
            return json.dumps(instance_sizes)
        except ClientError as e:
            return f"Error retrieving EC2 instance sizes: {e}"

class IAMUserPermissionsInput(BaseModel):
    """Input for IAM User Permissions Tool."""
    username: str = Field(description="The IAM username to check permissions for")

class IAMUserPermissionsTool(BaseTool):
    name: str = "iam_user_permissions"
    description: str = "Get the permissions attached to a specified IAM user."
    args_schema: Type[BaseModel] = IAMUserPermissionsInput

    def _run(self, username: str) -> str:
        iam = boto3.client('iam')
        try:
            response = iam.list_attached_user_policies(UserName=username)
            policies = [policy['PolicyName'] for policy in response.get('AttachedPolicies', [])]
            return json.dumps(policies)
        except ClientError as e:
            return f"Error retrieving permissions for IAM user {username}: {e}"
        
def get_aws_tools():
    """Return a list of AWS tools."""
    return [
        S3ListBucketsTool(),
        S3BucketContentsTool(),
        EC2ListInstancesTool(),
        IAMListUsersTool(),
        S3PublicBucketsTool(),
        EC2InstanceSizeTool(),
        IAMUserPermissionsTool()
    ]