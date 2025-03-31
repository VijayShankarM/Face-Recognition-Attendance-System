# Serverless Face Recognition Attendance System

## Project Overview
This project is a serverless face recognition attendance system using AWS services. Employees scan their faces through a web application, and Amazon Rekognition matches the faces to registered employees. If a match is found, attendance is recorded in DynamoDB. The system includes an admin panel for managing employees and viewing attendance logs.

---

## Step-by-Step Setup Instructions

### 1. AWS S3 Configuration
- Create two S3 buckets:
  - One for storing employee images.
  - Another for storing scanned attendance images.
- Enable static website hosting for the frontend bucket.
- Configure bucket policies to allow public read access for images.
- Set up CORS for proper API communication.

### 2. Amazon Rekognition Setup
- Create a Rekognition collection for storing employee faces.
- Upload employee images and index them in the collection.

### 3. AWS DynamoDB Configuration
- Create a table for storing employee details.
- Create another table for recording attendance logs.

### 4. AWS Lambda Functions
- Create a function for employee registration:
  - Upload employee images to S3.
  - Index the faces in the Rekognition collection.
  - Store employee details in DynamoDB.
- Create a function for scanning attendance:
  - Receive an image from the web app.
  - Search for a match using Rekognition.
  - If matched, record attendance in DynamoDB.
- Create a function for retrieving attendance records for the admin panel.

### 5. API Gateway Configuration
- Create REST API resources and methods.
- Configure CORS settings to allow frontend access.
- Integrate API Gateway with Lambda functions.

### 6. Web Frontend Setup
- Develop a web page for employee scanning using JavaScript and HTML.
- Implement a camera feature to capture employee images.
- Integrate API calls for scanning and recording attendance.
- Develop an admin panel to:
  - Register employees.
  - View attendance logs.

### 7. CloudFront Configuration
- Set up CloudFront distribution for frontend hosting.
- Configure the origin to point to the S3 static website bucket.
- Enable necessary caching and security settings.

---

## Features
- **Serverless Architecture:** Uses AWS Lambda, API Gateway, S3, DynamoDB, and Rekognition.
- **Face Recognition-Based Attendance:** Matches employee faces using Rekognition.
- **Admin Panel:** Allows employee registration and attendance tracking.
- **Scalable and Secure:** Uses AWS services for a fully managed solution.
- **CloudFront CDN:** Ensures fast and secure access to the web application.

---

## Future Enhancements
- Implement authentication for admin access.
- Add mobile support for attendance marking.
- Integrate notifications for attendance updates.

---

## Technologies Used
- **Frontend:** HTML, JavaScript, CloudFront
- **Backend:** AWS Lambda, API Gateway, DynamoDB
- **Storage & Recognition:** Amazon S3, Amazon Rekognition

