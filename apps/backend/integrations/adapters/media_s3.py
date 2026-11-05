"""Storage S3 compatível: bucket privado, sempre por URL assinada."""

from __future__ import annotations

from functools import cached_property

from django.conf import settings

from integrations.ports import MediaStoragePort


class S3MediaAdapter(MediaStoragePort):
    @cached_property
    def _client(self):
        import boto3
        from botocore.config import Config

        return boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL or None,
            region_name=settings.AWS_S3_REGION_NAME or None,
            config=Config(signature_version="s3v4"),
        )

    @property
    def _bucket(self) -> str:
        return settings.AWS_STORAGE_BUCKET_NAME

    def put(self, *, key: str, data: bytes, content_type: str) -> None:
        self._client.put_object(Bucket=self._bucket, Key=key, Body=data, ContentType=content_type)

    def get(self, *, key: str) -> bytes | None:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
        except self._client.exceptions.NoSuchKey:
            return None
        return response["Body"].read()

    def delete(self, *, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)

    def signed_url(self, *, key: str, ttl_seconds: int, content_type: str = "") -> str:
        return self._client.generate_presigned_url(
            "get_object", Params={"Bucket": self._bucket, "Key": key}, ExpiresIn=ttl_seconds
        )
