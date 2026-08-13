#!/usr/bin/env python3
"""검증된 외부 데이터 산출물을 Azure Blob immutable snapshot으로 발행한다.

인증은 ``DefaultAzureCredential``을 사용한다. GitHub Actions에서는 OIDC 로그인, Azure ML에서는
managed identity를 사용하며 장기 account key/connection string을 코드에 넣지 않는다. 모든 파일을
임시 prefix에 업로드·검증한 뒤 ``_SUCCESS.json``을 마지막에 기록하므로 불완전 snapshot은 소비되지
않는다.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_ALLOWED_ROOTS = (Path("data/gold"), Path("reports/market"), Path("reports/pipeline"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_metadata(path: Path) -> dict[str, Any]:
    try:
        relative = path.relative_to(Path.cwd().resolve())
    except ValueError:
        relative = Path(path.name)
    metadata: dict[str, Any] = {
        "path": relative.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }
    if path.suffix.lower() == ".parquet":
        frame = pd.read_parquet(path)
        metadata["rows"] = len(frame)
        metadata["columns"] = [str(column) for column in frame.columns]
    return metadata


def _validated_files(raw_paths: list[str]) -> list[Path]:
    files = [Path(raw).resolve() for raw in raw_paths]
    roots = [root.resolve() for root in DEFAULT_ALLOWED_ROOTS]
    for path in files:
        if not path.is_file():
            raise FileNotFoundError(f"[오류] 업로드 파일 없음: {path}")
        if not any(path.is_relative_to(root) for root in roots):
            raise ValueError(
                f"[오류] 허용되지 않은 업로드 경로: {path}. "
                f"허용 루트: {[str(root) for root in roots]}")
    return sorted(set(files))


def build_manifest(files: list[Path], snapshot_id: str) -> dict[str, Any]:
    """snapshot manifest를 생성한다. 비밀정보·계정명은 포함하지 않는다."""
    return {
        "schema_version": "1.0",
        "snapshot_id": snapshot_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_commit": os.environ.get("GITHUB_SHA", "local"),
        "source_run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "files": [_file_metadata(path) for path in files],
    }


def publish(
    account_url: str,
    container: str,
    prefix: str,
    files: list[Path],
    manifest: dict[str, Any],
) -> None:
    """파일을 임시 prefix에 업로드하고 해시를 확인한 뒤 성공 marker를 기록한다."""
    try:
        from azure.identity import DefaultAzureCredential
        from azure.storage.blob import BlobServiceClient
    except ImportError as exc:
        raise RuntimeError(
            "[오류] Azure Blob 의존성이 없습니다. Actions 환경 의존성 단계를 확인하세요.") from exc

    service = BlobServiceClient(account_url=account_url, credential=DefaultAzureCredential())
    client = service.get_container_client(container)
    snapshot_prefix = f"{prefix.rstrip('/')}/{manifest['snapshot_id']}"

    for path, metadata in zip(files, manifest["files"]):
        blob_name = f"{snapshot_prefix}/{metadata['path']}"
        metadata["blob_name"] = blob_name
        with path.open("rb") as stream:
            client.upload_blob(name=blob_name, data=stream, overwrite=False)
        downloaded = client.download_blob(blob_name).readall()
        if hashlib.sha256(downloaded).hexdigest() != metadata["sha256"]:
            raise RuntimeError(f"[오류] 업로드 해시 불일치: {path}")

    manifest_bytes = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
    client.upload_blob(
        name=f"{snapshot_prefix}/_SUCCESS.json", data=manifest_bytes, overwrite=False
    )
    print(f"[완료] Azure Blob snapshot 발행: {manifest['snapshot_id']} · {len(files)}개 파일")


def main() -> int:
    parser = argparse.ArgumentParser(description="Azure Blob immutable snapshot 발행")
    parser.add_argument("paths", nargs="+", help="data/gold 또는 reports 하위 검증 산출물")
    parser.add_argument("--dry-run", action="store_true", help="manifest만 검증하고 업로드하지 않음")
    parser.add_argument("--snapshot-id", default=os.environ.get("NEXUS_SNAPSHOT_ID", ""))
    args = parser.parse_args()

    files = _validated_files(args.paths)
    snapshot_id = args.snapshot_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    manifest = build_manifest(files, snapshot_id)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    if args.dry_run:
        return 0

    account_url = os.environ.get("AZURE_STORAGE_ACCOUNT_URL", "").strip()
    container = os.environ.get("AZURE_STORAGE_CONTAINER", "").strip()
    prefix = os.environ.get("AZURE_STORAGE_PREFIX", "nexus/model-ready").strip()
    if not account_url or not container:
        raise RuntimeError(
            "[오류] AZURE_STORAGE_ACCOUNT_URL/AZURE_STORAGE_CONTAINER가 필요합니다.")
    publish(account_url, container, prefix, files, manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
