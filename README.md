# Rekognition_Project# AWS Rekognition Image Labeling Pipeline (Automated with GitHub Actions + CloudFormation)

This project demonstrates an end-to-end, automated image labeling pipeline using **Amazon Rekognition**, **AWS Lambda**, **DynamoDB**, and **S3**, fully provisioned via **CloudFormation** and deployed through **GitHub Actions** workflows. Images uploaded to S3 automatically trigger a Lambda function that runs Rekognition to detect labels and logs results into the appropriate DynamoDB table (Beta or Prod).  

---

## Project Setup and Usage

1. **Set Up Required AWS Resources**
   - **S3 Buckets:** Create two S3 buckets (or prefixes) for images and Lambda code. One for Beta, one for Prod. These buckets will store both your deployment artifacts (Lambda `.zip` file) and uploaded images to be analyzed.
   - **Rekognition:** No explicit provisioning is needed—Rekognition is available as a managed AWS service, but ensure your Lambda execution role has permissions for `rekognition:DetectLabels`.
   - **DynamoDB Tables:** Create two DynamoDB tables (one for Beta, one for Prod) via CloudFormation. Each table should have a primary key such as `ImageKey` (string) to store object keys from S3. Rekognition label data will be logged here.

2. **Configure GitHub Secrets**
   - Store the following secrets in your repository:
     - `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_REGION` → credentials for GitHub Actions to deploy.
     - `CF_STACK_NAME_BETA` / `CF_STACK_NAME_PROD` → stack names for each environment.
     - `S3_BUCKET_BETA` / `S3_BUCKET_PROD` → names of your buckets.
     - `S3_PATH_BETA` / `S3_PATH_PROD` → paths/prefixes for storing Lambda deployment packages.
     - `LAMBDA_NAME_BETA` / `LAMBDA_NAME_PROD` → logical names of your Lambda functions.
     - `DYNAMODB_TABLE_NAME_BETA` / `DYNAMODB_TABLE_NAME_PROD` → DynamoDB table names.

3. **Add and Analyze New Images**
   - Upload images into the correct S3 bucket/prefix (Beta or Prod).
   - Each upload triggers an event notification to the environment’s Lambda function.
   - The Lambda retrieves the image, runs Rekognition `detect_labels`, and writes results (labels, confidence scores, timestamps) into the matching DynamoDB table.

4. **Verify Data Logging in DynamoDB**
   - Open the **DynamoDB console** for your chosen environment’s table.
   - Query by the `ImageKey` (or primary key you defined) to see the latest entries.
   - Each record should contain:
     - **Image metadata** (bucket name, key).
     - **Rekognition label results** with confidence scores.
     - **Timestamps** for when the analysis was triggered.
   - You can also monitor **CloudWatch Logs** for the Lambda function to verify execution details, errors, or debug output.

---

This README covers the entire flow: from provisioning AWS resources, configuring GitHub secrets, and uploading new images, to verifying that Rekognition outputs are correctly logged in DynamoDB.  