import boto3
import json

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb")
TABLE_NAME = "AttendanceRecords"

def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)

    try:
        # Scan the table to get all records
        response = table.scan()
        items = response.get("Items", [])

        # Format the response
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps(items)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({"error": str(e)})
        }
