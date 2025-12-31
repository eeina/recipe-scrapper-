"""
S3 Upload Utility for Recipe Scraper
Handles uploading images from URLs to AWS S3
"""

import os
import logging
import requests
import boto3
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, Optional
import mimetypes

logger = logging.getLogger(__name__)


# Initialize S3 client
def get_s3_client():
    """Create and return S3 client with credentials from environment"""
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    if not aws_access_key or not aws_secret_key:
        logger.warning("AWS credentials not configured")
        return None

    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )
        logger.debug("S3 client initialized successfully")
        return s3_client
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {str(e)}")
        return None


def generate_unique_filename(extension: str = "") -> str:
    """Generate a unique filename with timestamp and random hex"""
    timestamp = int(datetime.now().timestamp() * 1000)
    hex_timestamp = hex(timestamp)[2:]
    import random

    random_hex = hex(random.randint(0, 0xFFFFF))[2:].zfill(5)

    if extension:
        return f"{hex_timestamp}-{random_hex}.{extension}"
    return f"{hex_timestamp}-{random_hex}"


def get_extension_from_url(url: str, content_type: Optional[str] = None) -> str:
    """Extract file extension from URL or content type"""
    # Allowed image formats
    ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "webp", "gif", "svg"]

    # Try to get extension from URL
    parsed_url = urlparse(url)
    path = parsed_url.path
    if "." in path:
        ext = path.split(".")[-1].lower()
        if ext in ALLOWED_EXTENSIONS:
            return ext

    # Try to get from content type
    if content_type:
        ext = mimetypes.guess_extension(content_type)
        if ext:
            ext = ext.lstrip(".")
            if ext == "jpe":
                ext = "jpg"
            if ext in ALLOWED_EXTENSIONS:
                return ext

    # Default to jpg
    return "jpg"


def upload_image_from_url(
    image_url: str, s3_client=None, bucket_name: str = None
) -> Dict[str, str]:
    """
    Download image from URL and upload to S3

    Args:
        image_url: URL of the image to upload
        s3_client: Boto3 S3 client (optional, will create if not provided)
        bucket_name: S3 bucket name (optional, will read from env if not provided)

    Returns:
        Dict with success status, url, and key
        {
            "success": True,
            "url": "https://bucket.s3.region.amazonaws.com/key",
            "key": "uploads/scraper/filename.jpg"
        }
    """
    if not image_url:
        logger.warning("No image URL provided")
        return {"success": False, "url": "", "key": ""}

    # Initialize S3 client if not provided
    if not s3_client:
        s3_client = get_s3_client()

    if not s3_client:
        logger.warning("S3 client not available, returning original URL")
        return {"success": False, "url": image_url, "key": ""}

    # Get bucket name
    if not bucket_name:
        bucket_name = os.getenv("AWS_BUCKET_NAME")

    if not bucket_name:
        logger.error("AWS_BUCKET_NAME not configured")
        return {"success": False, "url": image_url, "key": ""}

    try:
        logger.debug(f"Downloading image from URL: {image_url}")

        # Download image
        response = requests.get(
            image_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            timeout=30,
            stream=True,
        )
        response.raise_for_status()

        # Get content type and extension
        content_type = response.headers.get("Content-Type", "image/jpeg")
        extension = get_extension_from_url(image_url, content_type)

        # Generate unique filename
        filename = generate_unique_filename(extension)
        key = f"uploads/scraper/{filename}"

        logger.debug(f"Uploading to S3: bucket={bucket_name}, key={key}")

        # Upload to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=response.content,
            ContentType=content_type,
            ACL="public-read",
        )

        # Construct URL
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        s3_url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{key}"

        logger.info(f"Successfully uploaded image to S3: {key}")

        return {"success": True, "url": s3_url, "key": key}

    except requests.RequestException as e:
        logger.error(f"Failed to download image from URL: {str(e)}")
        return {"success": False, "url": image_url, "key": ""}

    except Exception as e:
        logger.error(f"Failed to upload image to S3: {str(e)}")
        return {"success": False, "url": image_url, "key": ""}


def upload_image_if_configured(image_url: str) -> Dict[str, str]:
    """
    Wrapper function that uploads image to S3 if configured,
    otherwise returns original URL

    Returns:
        Dict with url and key:
        {
            "url": "https://s3.url or original url",
            "key": "s3-key or empty string"
        }
    """
    if not image_url:
        return {"url": "", "key": ""}

    result = upload_image_from_url(image_url)

    if result["success"]:
        return {"url": result["url"], "key": result["key"]}
    else:
        # If upload failed, return original URL
        return {"url": image_url, "key": ""}
