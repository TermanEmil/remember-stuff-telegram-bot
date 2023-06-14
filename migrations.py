from botocore.exceptions import ClientError

import configs


def ensure_conversation_table_exists(dynamodb):
    table_name = configs.conversation_table_name
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print(f'Table created: {table_name}')
    except ClientError as ce:
        if ce.response['Error']['Code'] != 'ResourceInUseException':
            raise ce


def ensure_user_data_table_exists(dynamodb):
    table_name = configs.user_data_table_name
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'N'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print(f'Table created: {table_name}')
    except ClientError as ce:
        if ce.response['Error']['Code'] != 'ResourceInUseException':
            raise ce
