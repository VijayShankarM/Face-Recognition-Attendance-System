import boto3
import base64
import json
import uuid
import logging
from datetime import datetime

# Initialize AWS clients
s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")
dynamodb = boto3.resource("dynamodb")

# AWS Resources
ATTENDANCE_BUCKET = "attendance-images-01"  # Store scanned images
EMPLOYEE_BUCKET = "attend-recog"  # Store employee images
COLLECTION_ID = "EmployeeFaces"
TABLE_NAME = "AttendanceRecords"

# Enable logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        logger.info("Received event: %s", json.dumps(event))

        # Handle CORS preflight request (OPTIONS method)
        if event.get("httpMethod") == "OPTIONS":
            return success_response(200, {"message": "CORS preflight passed"})

        # Validate request body
        if "body" not in event or not event["body"]:
            return error_response(400, "Missing request body")

        try:
            body = json.loads(event["body"])
            if "image" not in body:
                return error_response(400, "Missing 'image' in request")
        except json.JSONDecodeError:
            return error_response(400, "Invalid JSON format")

        # Extract and decode Base64 image
        try:
            base64_str = body["image"]
            if "," in base64_str:
                base64_str = base64_str.split(",")[1]  # Remove metadata prefix
            image_data = base64.b64decode(base64_str)
            image_name = f"{uuid.uuid4()}.png"
        except Exception:
            return error_response(400, "Invalid base64 image format")

        # Upload scanned image to ATTENDANCE_BUCKET
        try:
            s3.put_object(
                Bucket=ATTENDANCE_BUCKET,
                Key=image_name,
                Body=image_data,
                ContentType="image/png"
            )
        except Exception:
            return error_response(500, "S3 upload failed")

        # Search for face match in Rekognition
        try:
            response = rekognition.search_faces_by_image(
                CollectionId=COLLECTION_ID,
                Image={"S3Object": {"Bucket": ATTENDANCE_BUCKET, "Name": image_name}},
                MaxFaces=1,
                FaceMatchThreshold=80
            )
        except Exception:
            return error_response(500, "Rekognition failed")

        # Check if a face match is found
        if not response.get("FaceMatches"):
            return error_response(404, "Face not recognized")

        matched_face = response["FaceMatches"][0]["Face"]
        employee_id = matched_face.get("ExternalImageId", matched_face.get("FaceId")).strip()

        # Fetch employee details from DynamoDB
        employees_table = dynamodb.Table("Employees")
        employee_data = employees_table.get_item(Key={"EmployeeID": employee_id}).get("Item")

        if not employee_data:
            return error_response(404, "Employee not found")

        stored_image_name = employee_data.get("ImageName", "")
        if not stored_image_name:
            return error_response(404, "Image not found in database")

        employee_image_url = f"https://{EMPLOYEE_BUCKET}.s3.amazonaws.com/{stored_image_name}"
        scanned_image_url = f"https://{ATTENDANCE_BUCKET}.s3.amazonaws.com/{image_name}"

        # Store attendance in DynamoDB
        try:
            attendance_table = dynamodb.Table(TABLE_NAME)
            attendance_table.put_item(Item={
                "EmployeeID": employee_id,
                "Timestamp": datetime.utcnow().isoformat(),
                "ImageURL": scanned_image_url,
                "EmployeeName": employee_data.get("Name", "Unknown"),
                "Sector": employee_data.get("Sector", "Unknown")
            })
        except Exception:
            return error_response(500, "DynamoDB write failed")

        return success_response(200, {
            "message": "Attendance marked",
            "employee_id": employee_id,
            "employee_name": employee_data.get("Name", "Unknown"),
            "sector": employee_data.get("Sector", "Unknown"),
            "image_url": employee_image_url
        })
    
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return error_response(500, "Unexpected error")

# Success response function
def success_response(status_code, data):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(data)
    }

# Error response function
def error_response(status_code, message):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps({"error": message})
    }
