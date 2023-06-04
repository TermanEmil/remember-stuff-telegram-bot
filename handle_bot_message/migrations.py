from botocore.exceptions import ClientError

import configs


def ensure_user_session_table_exists(dynamodb):
    try:
        dynamodb.create_table(
            TableName=configs.user_session_table_name,
            KeySchema=[
                {
                    'AttributeName': 'chat_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'chat_id',
                    'AttributeType': 'N'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print(f'Table created: {configs.user_session_table_name}')
    except ClientError as ce:
        if ce.response['Error']['Code'] != 'ResourceInUseException':
            raise ce


def ensure_conversation_table_exists(dynamodb):
    try:
        dynamodb.create_table(
            TableName=configs.conversation_table_name,
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
        print(f'Table created: {configs.conversation_table_name}')
    except ClientError as ce:
        if ce.response['Error']['Code'] != 'ResourceInUseException':
            raise ce

