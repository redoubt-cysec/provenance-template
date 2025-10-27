import hashlib
import json
from pathlib import Path

from src.demo_cli.verify import Verifier


def _write_binary(tmp_path: Path, content: bytes = b"sample-binary") -> Path:
    binary = tmp_path / "demo.bin"
    binary.write_bytes(content)
    return binary


def test_verify_checksum_requires_manifest(tmp_path):
    binary = _write_binary(tmp_path)

    verifier = Verifier(binary)
    result = verifier.verify_checksum()

    assert not result.passed
    assert "manifest" in result.message.lower()


def test_verify_checksum_matches_manifest(tmp_path):
    content = b"release-binary"
    binary = _write_binary(tmp_path, content)
    checksum = hashlib.sha256(content).hexdigest()

    manifest = tmp_path / "checksums.txt"
    manifest.write_text(f"{checksum}  {binary.name}\n", encoding="utf-8")

    verifier = Verifier(binary)
    result = verifier.verify_checksum()

    assert result.passed
    assert checksum[:8] in result.details


def test_slsa_provenance_validates_subject_digest(tmp_path):
    content = b"signed binary"
    binary = _write_binary(tmp_path, content)
    checksum = hashlib.sha256(content).hexdigest()

    attestation = {
        "subject": [{"name": binary.name, "digest": {"sha256": checksum}}],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {"builder": {"id": "builder://unit-test"}, "buildType": "unit-test"},
    }
    (tmp_path / "attestation.jsonl").write_text(json.dumps(attestation) + "\n", encoding="utf-8")

    verifier = Verifier(binary)
    result = verifier.verify_slsa_provenance()

    assert result.passed
    assert "builder://unit-test" in result.details


def test_reproducible_build_requires_source_date_epoch(tmp_path):
    binary = _write_binary(tmp_path)

    verifier = Verifier(binary)
    result = verifier.verify_reproducible_build()

    assert not result.passed
    assert "source_date_epoch" in result.message.lower()


def test_reproducible_build_reads_metadata(tmp_path):
    binary = _write_binary(tmp_path)
    metadata = tmp_path / "build-metadata.json"
    metadata.write_text(json.dumps({"SOURCE_DATE_EPOCH": "1700000000"}), encoding="utf-8")

    verifier = Verifier(binary)
    result = verifier.verify_reproducible_build()

    assert result.passed
    assert "1700000000" in result.details
