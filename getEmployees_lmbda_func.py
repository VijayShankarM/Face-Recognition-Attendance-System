import json
import boto3

# Initialize AWS resources
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Employees")

# S3 Bucket Details
S3_BUCKET = "attend-recog"
S3_REGION = "us-east-1"

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))  # Debugging log

        # Handle OPTIONS request for CORS
        if event["httpMethod"] == "OPTIONS":
            return cors_response()

        # Fetch employees from DynamoDB
        response = table.scan()
        employees = response.get("Items", [])

        # Process employee images
        for employee in employees:
            if "ImageName" in employee and employee["ImageName"]:  # Fix field name
                # Ensure S3 URL is correctly formatted
                employee["Image"] = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{employee['ImageName']}"
            else:
                # Placeholder if no image
                employee["Image"] = "https://dummyimage.com/100x100/cccccc/ffffff&text=No+Image"

        print("Processed Employees Data:", json.dumps(employees))  # Debugging log

        return success_response(200, employees)

    except Exception as e:
        print("Error:", str(e))  # Log error
        return error_response(500, str(e))

### 🔹 Helper Functions ###
def success_response(status_code, data):
    return {
        "statusCode": status_code,
        "headers": cors_headers(),
        "body": json.dumps(data)
    }

def error_response(status_code, message):
    return {
        "statusCode": status_code,
        "headers": cors_headers(),
        "body": json.dumps({"error": message})
    }

def cors_response():
    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps({"message": "CORS preflight success"})
    }

def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Credentials": "true"
    }
