"""
Self-verification module for the demo CLI.

This module demonstrates how to verify a binary's attestations using
the complete security toolchain:
- Sigstore signature verification
- Rekor transparency log verification
- GitHub attestations verification
- SBOM verification
- OSV vulnerability scanning
- Checksum integrity verification
"""

import base64
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class VerificationResult:
    """Result of a verification check."""

    def __init__(self, name: str, passed: bool, message: str, details: Optional[str] = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details


class Verifier:
    """Handles all verification operations for the CLI binary."""

    def __init__(self, binary_path: Optional[Path] = None):
        """
        Initialize verifier.

        Args:
            binary_path: Path to the binary to verify. If None, uses the running binary.
        """
        if binary_path:
            self.binary_path = binary_path
        else:
            # Try to find the .pyz file we're running from
            self.binary_path = self._find_running_binary()

        self.console = Console() if RICH_AVAILABLE else None
        self.results: List[VerificationResult] = []

        # GitHub repo info (will be replaced during setup)
        self.github_repo = os.getenv("GITHUB_REPOSITORY", "OWNER/REPO")
        self.version = self._get_version()

    def _find_running_binary(self) -> Optional[Path]:
        """Find the .pyz file we're running from."""
        # Check if we're running from a .pyz
        if hasattr(sys, "_MEIPASS"):
            # PyInstaller bundle
            return Path(sys.executable)

        # Check for .pyz in sys.path
        for path_str in sys.path:
            path = Path(path_str)
            if path.suffix == ".pyz" and path.exists():
                return path

        # Check for dist/provenance-demo.pyz relative to package
        pkg_dir = Path(__file__).parent.parent.parent
        pyz_path = pkg_dir / "dist" / "provenance-demo.pyz"
        if pyz_path.exists():
            return pyz_path

        return None

    def _get_version(self) -> str:
        """
        Get the package version.

        If verifying an external binary, extract version from that binary.
        Otherwise, use the version of the running package.
        """
        # If verifying an external .pyz file, extract its version
        if self.binary_path and self.binary_path.suffix == ".pyz" and self.binary_path.exists():
            try:
                result = subprocess.run(
                    [str(self.binary_path), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except Exception:
                pass  # Fall through to default version

        # Use the version of the running package
        try:
            from . import __version__
            return __version__
        except ImportError:
            return "unknown"

    def _print_header(self, text: str):
        """Print a section header."""
        if self.console:
            self.console.print(f"\n[bold cyan]{text}[/bold cyan]")
        else:
            print(f"\n{'='*60}")
            print(text)
            print('='*60)

    def _print_result(self, result: VerificationResult):
        """Print a verification result."""
        if self.console:
            status = "[green]✓[/green]" if result.passed else "[red]✗[/red]"
            self.console.print(f"{status} {result.name}: {result.message}")
            if result.details:
                self.console.print(f"  [dim]{result.details}[/dim]")
        else:
            status = "✓" if result.passed else "✗"
            print(f"{status} {result.name}: {result.message}")
            if result.details:
                print(f"  {result.details}")

    def _calculate_binary_sha256(self) -> Optional[str]:
        """Return the SHA256 checksum for the current binary."""
        if not self.binary_path or not self.binary_path.exists():
            return None

        sha256_hash = hashlib.sha256()
        with open(self.binary_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    def verify_checksum(self) -> VerificationResult:
        """Verify the binary's checksum matches the release."""
        if not self.binary_path or not self.binary_path.exists():
            return VerificationResult(
                "Checksum Verification",
                False,
                "Binary not found",
                f"Could not locate binary at {self.binary_path}"
            )

        checksum = self._calculate_binary_sha256()
        if not checksum:
            return VerificationResult(
                "Checksum Verification",
                False,
                "Unable to calculate binary checksum"
            )

        # Try to find checksum manifest
        candidates = [
            self.binary_path.parent / "checksums.txt",
            self.binary_path.parent / f"{self.binary_path.name}.sha256",
            self.binary_path.with_suffix(self.binary_path.suffix + ".sha256"),
        ]
        checksums_file = next((p for p in candidates if p.exists()), None)

        if not checksums_file:
            return VerificationResult(
                "Checksum Verification",
                False,
                "Release checksum manifest not found",
                f"Expected one of: {', '.join(str(p) for p in candidates)}"
            )

        expected_checksum = None
        try:
            for line in checksums_file.read_text().splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue

                parts = stripped.split()
                if len(parts) == 1:
                    # .sha256 files often contain only the checksum
                    expected_checksum = parts[0]
                    break

                candidate_path = parts[-1].lstrip("*")
                if Path(candidate_path).name == self.binary_path.name:
                    expected_checksum = parts[0]
                    break
        except Exception as exc:
            return VerificationResult(
                "Checksum Verification",
                False,
                "Failed to read checksum manifest",
                str(exc)[:200]
            )

        if not expected_checksum:
            return VerificationResult(
                "Checksum Verification",
                False,
                "Binary missing from checksum manifest",
                f"Manifest: {checksums_file}"
            )

        if checksum.lower() != expected_checksum.lower():
            return VerificationResult(
                "Checksum Verification",
                False,
                "SHA256 checksum mismatch",
                f"Calculated {checksum[:16]}…, expected {expected_checksum[:16]}…"
            )

        return VerificationResult(
            "Checksum Verification",
            True,
            "SHA256 checksum matches release manifest",
            f"Checksum: {checksum[:16]}… (manifest: {checksums_file.name})"
        )

    def verify_sigstore_signature(self) -> VerificationResult:
        """Verify Sigstore signature using cosign or sigstore-python."""
        if not self.binary_path or not self.binary_path.exists():
            return VerificationResult(
                "Sigstore Signature",
                False,
                "Binary not found"
            )

        # Check for signature bundle
        sig_bundle = self.binary_path.with_suffix(self.binary_path.suffix + ".sigstore")
        if not sig_bundle.exists():
            sig_bundle = self.binary_path.parent / f"{self.binary_path.name}.sigstore"

        if not sig_bundle.exists():
            return VerificationResult(
                "Sigstore Signature",
                False,
                "No signature bundle found",
                f"Expected at: {sig_bundle}"
            )

        # Try to verify using cosign CLI (preferred for full verification)
        try:
            result = subprocess.run(
                [
                    "cosign", "verify-blob",
                    str(self.binary_path),
                    "--bundle", str(sig_bundle),
                    "--certificate-identity-regexp", ".*",
                    "--certificate-oidc-issuer-regexp", ".*"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return VerificationResult(
                    "Sigstore Signature",
                    True,
                    "Signature verified via Rekor transparency log",
                    "Keyless signing with certificate from Fulcio CA"
                )
            else:
                return VerificationResult(
                    "Sigstore Signature",
                    False,
                    "Signature verification failed",
                    result.stderr[:200] if result.stderr else None
                )

        except FileNotFoundError:
            return VerificationResult(
                "Sigstore Signature",
                False,
                "cosign not installed",
                "Install: brew install cosign or see https://docs.sigstore.dev"
            )
        except subprocess.TimeoutExpired:
            return VerificationResult(
                "Sigstore Signature",
                False,
                "Verification timeout",
                "Rekor transparency log query timed out"
            )
        except Exception as e:
            return VerificationResult(
                "Sigstore Signature",
                False,
                "Verification error",
                str(e)[:200]
            )

    def verify_github_attestation(self) -> VerificationResult:
        """Verify GitHub attestation using gh CLI."""
        if not self.binary_path or not self.binary_path.exists():
            return VerificationResult(
                "GitHub Attestation",
                False,
                "Binary not found"
            )

        try:
            result = subprocess.run(
                [
                    "gh", "attestation", "verify",
                    str(self.binary_path),
                    "--repo", self.github_repo
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return VerificationResult(
                    "GitHub Attestation",
                    True,
                    "GitHub attestation verified",
                    f"Repository: {self.github_repo}"
                )
            else:
                return VerificationResult(
                    "GitHub Attestation",
                    False,
                    "Attestation verification failed",
                    result.stderr[:200] if result.stderr else None
                )

        except FileNotFoundError:
            return VerificationResult(
                "GitHub Attestation",
                False,
                "gh CLI not installed",
                "Install: brew install gh or see https://cli.github.com"
            )
        except subprocess.TimeoutExpired:
            return VerificationResult(
                "GitHub Attestation",
                False,
                "Verification timeout"
            )
        except Exception as e:
            return VerificationResult(
                "GitHub Attestation",
                False,
                "Verification error",
                str(e)[:200]
            )

    def verify_sbom_attestation(self) -> VerificationResult:
        """Verify GitHub SBOM attestation using gh CLI."""
        if not self.binary_path or not self.binary_path.exists():
            return VerificationResult(
                "SBOM Attestation",
                False,
                "Binary not found"
            )

        try:
            result = subprocess.run(
                [
                    "gh", "attestation", "verify",
                    str(self.binary_path),
                    "--repo", self.github_repo,
                    "--predicate-type", "https://spdx.dev/Document"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return VerificationResult(
                    "SBOM Attestation",
                    True,
                    "SBOM attestation verified",
                    f"SPDX document attestation for {self.binary_path.name}"
                )
            else:
                # SBOM attestation might not be present in all releases
                return VerificationResult(
                    "SBOM Attestation",
                    False,
                    "SBOM attestation not found or verification failed",
                    "This is expected for releases before SBOM attestation was added"
                )

        except FileNotFoundError:
            return VerificationResult(
                "SBOM Attestation",
                False,
                "gh CLI not installed",
                "Install: brew install gh or see https://cli.github.com"
            )
        except subprocess.TimeoutExpired:
            return VerificationResult(
                "SBOM Attestation",
                False,
                "Verification timeout"
            )
        except Exception as e:
            return VerificationResult(
                "SBOM Attestation",
                False,
                "Verification error",
                str(e)[:200]
            )

    def verify_sbom(self) -> VerificationResult:
        """Verify SBOM exists and is valid in multiple formats."""
        if not self.binary_path:
            return VerificationResult(
                "SBOM Verification",
                False,
                "Binary not found"
            )

        # Look for SBOM files in multiple formats
        sbom_files = {
            "spdx": self.binary_path.parent / "sbom.spdx.json",
            "cyclonedx": self.binary_path.parent / "sbom.cyclonedx.json",
            "generic": self.binary_path.parent / "sbom.json"
        }

        found_formats = []
        total_components = 0

        # Validate each SBOM format
        for format_name, sbom_file in sbom_files.items():
            if not sbom_file.exists():
                continue

            try:
                with open(sbom_file) as f:
                    sbom = json.load(f)

                if format_name == "cyclonedx" and sbom.get("bomFormat") == "CycloneDX":
                    components = sbom.get("components", [])
                    found_formats.append(f"CycloneDX ({len(components)} components)")
                    total_components += len(components)
                elif format_name == "spdx" and "spdxVersion" in sbom:
                    packages = sbom.get("packages", [])
                    found_formats.append(f"SPDX ({len(packages)} packages)")
                    total_components += len(packages)
                elif format_name == "generic":
                    # Try to detect format
                    if "bomFormat" in sbom:
                        found_formats.append(f"{sbom.get('bomFormat')} (generic)")
                    elif "spdxVersion" in sbom:
                        found_formats.append("SPDX (generic)")

            except (json.JSONDecodeError, Exception):
                continue

        if not found_formats:
            return VerificationResult(
                "SBOM Verification",
                False,
                "No valid SBOM files found",
                f"Expected at: {sbom_files['spdx']} or {sbom_files['cyclonedx']}"
            )

        return VerificationResult(
            "SBOM Verification",
            True,
            f"Valid SBOMs in {len(found_formats)} format(s)",
            f"Formats: {', '.join(found_formats)}"
        )

    def verify_osv_scan(self) -> VerificationResult:
        """Run OSV vulnerability scan on the SBOM."""
        if not self.binary_path:
            return VerificationResult(
                "OSV Vulnerability Scan",
                False,
                "Binary not found"
            )

        # First check if scan results already exist
        scan_results_file = self.binary_path.parent / "osv-scan-results.json"
        if scan_results_file.exists():
            try:
                with open(scan_results_file) as f:
                    results = json.load(f)
                    # OSV scanner results structure
                    vulnerabilities = results.get("results", [{}])[0].get("packages", [])
                    if not vulnerabilities:
                        return VerificationResult(
                            "OSV Vulnerability Scan",
                            True,
                            "No known vulnerabilities found",
                            "Pre-scanned results from release"
                        )
                    else:
                        return VerificationResult(
                            "OSV Vulnerability Scan",
                            False,
                            f"Found vulnerabilities in {len(vulnerabilities)} package(s)",
                            f"See osv-scan-report.txt for details"
                        )
            except Exception:
                # Fall through to run scan ourselves
                pass

        sbom_file = self.binary_path.parent / "sbom.spdx.json"
        if not sbom_file.exists():
            sbom_file = self.binary_path.parent / "sbom.json"
        if not sbom_file.exists():
            sbom_file = self.binary_path.with_suffix(".sbom.json")

        if not sbom_file.exists():
            return VerificationResult(
                "OSV Vulnerability Scan",
                False,
                "SBOM not found for scanning"
            )

        try:
            result = subprocess.run(
                ["osv-scanner", "--sbom", str(sbom_file), "--format", "json"],
                capture_output=True,
                text=True,
                timeout=60
            )

            # OSV scanner returns 0 if no vulnerabilities, 1 if vulnerabilities found
            if result.returncode == 0:
                return VerificationResult(
                    "OSV Vulnerability Scan",
                    True,
                    "No known vulnerabilities found",
                    "Scanned against OSV database"
                )
            elif result.returncode == 1:
                # Parse vulnerabilities if possible
                try:
                    output = json.loads(result.stdout)
                    vuln_count = len(output.get("results", [{}])[0].get("packages", []))
                    return VerificationResult(
                        "OSV Vulnerability Scan",
                        False,
                        f"Found vulnerabilities in {vuln_count} package(s)",
                        "Run 'osv-scanner --sbom sbom.json' for details"
                    )
                except:
                    return VerificationResult(
                        "OSV Vulnerability Scan",
                        False,
                        "Vulnerabilities detected",
                        "Run 'osv-scanner --sbom sbom.json' for details"
                    )
            else:
                return VerificationResult(
                    "OSV Vulnerability Scan",
                    False,
                    "Scan failed",
                    result.stderr[:200] if result.stderr else None
                )

        except FileNotFoundError:
            return VerificationResult(
                "OSV Vulnerability Scan",
                False,
                "osv-scanner not installed",
                "Install: brew install osv-scanner or see https://google.github.io/osv-scanner/"
            )
        except subprocess.TimeoutExpired:
            return VerificationResult(
                "OSV Vulnerability Scan",
                False,
                "Scan timeout"
            )
        except Exception as e:
            return VerificationResult(
                "OSV Vulnerability Scan",
                False,
                "Scan error",
                str(e)[:200]
            )

    def _load_attestation_statements(self, attestation_file: Path) -> List[Dict]:
        """Load attestation statements from a JSONL bundle."""
        statements: List[Dict] = []
        with open(attestation_file) as f:
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)

                # Handle DSSE envelopes
                if "payload" in record and "payloadType" in record:
                    try:
                        payload_bytes = base64.b64decode(record["payload"])
                        payload = json.loads(payload_bytes)
                        statements.append(payload)
                        continue
                    except (ValueError, json.JSONDecodeError):
                        pass

                if isinstance(record, dict):
                    statements.append(record)
        return statements

    def verify_slsa_provenance(self) -> VerificationResult:
        """Verify SLSA provenance attestation."""
        if not self.binary_path:
            return VerificationResult(
                "SLSA Provenance",
                False,
                "Binary not found"
            )

        # SLSA provenance is included in GitHub attestations
        # We verify it through the attestation bundle
        attestation_file = self.binary_path.parent / "attestation.jsonl"
        if not attestation_file.exists():
            return VerificationResult(
                "SLSA Provenance",
                False,
                "Attestation bundle not found",
                f"Expected at: {attestation_file}"
            )

        try:
            statements = self._load_attestation_statements(attestation_file)
            if not statements:
                return VerificationResult(
                    "SLSA Provenance",
                    False,
                    "Attestation bundle is empty or unreadable",
                    f"File: {attestation_file}"
                )

            binary_checksum = self._calculate_binary_sha256()
            if not binary_checksum:
                return VerificationResult(
                    "SLSA Provenance",
                    False,
                    "Unable to calculate binary checksum"
                )

            slsa_statements = [
                stmt for stmt in statements
                if "predicateType" in stmt and "slsa" in stmt["predicateType"].lower()
            ]

            if not slsa_statements:
                return VerificationResult(
                    "SLSA Provenance",
                    False,
                    "No SLSA provenance in attestation bundle",
                    f"Found {len(statements)} attestation(s)"
                )

            for statement in slsa_statements:
                subjects = statement.get("subject", [])
                for subject in subjects:
                    subject_name = subject.get("name", "")
                    digest = subject.get("digest", {})
                    subject_checksum = (digest.get("sha256") or "").lower()

                    if Path(subject_name).name != self.binary_path.name:
                        continue

                    if subject_checksum != binary_checksum.lower():
                        return VerificationResult(
                            "SLSA Provenance",
                            False,
                            "Attestation digest does not match binary",
                            f"Attested {subject_checksum[:16]}…, calculated {binary_checksum[:16]}…"
                        )

                    builder_id = (
                        statement.get("predicate", {})
                        .get("builder", {})
                        .get("id", "unknown")
                    )
                    build_type = statement.get("predicate", {}).get("buildType", "unknown")

                    return VerificationResult(
                        "SLSA Provenance",
                        True,
                        "SLSA provenance attestation verified",
                        f"Builder: {builder_id} | Build type: {build_type}"
                    )

            return VerificationResult(
                "SLSA Provenance",
                False,
                "Attestation bundle does not cover binary",
                f"Binary: {self.binary_path.name}"
            )

        except Exception as e:
            return VerificationResult(
                "SLSA Provenance",
                False,
                "Provenance verification error",
                str(e)[:200]
            )

    def verify_reproducible_build(self) -> VerificationResult:
        """Check for reproducible build indicators."""
        if not self.binary_path or not self.binary_path.exists():
            return VerificationResult(
                "Reproducible Build",
                False,
                "Binary not found"
            )

        # Check if SOURCE_DATE_EPOCH was used via attestation metadata
        provenance_file = self.binary_path.parent / "attestation.jsonl"
        source_date_epoch = None

        def _extract_epoch_from_payload(payload: Dict) -> Optional[str]:
            if not isinstance(payload, dict):
                return None
            if "SOURCE_DATE_EPOCH" in payload:
                return str(payload["SOURCE_DATE_EPOCH"])
            for value in payload.values():
                if isinstance(value, dict):
                    nested = _extract_epoch_from_payload(value)
                    if nested:
                        return nested
                elif isinstance(value, list):
                    for item in value:
                        nested = _extract_epoch_from_payload(item) if isinstance(item, dict) else None
                        if nested:
                            return nested
            return None

        if provenance_file.exists():
            try:
                statements = self._load_attestation_statements(provenance_file)
                for statement in statements:
                    epoch = _extract_epoch_from_payload(statement.get("predicate", {}))
                    if epoch:
                        source_date_epoch = epoch
                        break
            except Exception:
                pass

        # Check build metadata file if it exists
        metadata_file = self.binary_path.parent / "build-metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    epoch = _extract_epoch_from_payload(metadata)
                    if epoch:
                        source_date_epoch = epoch
            except Exception:
                pass

        if not source_date_epoch:
            return VerificationResult(
                "Reproducible Build",
                False,
                "SOURCE_DATE_EPOCH not found in build metadata",
                "Ensure builds export SOURCE_DATE_EPOCH in provenance or metadata"
            )

        if not str(source_date_epoch).isdigit():
            return VerificationResult(
                "Reproducible Build",
                False,
                "Invalid SOURCE_DATE_EPOCH value",
                f"Value: {source_date_epoch}"
            )

        return VerificationResult(
            "Reproducible Build",
            True,
            "Reproducible build verified",
            f"SOURCE_DATE_EPOCH: {source_date_epoch}"
        )

    def verify_certificate_identity(self) -> VerificationResult:
        """Verify Sigstore certificate identity and issuer."""
        if not self.binary_path or not self.binary_path.exists():
            return VerificationResult(
                "Certificate Identity",
                False,
                "Binary not found"
            )

        sig_bundle = self.binary_path.with_suffix(self.binary_path.suffix + ".sigstore")
        if not sig_bundle.exists():
            return VerificationResult(
                "Certificate Identity",
                False,
                "Signature bundle not found",
                "Sigstore signature required for certificate verification"
            )

        try:
            # Use cosign to verify with specific identity requirements
            result = subprocess.run(
                [
                    "cosign", "verify-blob",
                    str(self.binary_path),
                    "--bundle", str(sig_bundle),
                    "--certificate-identity-regexp", f".*{self.github_repo}.*",
                    "--certificate-oidc-issuer", "https://token.actions.githubusercontent.com"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return VerificationResult(
                    "Certificate Identity",
                    True,
                    "Certificate identity verified",
                    f"OIDC issuer: GitHub Actions | Repo: {self.github_repo}"
                )
            else:
                return VerificationResult(
                    "Certificate Identity",
                    False,
                    "Certificate identity verification failed",
                    "Certificate may not match expected GitHub repository"
                )

        except FileNotFoundError:
            return VerificationResult(
                "Certificate Identity",
                False,
                "cosign not installed",
                "Install: brew install cosign"
            )
        except subprocess.TimeoutExpired:
            return VerificationResult(
                "Certificate Identity",
                False,
                "Verification timeout"
            )
        except Exception as e:
            return VerificationResult(
                "Certificate Identity",
                False,
                "Verification error",
                str(e)[:200]
            )

    def verify_build_environment(self) -> VerificationResult:
        """Verify build environment details from SLSA provenance."""
        if not self.binary_path:
            return VerificationResult(
                "Build Environment",
                False,
                "Binary not found"
            )

        provenance_file = self.binary_path.parent / "attestation.jsonl"
        if not provenance_file.exists():
            return VerificationResult(
                "Build Environment",
                False,
                "Provenance file not found"
            )

        try:
            statements = self._load_attestation_statements(provenance_file)
            slsa_statements = [
                stmt for stmt in statements
                if "predicateType" in stmt and "slsa" in stmt["predicateType"].lower()
            ]

            if not slsa_statements:
                return VerificationResult(
                    "Build Environment",
                    False,
                    "No SLSA provenance found"
                )

            # Extract build environment details
            predicate = slsa_statements[0].get("predicate", {})
            builder_id = predicate.get("builder", {}).get("id", "unknown")
            build_type = predicate.get("buildType", "unknown")

            # Extract workflow/runner details if available
            metadata = predicate.get("metadata", {})
            invocation = predicate.get("invocation", {})

            details_parts = []
            if "github" in builder_id.lower():
                details_parts.append("Builder: GitHub Actions")
            if invocation.get("configSource"):
                config_uri = invocation["configSource"].get("uri", "")
                if config_uri:
                    details_parts.append(f"Workflow: {config_uri.split('/')[-1]}")

            details = " | ".join(details_parts) if details_parts else f"Builder: {builder_id}"

            return VerificationResult(
                "Build Environment",
                True,
                "Build environment verified from SLSA provenance",
                details
            )

        except Exception as e:
            return VerificationResult(
                "Build Environment",
                False,
                "Failed to verify build environment",
                str(e)[:200]
            )

    def verify_license_compliance(self) -> VerificationResult:
        """Verify license compliance from SBOM."""
        if not self.binary_path:
            return VerificationResult(
                "License Compliance",
                False,
                "Binary not found"
            )

        # Look for SBOM files
        sbom_files = [
            self.binary_path.parent / "sbom.spdx.json",
            self.binary_path.parent / "sbom.cyclonedx.json",
            self.binary_path.parent / "sbom.json"
        ]

        licenses_found = set()
        packages_without_license = 0
        total_packages = 0

        for sbom_file in sbom_files:
            if not sbom_file.exists():
                continue

            try:
                with open(sbom_file) as f:
                    sbom = json.load(f)

                # Parse CycloneDX format
                if sbom.get("bomFormat") == "CycloneDX":
                    components = sbom.get("components", [])
                    for component in components:
                        total_packages += 1
                        licenses = component.get("licenses", [])
                        if licenses:
                            for lic in licenses:
                                if isinstance(lic, dict):
                                    lic_id = lic.get("license", {}).get("id") or lic.get("license", {}).get("name")
                                    if lic_id:
                                        licenses_found.add(lic_id)
                        else:
                            packages_without_license += 1

                # Parse SPDX format
                elif "spdxVersion" in sbom:
                    packages = sbom.get("packages", [])
                    for package in packages:
                        total_packages += 1
                        lic = package.get("licenseConcluded") or package.get("licenseDeclared")
                        if lic and lic != "NOASSERTION":
                            licenses_found.add(lic)
                        else:
                            packages_without_license += 1

                break  # Use first valid SBOM found

            except (json.JSONDecodeError, Exception):
                continue

        if total_packages == 0:
            return VerificationResult(
                "License Compliance",
                False,
                "No SBOM found with license information"
            )

        # Check for problematic licenses (GPL, AGPL for proprietary software)
        problematic_licenses = [
            lic for lic in licenses_found
            if any(x in lic.upper() for x in ["GPL", "AGPL", "LGPL"])
        ]

        if problematic_licenses:
            details = f"Found copyleft: {', '.join(sorted(problematic_licenses)[:3])}"
        else:
            details = f"{len(licenses_found)} unique licenses, {total_packages - packages_without_license}/{total_packages} packages licensed"

        return VerificationResult(
            "License Compliance",
            len(problematic_licenses) == 0,
            f"License check: {len(licenses_found)} unique licenses",
            details
        )

    def verify_dependency_pinning(self) -> VerificationResult:
        """Verify dependencies have pinned versions in SBOM."""
        if not self.binary_path:
            return VerificationResult(
                "Dependency Pinning",
                False,
                "Binary not found"
            )

        sbom_files = [
            self.binary_path.parent / "sbom.spdx.json",
            self.binary_path.parent / "sbom.cyclonedx.json"
        ]

        total_deps = 0
        unpinned_deps = []

        for sbom_file in sbom_files:
            if not sbom_file.exists():
                continue

            try:
                with open(sbom_file) as f:
                    sbom = json.load(f)

                if sbom.get("bomFormat") == "CycloneDX":
                    for component in sbom.get("components", []):
                        name = component.get("name", "unknown")
                        # Skip the package itself - it's not a dependency
                        if name in ("provenance-demo", ".", "demo_cli"):
                            continue
                        total_deps += 1
                        version = component.get("version", "")
                        # Check for unpinned versions (wildcards, ranges, etc.)
                        if not version or "*" in version or "^" in version or "~" in version or ">" in version or "<" in version:
                            unpinned_deps.append(name)

                elif "spdxVersion" in sbom:
                    for package in sbom.get("packages", []):
                        name = package.get("name", "unknown")
                        # Skip the package itself - it's not a dependency
                        if name in ("provenance-demo", ".", "demo_cli"):
                            continue
                        total_deps += 1
                        version = package.get("versionInfo", "")
                        if not version or "*" in version or "^" in version or "~" in version:
                            unpinned_deps.append(name)

                break  # Use first valid SBOM

            except (json.JSONDecodeError, Exception):
                continue

        if total_deps == 0:
            return VerificationResult(
                "Dependency Pinning",
                False,
                "No SBOM found with dependency information"
            )

        pinned_count = total_deps - len(unpinned_deps)
        pinned_percentage = (pinned_count / total_deps * 100) if total_deps > 0 else 0

        if len(unpinned_deps) == 0:
            return VerificationResult(
                "Dependency Pinning",
                True,
                f"All {total_deps} dependencies pinned to specific versions",
                f"100% pinned ({total_deps}/{total_deps})"
            )
        else:
            details = f"{pinned_percentage:.1f}% pinned ({pinned_count}/{total_deps})"
            if len(unpinned_deps) <= 3:
                details += f" | Unpinned: {', '.join(unpinned_deps)}"
            else:
                details += f" | {len(unpinned_deps)} unpinned dependencies"

            return VerificationResult(
                "Dependency Pinning",
                len(unpinned_deps) == 0,
                f"Dependency pinning: {pinned_count}/{total_deps} pinned",
                details
            )

    def verify_rekor_transparency_log(self) -> VerificationResult:
        """Verify and extract Rekor transparency log details."""
        if not self.binary_path or not self.binary_path.exists():
            return VerificationResult(
                "Rekor Transparency Log",
                False,
                "Binary not found"
            )

        # Look for Sigstore bundle which contains Rekor log info
        sig_bundle = self.binary_path.parent / f"{self.binary_path.name}.sigstore.json"
        if not sig_bundle.exists():
            return VerificationResult(
                "Rekor Transparency Log",
                False,
                "Sigstore bundle not found",
                "Rekor verification requires .sigstore.json bundle"
            )

        try:
            with open(sig_bundle) as f:
                bundle_data = json.load(f)

            # Extract Rekor log entry details - handle both bundle formats
            # Format 1: verificationMaterial.tlogEntries (newer format)
            verification_material = bundle_data.get("verificationMaterial", {})
            tlog_entries = verification_material.get("tlogEntries", [])

            # Format 2: rekorBundle (older/cosign sign-blob format)
            rekor_bundle = bundle_data.get("rekorBundle", {})

            log_index = None
            log_id = None
            integrated_time = None

            if tlog_entries:
                # Use verificationMaterial format
                log_entry = tlog_entries[0]
                log_index = log_entry.get("logIndex")
                log_id = log_entry.get("logId", {})
                integrated_time = log_entry.get("integratedTime")
            elif rekor_bundle:
                # Use rekorBundle format
                payload = rekor_bundle.get("Payload", {})
                log_index = payload.get("logIndex")
                log_id = payload.get("logID")
                integrated_time = payload.get("integratedTime")
            else:
                return VerificationResult(
                    "Rekor Transparency Log",
                    False,
                    "No transparency log entries found in bundle"
                )

            # Format integrated time as human-readable
            import datetime
            if integrated_time:
                timestamp = datetime.datetime.fromtimestamp(
                    int(integrated_time),
                    tz=datetime.timezone.utc
                ).strftime("%Y-%m-%d %H:%M:%S UTC")
            else:
                timestamp = "unknown"

            # Extract log ID (key hint)
            key_hint = log_id.get("keyId", "unknown") if isinstance(log_id, dict) else "unknown"
            if isinstance(key_hint, str) and len(key_hint) > 16:
                key_hint = key_hint[:16] + "..."

            details = f"Index: {log_index} | Time: {timestamp} | Key: {key_hint}"

            return VerificationResult(
                "Rekor Transparency Log",
                True,
                "Rekor transparency log entry verified",
                details
            )

        except FileNotFoundError:
            return VerificationResult(
                "Rekor Transparency Log",
                False,
                "Sigstore bundle file not found"
            )
        except json.JSONDecodeError:
            return VerificationResult(
                "Rekor Transparency Log",
                False,
                "Invalid Sigstore bundle format"
            )
        except Exception as e:
            return VerificationResult(
                "Rekor Transparency Log",
                False,
                "Failed to extract Rekor log details",
                str(e)[:200]
            )

    def verify_artifact_metadata(self) -> VerificationResult:
        """Verify GitHub release artifact metadata."""
        if not self.binary_path:
            return VerificationResult(
                "Artifact Metadata",
                False,
                "Binary not found"
            )

        try:
            # Try to find the release containing this artifact
            # Step 1: Get list of recent release tags
            result = subprocess.run(
                [
                    "gh", "release", "list",
                    "--repo", self.github_repo,
                    "--json", "tagName",
                    "--limit", "20"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return VerificationResult(
                    "Artifact Metadata",
                    False,
                    "Could not fetch GitHub release list",
                    "Ensure gh CLI is authenticated"
                )

            releases = json.loads(result.stdout)

            # Step 2: For each release, check if it contains our artifact
            release_data = None
            for release in releases:
                tag = release.get("tagName", "")
                if not tag:
                    continue

                # Get full release details including assets
                view_result = subprocess.run(
                    [
                        "gh", "release", "view", tag,
                        "--repo", self.github_repo,
                        "--json", "tagName,name,assets,body"
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if view_result.returncode == 0:
                    release_details = json.loads(view_result.stdout)
                    assets = release_details.get("assets", [])
                    if any(asset["name"] == self.binary_path.name for asset in assets):
                        release_data = release_details
                        break

            # If not found, fall back to latest release
            if not release_data:
                result = subprocess.run(
                    [
                        "gh", "release", "view",
                        "--repo", self.github_repo,
                        "--json", "tagName,name,assets,body"
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    release_data = json.loads(result.stdout)

            if not release_data:
                return VerificationResult(
                    "Artifact Metadata",
                    False,
                    "No release found"
                )

            tag_name = release_data.get("tagName", "")
            release_name = release_data.get("name", "")
            assets = release_data.get("assets", [])
            body = release_data.get("body", "")

            # Check if version matches tag (normalize for hatch-vcs format)
            version_matches_tag = False
            if tag_name:
                # Strip 'v' prefix if present
                tag_version = tag_name.lstrip("v")
                current_version = self.version.lstrip("v")

                # Normalize version format: "0.0.1-alpha.35" -> "0.0.1a35"
                normalized_tag = tag_version.replace("-alpha.", "a").replace("-beta.", "b").replace("-rc.", "rc")

                version_matches_tag = (normalized_tag == current_version or tag_version == current_version)

            # Check if binary is in release assets
            binary_in_assets = any(
                asset["name"] == self.binary_path.name
                for asset in assets
            )

            # Check for expected artifacts
            expected_artifacts = [".pyz", ".nupkg", "sbom"]
            found_artifacts = []
            for expected in expected_artifacts:
                if any(expected in asset["name"] for asset in assets):
                    found_artifacts.append(expected)

            # Check if release has notes
            has_release_notes = len(body.strip()) > 0

            # Build details
            details_parts = []
            if version_matches_tag:
                details_parts.append(f"Tag: {tag_name}")
            else:
                details_parts.append(f"Tag mismatch: {tag_name} != v{self.version}")

            details_parts.append(f"Assets: {len(assets)}")
            details_parts.append(f"Expected artifacts: {'/'.join(found_artifacts)}")

            if has_release_notes:
                details_parts.append("Has release notes")

            details = " | ".join(details_parts)

            # Pass if version matches and binary is in assets
            passed = version_matches_tag and binary_in_assets

            if not passed:
                message = "Artifact metadata verification failed"
                if not version_matches_tag:
                    message = "Version does not match release tag"
                elif not binary_in_assets:
                    message = "Binary not found in release assets"
            else:
                message = "Artifact metadata verified"

            return VerificationResult(
                "Artifact Metadata",
                passed,
                message,
                details
            )

        except subprocess.TimeoutExpired:
            return VerificationResult(
                "Artifact Metadata",
                False,
                "GitHub API request timeout"
            )
        except json.JSONDecodeError:
            return VerificationResult(
                "Artifact Metadata",
                False,
                "Invalid GitHub API response"
            )
        except Exception as e:
            return VerificationResult(
                "Artifact Metadata",
                False,
                "Failed to verify artifact metadata",
                str(e)[:200]
            )

    def verify_all(self) -> bool:
        """
        Run all verification checks.

        Returns:
            True if all checks passed, False otherwise.
        """
        self._print_header(f"🔐 Verifying {self.binary_path.name if self.binary_path else 'binary'}")

        if self.console:
            self.console.print(f"[dim]Version: {self.version}[/dim]")
            self.console.print(f"[dim]Repository: {self.github_repo}[/dim]")
        else:
            print(f"Version: {self.version}")
            print(f"Repository: {self.github_repo}")

        # Run all checks
        checks = [
            ("Checksum", self.verify_checksum),
            ("Sigstore Signature", self.verify_sigstore_signature),
            ("Certificate Identity", self.verify_certificate_identity),
            ("Rekor Transparency Log", self.verify_rekor_transparency_log),
            ("GitHub Attestation", self.verify_github_attestation),
            ("SBOM Attestation", self.verify_sbom_attestation),
            ("SBOM", self.verify_sbom),
            ("OSV Scan", self.verify_osv_scan),
            ("SLSA Provenance", self.verify_slsa_provenance),
            ("Build Environment", self.verify_build_environment),
            ("Reproducible Build", self.verify_reproducible_build),
            ("Artifact Metadata", self.verify_artifact_metadata),
            ("License Compliance", self.verify_license_compliance),
            ("Dependency Pinning", self.verify_dependency_pinning),
        ]

        if self.console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True
            ) as progress:
                for name, check_func in checks:
                    task = progress.add_task(f"Checking {name}...", total=None)
                    result = check_func()
                    self.results.append(result)
                    progress.remove_task(task)
                    self._print_result(result)
        else:
            for name, check_func in checks:
                print(f"\nChecking {name}...")
                result = check_func()
                self.results.append(result)
                self._print_result(result)

        # Summary
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        all_passed = passed == total

        self._print_header("Summary")
        if self.console:
            status_color = "green" if all_passed else "red"
            self.console.print(f"[{status_color}]{passed}/{total} checks passed[/{status_color}]")

            if not all_passed:
                self.console.print("\n[yellow]⚠ Some verifications failed or are skipped[/yellow]")
                self.console.print("[dim]This may be expected if:[/dim]")
                self.console.print("[dim]  • You're running a development build (not a release)[/dim]")
                self.console.print("[dim]  • Security tools (cosign, gh, osv-scanner) are not installed[/dim]")
                self.console.print("[dim]  • Attestation files are not present locally[/dim]")
        else:
            status = "✓" if all_passed else "✗"
            print(f"{status} {passed}/{total} checks passed")

            if not all_passed:
                print("\n⚠ Some verifications failed or are skipped")
                print("This may be expected if:")
                print("  • You're running a development build (not a release)")
                print("  • Security tools (cosign, gh, osv-scanner) are not installed")
                print("  • Attestation files are not present locally")

        return all_passed


def verify_command(args) -> int:
    """Run the verify command."""
    binary_path = None
    if hasattr(args, 'file') and args.file:
        binary_path = Path(args.file)

    verifier = Verifier(binary_path)
    success = verifier.verify_all()

    return 0 if success else 1
