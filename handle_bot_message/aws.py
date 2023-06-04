import os

import boto3

import migrations

dynamodb = boto3.resource(
    'dynamodb',
    region_name='eu-central-1',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))


def get_db():
    # migrations.ensure_user_session_table_exists(dynamodb)
    # migrations.ensure_conversation_table_exists(dynamodb)
    return dynamodb

