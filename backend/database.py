"""
DynamoDB database setup and operations for StoryWeave
"""
import boto3
import os
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

# Initialize DynamoDB client
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.environ.get('AWS_REGION', 'us-west-2')
)


def create_tables():
    """
    Create all required DynamoDB tables
    Run this once during initial setup
    """
    region = os.environ.get('AWS_REGION', 'us-west-2')
    dynamodb_client = boto3.client('dynamodb', region_name=region)

    tables_config = [
        {
            'TableName': os.environ.get('DYNAMODB_TABLE_USERS', 'StoryWeave-Users'),
            'KeySchema': [
                {'AttributeName': 'email', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': os.environ.get('DYNAMODB_TABLE_PROFILES', 'StoryWeave-Profiles'),
            'KeySchema': [
                {'AttributeName': 'child_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'child_id', 'AttributeType': 'S'},
                {'AttributeName': 'user_email', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'user_email-index',
                    'KeySchema': [
                        {'AttributeName': 'user_email', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': os.environ.get('DYNAMODB_TABLE_STORIES', 'StoryWeave-Stories'),
            'KeySchema': [
                {'AttributeName': 'story_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'story_id', 'AttributeType': 'S'},
                {'AttributeName': 'child_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'child_id-timestamp-index',
                    'KeySchema': [
                        {'AttributeName': 'child_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': os.environ.get('DYNAMODB_TABLE_CACHE', 'StoryWeave-Cache'),
            'KeySchema': [
                {'AttributeName': 'cache_key', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'cache_key', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        }
    ]

    for table_config in tables_config:
        try:
            table = dynamodb_client.create_table(**table_config)
            logger.info(f"Creating table {table_config['TableName']}...")
            print(f"✓ Table {table_config['TableName']} created successfully")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"⚠ Table {table_config['TableName']} already exists")
            else:
                logger.error(f"Error creating table {table_config['TableName']}: {str(e)}")
                raise

    # Enable TTL on cache table
    try:
        cache_table_name = os.environ.get('DYNAMODB_TABLE_CACHE', 'StoryWeave-Cache')
        dynamodb_client.update_time_to_live(
            TableName=cache_table_name,
            TimeToLiveSpecification={
                'Enabled': True,
                'AttributeName': 'expires_at'
            }
        )
        print(f"✓ TTL enabled on {cache_table_name}")
    except ClientError as e:
        if 'TimeToLive is already enabled' in str(e):
            print(f"⚠ TTL already enabled on {cache_table_name}")
        else:
            logger.warning(f"Could not enable TTL: {str(e)}")


def get_table(table_type):
    """
    Get a DynamoDB table reference

    Args:
        table_type: 'users', 'profiles', 'stories', or 'cache'
    """
    table_names = {
        'users': os.environ.get('DYNAMODB_TABLE_USERS', 'StoryWeave-Users'),
        'profiles': os.environ.get('DYNAMODB_TABLE_PROFILES', 'StoryWeave-Profiles'),
        'stories': os.environ.get('DYNAMODB_TABLE_STORIES', 'StoryWeave-Stories'),
        'cache': os.environ.get('DYNAMODB_TABLE_CACHE', 'StoryWeave-Cache')
    }

    table_name = table_names.get(table_type)
    if not table_name:
        raise ValueError(f"Invalid table type: {table_type}")

    return dynamodb.Table(table_name)


def save_profile(profile_data):
    """Save a child profile to DynamoDB"""
    import memory_store

    try:
        table = get_table('profiles')
        table.put_item(Item=profile_data)
        logger.info(f"Profile saved to DynamoDB: {profile_data['child_id']}")
        return True
    except ClientError as e:
        logger.warning(f"DynamoDB error, using memory store: {str(e)}")
        # Fallback to memory store
        return memory_store.save_profile_memory(profile_data)


def get_profile(child_id):
    """Retrieve a child profile from DynamoDB"""
    table = get_table('profiles')
    try:
        response = table.get_item(Key={'child_id': child_id})
        return response.get('Item')
    except ClientError as e:
        logger.error(f"Error getting profile: {str(e)}")
        return None


def save_story(child_id, story_text, profile_type, theme, age, interests, story_length):
    """Save a story to DynamoDB"""
    from utils import generate_uuid, get_current_timestamp
    from decimal import Decimal

    table = get_table('stories')
    story_data = {
        'story_id': generate_uuid(),
        'child_id': child_id,
        'story': story_text,
        'profile_type': profile_type,
        'theme': theme,
        'age': age,
        'interests': interests,
        'story_length': Decimal(str(story_length)),
        'timestamp': get_current_timestamp()
    }

    try:
        table.put_item(Item=story_data)
        logger.info(f"Story saved: {story_data['story_id']}")
        return True
    except ClientError as e:
        logger.error(f"Error saving story: {str(e)}")
        raise


def get_story_history(child_id, limit=10):
    """Get story history for a child"""
    table = get_table('stories')
    try:
        response = table.query(
            IndexName='child_id-timestamp-index',
            KeyConditionExpression='child_id = :child_id',
            ExpressionAttributeValues={':child_id': child_id},
            ScanIndexForward=False,
            Limit=limit
        )
        return response.get('Items', [])
    except ClientError as e:
        logger.error(f"Error getting story history: {str(e)}")
        return []


def get_cached_story(cache_key):
    """Get a cached story"""
    table = get_table('cache')
    try:
        response = table.get_item(Key={'cache_key': cache_key})
        return response.get('Item')
    except ClientError as e:
        logger.error(f"Error getting cached story: {str(e)}")
        return None


def save_cached_story(cache_key, story_text, expires_at):
    """Save a story to cache"""
    table = get_table('cache')
    cache_data = {
        'cache_key': cache_key,
        'story': story_text,
        'expires_at': expires_at,
        'access_count': 0
    }

    try:
        table.put_item(Item=cache_data)
        logger.info(f"Story cached: {cache_key}")
        return True
    except ClientError as e:
        logger.error(f"Error caching story: {str(e)}")
        return False


def create_user(email, password_hash, name):
    """Create a new user account"""
    from utils import get_current_timestamp
    import memory_store

    try:
        table = get_table('users')
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'name': name,
            'created_at': get_current_timestamp(),
            'updated_at': get_current_timestamp()
        }

        # Check if user already exists
        existing_user = get_user(email)
        if existing_user:
            return {'error': 'User with this email already exists'}, False

        table.put_item(Item=user_data)
        logger.info(f"User created in DynamoDB: {email}")
        return user_data, True
    except ClientError as e:
        logger.warning(f"DynamoDB error, using memory store: {str(e)}")
        # Fallback to memory store
        return memory_store.create_user_memory(email, password_hash, name)


def get_user(email):
    """Get user by email"""
    import memory_store

    try:
        table = get_table('users')
        response = table.get_item(Key={'email': email})
        return response.get('Item')
    except ClientError as e:
        logger.warning(f"DynamoDB error, checking memory store: {str(e)}")
        # Fallback to memory store
        return memory_store.get_user_memory(email)


def get_profiles_by_user(user_email):
    """Get all child profiles for a user"""
    import memory_store
    from boto3.dynamodb.conditions import Attr

    try:
        table = get_table('profiles')
        # Use scan with filter instead of query (works without GSI)
        # Note: This is less efficient but works with current IAM permissions
        response = table.scan(
            FilterExpression=Attr('user_email').eq(user_email)
        )
        return response.get('Items', [])
    except ClientError as e:
        logger.warning(f"DynamoDB error, checking memory store: {str(e)}")
        # Fallback to memory store
        return memory_store.get_profiles_by_user_memory(user_email)


if __name__ == "__main__":
    # Run this to create tables
    print("Creating DynamoDB tables...")
    create_tables()
    print("\n✓ All tables created successfully!")
    print("\nYou can now run the Flask application.")
