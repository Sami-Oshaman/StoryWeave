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
            'TableName': os.environ.get('DYNAMODB_TABLE_PROFILES', 'StoryWeave-Profiles'),
            'KeySchema': [
                {'AttributeName': 'child_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'child_id', 'AttributeType': 'S'}
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
        table_type: 'profiles', 'stories', or 'cache'
    """
    table_names = {
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
    table = get_table('profiles')
    try:
        table.put_item(Item=profile_data)
        logger.info(f"Profile saved: {profile_data['child_id']}")
        return True
    except ClientError as e:
        logger.error(f"Error saving profile: {str(e)}")
        raise


def get_profile(child_id):
    """Retrieve a child profile from DynamoDB"""
    table = get_table('profiles')
    try:
        response = table.get_item(Key={'child_id': child_id})
        return response.get('Item')
    except ClientError as e:
        logger.error(f"Error getting profile: {str(e)}")
        return None


def save_story(story_data):
    """Save a story to DynamoDB"""
    table = get_table('stories')
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


def save_cached_story(cache_data):
    """Save a story to cache"""
    table = get_table('cache')
    try:
        table.put_item(Item=cache_data)
        logger.info(f"Story cached: {cache_data['cache_key']}")
        return True
    except ClientError as e:
        logger.error(f"Error caching story: {str(e)}")
        return False


def update_cache_access_count(cache_key):
    """Increment access count for cached story"""
    table = get_table('cache')
    try:
        table.update_item(
            Key={'cache_key': cache_key},
            UpdateExpression='SET access_count = access_count + :inc',
            ExpressionAttributeValues={':inc': 1}
        )
    except ClientError as e:
        logger.warning(f"Could not update access count: {str(e)}")


if __name__ == "__main__":
    # Run this to create tables
    print("Creating DynamoDB tables...")
    create_tables()
    print("\n✓ All tables created successfully!")
    print("\nYou can now run the Flask application.")
