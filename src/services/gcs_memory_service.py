# agent/services/gcs_memory_service.py
import os
import json
from google.cloud import storage
from typing import Dict, Any, List

class GCSMemoryService:
    """
    A simple GCS-backed memory service. Stores one JSON file per user:
    gs://{bucket}/{prefix}{user_id}.json
    """

    def __init__(self, bucket_name: str, prefix: str = "babybrain_memory/"):
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def _blob(self, user_id: str):
        return self.bucket.blob(f"{self.prefix}{user_id}.json")

    def _load(self, user_id: str) -> Dict[str, Any]:
        b = self._blob(user_id)
        if not b.exists():
            base = {"family_profile": {"parent_name": None, "kids": []}, "sitters": []}
            b.upload_from_string(json.dumps(base), content_type="application/json")
            return base
        return json.loads(b.download_as_text())

    def _save(self, user_id: str, data: Dict[str, Any]):
        self._blob(user_id).upload_from_string(json.dumps(data, indent=2), content_type="application/json")

    def get_family_profile(self, user_id: str) -> Dict[str, Any]:
        data = self._load(user_id)
        return data.get("family_profile", {"parent_name": None, "kids": []})

    def add_sitter(self, user_id: str, sitter: Dict[str, str]) -> List[Dict[str, str]]:
        data = self._load(user_id)
        data.setdefault("sitters", [])
        if not any(s.get("name")==sitter.get("name") and s.get("phone")==sitter.get("phone") for s in data["sitters"]):
            data["sitters"].append(sitter)
            self._save(user_id, data)
        return data["sitters"]

    def get_sitters(self, user_id: str) -> List[Dict[str, str]]:
        data = self._load(user_id)
        return data.get("sitters", [])
