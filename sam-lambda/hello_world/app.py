import base64
import boto3
import json
import random
import os

def lambda_handler(event, context):
    if event['httpMethod'] != "POST":
        return generate_response(404, "Invalid request method")
    
    request = json.loads(event['body'])
    
    generate_image(request['prompt'])

    return generate_response(200, "Image generated successfully and uploaded to S3")

def generate_response(response_code, message):
    return {
        "statusCode": response_code,
        "body": message,
        "headers": { 
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            "Access-Control-Allow-Methods": "POST" 
        }
    }
    

def generate_image(prompt):
    # Set up the AWS clients

    bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
    s3_client = boto3.client("s3")

    # Define the model ID and S3 bucket name (replace with your actual bucket name)
    model_id = "amazon.titan-image-generator-v1"

    seed = random.randint(0, 2147483647)
    s3_image_path = f"generated_images/titan_{seed}.png"

    native_request = {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": prompt},
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "quality": "standard",
            "cfgScale": 8.0,
            "height": 1024,
            "width": 1024,
            "seed": seed,
        }
    }

    response = bedrock_client.invoke_model(modelId=model_id, body=json.dumps(native_request))
    model_response = json.loads(response["body"].read())

    # Extract and decode the Base64 image data
    base64_image_data = model_response["images"][0]
    image_data = base64.b64decode(base64_image_data)

    # Upload the decoded image data to S3
    s3_client.put_object(Bucket=os.environ["BUCKET_NAME"], Key=s3_image_path, Body=image_data)