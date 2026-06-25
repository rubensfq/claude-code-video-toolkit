"""Shared file transfer helpers for cloud GPU tools.

Provides R2 upload/download. Cloudflare R2 is required — cloud GPU tools will
raise RuntimeError if R2 is not configured rather than falling back to public
file hosting services.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def get_r2_client():
    """Get boto3 S3 client configured for Cloudflare R2.

    Returns (client, config_dict) or (None, None) if R2 is not configured.
    """
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from config import get_r2_config
        r2_config = get_r2_config()
    except ImportError:
        r2_config = None

    if not r2_config:
        return None, None

    try:
        import boto3
        from botocore.config import Config

        client = boto3.client(
            "s3",
            endpoint_url=r2_config["endpoint_url"],
            aws_access_key_id=r2_config["access_key_id"],
            aws_secret_access_key=r2_config["secret_access_key"],
            region_name="auto",
            config=Config(signature_version="s3v4"),
        )
        return client, r2_config
    except ImportError:
        print("  boto3 not installed, skipping R2", file=sys.stderr)
        return None, None


def upload_to_r2(file_path: str, prefix: str) -> tuple[str | None, str | None]:
    """Upload to Cloudflare R2 and return presigned download URL.

    Returns (presigned_url, object_key) or (None, None) on failure.
    """
    client, config = get_r2_client()
    if not client:
        return None, None

    import uuid
    file_name = Path(file_path).name
    object_key = f"{prefix}/{uuid.uuid4().hex[:8]}_{file_name}"

    try:
        client.upload_file(file_path, config["bucket_name"], object_key)

        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": config["bucket_name"], "Key": object_key},
            ExpiresIn=7200,
        )
        return url, object_key
    except Exception as e:
        print(f"  R2 upload error: {e}", file=sys.stderr)
        return None, None


def download_from_r2(object_key: str, output_path: str) -> bool:
    """Download object from R2 to local path."""
    client, config = get_r2_client()
    if not client:
        return False

    try:
        client.download_file(config["bucket_name"], object_key, output_path)
        return True
    except Exception as e:
        print(f"  R2 download error: {e}", file=sys.stderr)
        return False


def delete_from_r2(object_key: str) -> bool:
    """Delete object from R2 after job completion."""
    client, config = get_r2_client()
    if not client or not object_key:
        return False

    try:
        client.delete_object(Bucket=config["bucket_name"], Key=object_key)
        return True
    except Exception:
        return False


def upload_to_storage(file_path: str, prefix: str) -> tuple[str | None, str | None]:
    """Upload a file to private R2 storage for cloud GPU job input.

    Requires R2 to be configured via R2_ENDPOINT_URL, R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY, and R2_BUCKET_NAME in .env. Cloud GPU jobs must not
    upload files to public third-party services.

    Returns (presigned_url, r2_key) on success. Raises RuntimeError if R2 is
    not configured — configure R2 before using cloud GPU tools.
    """
    client, config = get_r2_client()
    if not client:
        raise RuntimeError(
            "R2 storage is required for cloud GPU tools but is not configured.\n"
            "Add these to your .env file:\n"
            "  R2_ENDPOINT_URL=https://<account>.r2.cloudflarestorage.com\n"
            "  R2_ACCESS_KEY_ID=<key>\n"
            "  R2_SECRET_ACCESS_KEY=<secret>\n"
            "  R2_BUCKET_NAME=<bucket>\n"
            "See docs/setup.md for Cloudflare R2 setup instructions."
        )

    file_size = Path(file_path).stat().st_size
    file_name = Path(file_path).name

    print(f"Uploading {file_name} ({file_size // 1024}KB) to R2...", file=sys.stderr)

    url, r2_key = upload_to_r2(file_path, prefix)
    if url:
        print(f"  Upload complete (R2)", file=sys.stderr)
        return url, r2_key

    raise RuntimeError(f"R2 upload failed for {file_name}. Check R2 credentials and bucket permissions.")


def download_from_url(url: str, output_path: str, verbose: bool = True) -> bool:
    """Download file from URL to local path with streaming."""
    import requests

    try:
        if verbose:
            print(f"Downloading result...", file=sys.stderr)

        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        if verbose:
            size_kb = Path(output_path).stat().st_size // 1024
            print(f"  Downloaded: {output_path} ({size_kb}KB)", file=sys.stderr)

        return True

    except Exception as e:
        print(f"Download error: {e}", file=sys.stderr)
        return False


def get_r2_payload_config() -> dict | None:
    """Get R2 config dict for embedding in cloud GPU job payloads.

    Returns the dict to include as payload["input"]["r2"], or None if R2
    is not configured. This is the format expected by RunPod/Modal handlers.
    """
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from config import get_r2_config
        r2_config = get_r2_config()
    except ImportError:
        r2_config = None

    if not r2_config:
        return None

    return {
        "endpoint_url": r2_config["endpoint_url"],
        "access_key_id": r2_config["access_key_id"],
        "secret_access_key": r2_config["secret_access_key"],
        "bucket_name": r2_config["bucket_name"],
    }
