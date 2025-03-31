import json
import boto3
import base64
import uuid
import logging

# Initialize AWS clients
s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")
dynamodb = boto3.resource("dynamodb")

# AWS Resource Names
EMPLOYEE_BUCKET = "attend-recog"  # Store employee images
COLLECTION_ID = "EmployeeFaces"
TABLE_NAME = "Employees"

# Enable logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        logger.info("Received event: %s", json.dumps(event))

        # Ensure request body exists
        if "body" not in event or not event["body"]:
            logger.error("Missing request body")
            return error_response(400, "Missing request body")

        try:
            body = json.loads(event["body"])
            logger.info("Parsed request body: %s", body)

            # Validate required fields
            required_fields = ["EmployeeID", "Name", "Sector", "Image"]
            for field in required_fields:
                if field not in body:
                    logger.error(f"Missing required field: {field}")
                    return error_response(400, f"Missing required field: {field}")

        except json.JSONDecodeError:
            logger.error("Invalid JSON format")
            return error_response(400, "Invalid JSON format")

        # Decode Base64 image
        try:
            image_data = base64.b64decode(body["Image"])
            image_name = f"{body['EmployeeID']}.png"  # Store image using EmployeeID
        except Exception as e:
            logger.error("Invalid base64 image: %s", str(e))
            return error_response(400, "Invalid base64 image")

        logger.info("Generated image name: %s", image_name)

        # Upload image to S3 (attend-recog bucket)
        try:
            s3.put_object(
                Bucket=EMPLOYEE_BUCKET,
                Key=image_name,
                Body=image_data,
                ContentType="image/png"
            )
            logger.info("Employee image uploaded to S3: %s", image_name)
        except Exception as e:
            logger.error("S3 upload error: %s", str(e))
            return error_response(500, "S3 upload failed")

        # Index face in Rekognition
        try:
            rekognition.index_faces(
                CollectionId=COLLECTION_ID,
                Image={"S3Object": {"Bucket": EMPLOYEE_BUCKET, "Name": image_name}},
                ExternalImageId=body["EmployeeID"],
                DetectionAttributes=[]
            )
            logger.info("Face indexed in Rekognition: %s", image_name)
        except Exception as e:
            logger.error("Rekognition indexing error: %s", str(e))
            return error_response(500, "Rekognition indexing failed")

        # Store employee details in DynamoDB
        try:
            table = dynamodb.Table(TABLE_NAME)
            table.put_item(Item={
                "EmployeeID": body["EmployeeID"],
                "Name": body["Name"],
                "Sector": body["Sector"],
                "ImageName": image_name  # Save image reference
            })
            logger.info("Employee details saved to DynamoDB: %s", body["EmployeeID"])
        except Exception as e:
            logger.error("DynamoDB error: %s", str(e))
            return error_response(500, "DynamoDB write failed")

        return success_response(200, {"message": "Employee registered successfully!"})

    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return error_response(500, "Unexpected error")


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
