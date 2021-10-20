import sqlite3

import boto3

# from common import conn
from secrets import AWS_DYNAMO_ID, AWS_REGION, AWS_DYNAMO_KEY


class CommonHelper:
    def __init__(self):
        self.conn = sqlite3.connect("bot_db.sqlite")
        self.db_cursor = self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_cursor.close()

    def set_bot_setting(self, key, value):
        sql_update_query = """update bot_settings set value = ? where key=?"""
        self.db_cursor.execute(sql_update_query, (value, key))
        self.conn.commit()

    def get_bot_setting(self, key):
        sql_select_query = """select value from bot_settings where key = ?"""
        return self.db_cursor.execute(sql_select_query, [key]).fetchone()[0]

    def get_dynamo_resource(self):
        return boto3.resource(
            "dynamodb",
            aws_access_key_id=AWS_DYNAMO_ID,
            aws_secret_access_key=AWS_DYNAMO_KEY,
            region_name=AWS_REGION,
        )
