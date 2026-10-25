"""로컬 폴더와 클라우드 버킷을 같은 방식으로 읽고 쓰기 위한 얇은 추상화."""
import json
import os

from . import config


def _is_gcs(root):
    return root.startswith("gs://")


def _split_gcs(root, rel):
    path = root[len("gs://"):].rstrip("/")
    bucket, _, prefix = path.partition("/")
    return bucket, f"{prefix}/{rel}" if prefix else rel


def write_json(rel, obj, root=None):
    root = root or config.STORAGE_ROOT
    text = json.dumps(obj, ensure_ascii=False, default=str)
    if _is_gcs(root):
        from google.cloud import storage
        bucket, blob = _split_gcs(root, rel)
        storage.Client().bucket(bucket).blob(blob).upload_from_string(text, content_type="application/json")
        return
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def read_json(rel, root=None):
    root = root or config.STORAGE_ROOT
    if _is_gcs(root):
        from google.cloud import storage
        bucket, blob = _split_gcs(root, rel)
        return json.loads(storage.Client().bucket(bucket).blob(blob).download_as_text())
    with open(os.path.join(root, rel), encoding="utf-8") as f:
        return json.load(f)


def exists(rel, root=None):
    root = root or config.STORAGE_ROOT
    if _is_gcs(root):
        from google.cloud import storage
        bucket, blob = _split_gcs(root, rel)
        return storage.Client().bucket(bucket).blob(blob).exists()
    return os.path.exists(os.path.join(root, rel))


def list_dates(prefix, root=None):
    """prefix 폴더 안의 YYYYMMDD.json 파일명에서 날짜 목록을 돌려준다."""
    root = root or config.STORAGE_ROOT
    if _is_gcs(root):
        from google.cloud import storage
        bucket, blob_prefix = _split_gcs(root, prefix)
        names = [b.name.rsplit("/", 1)[-1] for b in storage.Client().list_blobs(bucket, prefix=blob_prefix)]
    else:
        folder = os.path.join(root, prefix)
        names = os.listdir(folder) if os.path.isdir(folder) else []
    return sorted(n[:8] for n in names if n.endswith(".json") and n[:8].isdigit())
