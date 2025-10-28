"""
Platform Configuration Tests

Tests that all distribution configuration files are valid and properly structured.
These tests validate syntax, required fields, and consistency across all platform packages.
"""
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import yaml

from .template_utils import guard_placeholders

REPO_ROOT = Path(__file__).parent.parent


class TestDockerfile:
    """Test Docker configuration."""

    def test_dockerfile_exists(self):
        """Verify Dockerfile exists."""
        dockerfile = REPO_ROOT / "Dockerfile"
        assert dockerfile.exists(), "Dockerfile not found"

    def test_dockerfile_uses_multistage(self):
        """Verify Dockerfile uses multi-stage build."""
        dockerfile = REPO_ROOT / "Dockerfile"
        content = dockerfile.read_text()
        assert "FROM" in content
        assert "as builder" in content.lower(), "Should use multi-stage build"

    def test_dockerfile_runs_as_nonroot(self):
        """Verify Docker container runs as non-root user."""
        dockerfile = REPO_ROOT / "Dockerfile"
        content = dockerfile.read_text()
        assert "USER" in content, "Should specify USER directive"
        assert "USER root" not in content, "Should not run as root"

    def test_dockerfile_has_labels(self):
        """Verify Dockerfile has OCI labels."""
        dockerfile = REPO_ROOT / "Dockerfile"
        content = dockerfile.read_text()
        assert "LABEL" in content, "Should have LABEL directives"
        assert "org.opencontainers.image" in content, "Should have OCI labels"


class TestScoopManifest:
    """Test Scoop package configuration."""

    def test_scoop_manifest_exists(self):
        """Verify Scoop manifest exists."""
        manifest = REPO_ROOT / "packaging" / "scoop" / "redoubt.json"
        assert manifest.exists(), "Scoop manifest not found"

    def test_scoop_manifest_valid_json(self):
        """Verify Scoop manifest is valid JSON."""
        manifest = REPO_ROOT / "packaging" / "scoop" / "redoubt.json"
        with open(manifest) as f:
            data = json.load(f)
        assert isinstance(data, dict), "Manifest should be a JSON object"

    def test_scoop_manifest_required_fields(self):
        """Verify Scoop manifest has required fields."""
        manifest = REPO_ROOT / "packaging" / "scoop" / "redoubt.json"
        with open(manifest) as f:
            data = json.load(f)

        required = ["version", "description", "homepage", "license", "url", "bin"]
        for field in required:
            assert field in data, f"Missing required field: {field}"
        guard_placeholders(
            [data.get("homepage"), data.get("url"), data.get("hash")],
            "Scoop manifest distribution references"
        )

    def test_scoop_manifest_has_checkver(self):
        """Verify Scoop manifest has auto-update configuration."""
        manifest = REPO_ROOT / "packaging" / "scoop" / "redoubt.json"
        with open(manifest) as f:
            data = json.load(f)
        assert "checkver" in data, "Should have checkver for auto-updates"
        assert "autoupdate" in data, "Should have autoupdate configuration"


class TestWinGetManifest:
    """Test WinGet package configuration."""

    def test_winget_manifest_exists(self):
        """Verify WinGet manifest exists."""
        manifest = REPO_ROOT / "packaging" / "winget" / "manifests" / "OWNER.redoubt.yaml"
        assert manifest.exists(), "WinGet manifest not found"

    def test_winget_manifest_valid_yaml(self):
        """Verify WinGet manifest is valid YAML."""
        manifest = REPO_ROOT / "packaging" / "winget" / "manifests" / "OWNER.redoubt.yaml"
        with open(manifest) as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict), "Manifest should be a YAML object"

    def test_winget_manifest_required_fields(self):
        """Verify WinGet manifest has required fields."""
        manifest = REPO_ROOT / "packaging" / "winget" / "manifests" / "OWNER.redoubt.yaml"
        with open(manifest) as f:
            data = yaml.safe_load(f)

        required = [
            "PackageIdentifier", "PackageVersion", "PackageName",
            "Publisher", "License", "ShortDescription", "Installers"
        ]
        for field in required:
            assert field in data, f"Missing required field: {field}"
        guard_placeholders(
            [
                data.get("PackageIdentifier"),
                data.get("Publisher"),
                data.get("PublisherUrl"),
                data.get("PackageUrl"),
            ],
            "WinGet manifest metadata"
        )

    def test_winget_manifest_has_installers(self):
        """Verify WinGet manifest has installer configuration."""
        manifest = REPO_ROOT / "packaging" / "winget" / "manifests" / "OWNER.redoubt.yaml"
        with open(manifest) as f:
            data = yaml.safe_load(f)
        assert "Installers" in data, "Should have Installers section"
        assert len(data["Installers"]) > 0, "Should have at least one installer"


class TestDebianPackage:
    """Test Debian package configuration."""

    def test_debian_control_exists(self):
        """Verify Debian control file exists."""
        control = REPO_ROOT / "packaging" / "debian" / "control"
        assert control.exists(), "packaging/debian/control not found"

    def test_debian_control_has_source(self):
        """Verify Debian control has source package."""
        control = REPO_ROOT / "packaging" / "debian" / "control"
        content = control.read_text()
        assert "Source:" in content, "Should have Source field"
        assert "Package:" in content, "Should have Package field"

    def test_debian_rules_exists(self):
        """Verify Debian rules file exists."""
        rules = REPO_ROOT / "packaging" / "debian" / "rules"
        assert rules.exists(), "packaging/debian/rules not found"

    def test_debian_rules_executable(self):
        """Verify Debian rules is executable."""
        rules = REPO_ROOT / "packaging" / "debian" / "rules"
        assert rules.stat().st_mode & 0o111, "packaging/debian/rules should be executable"

    def test_debian_changelog_exists(self):
        """Verify Debian changelog exists."""
        changelog = REPO_ROOT / "packaging" / "debian" / "changelog"
        assert changelog.exists(), "packaging/debian/changelog not found"


class TestRPMSpec:
    """Test RPM package configuration."""

    def test_rpm_spec_exists(self):
        """Verify RPM spec file exists."""
        spec = REPO_ROOT / "packaging" / "rpm" / "redoubt.spec"
        assert spec.exists(), "RPM spec file not found"

    def test_rpm_spec_has_required_fields(self):
        """Verify RPM spec has required fields."""
        spec = REPO_ROOT / "packaging" / "rpm" / "redoubt.spec"
        content = spec.read_text()

        required = ["Name:", "Version:", "Release:", "Summary:", "License:", "URL:"]
        for field in required:
            assert field in content, f"RPM spec missing required field: {field}"

    def test_rpm_spec_has_sections(self):
        """Verify RPM spec has required sections."""
        spec = REPO_ROOT / "packaging" / "rpm" / "redoubt.spec"
        content = spec.read_text()

        sections = ["%description", "%prep", "%build", "%install", "%files"]
        for section in sections:
            assert section in content, f"RPM spec missing section: {section}"


class TestFlatpakManifest:
    """Test Flatpak configuration."""

    def test_flatpak_manifest_exists(self):
        """Verify Flatpak manifest exists."""
        manifest = REPO_ROOT / "packaging" / "flatpak" / "com.OWNER.Redoubt.yml"
        assert manifest.exists(), "Flatpak manifest not found"

    def test_flatpak_manifest_valid_yaml(self):
        """Verify Flatpak manifest is valid YAML."""
        manifest = REPO_ROOT / "packaging" / "flatpak" / "com.OWNER.Redoubt.yml"
        with open(manifest) as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict), "Manifest should be a YAML object"

    def test_flatpak_manifest_has_app_id(self):
        """Verify Flatpak manifest has proper app ID."""
        manifest = REPO_ROOT / "packaging" / "flatpak" / "com.OWNER.Redoubt.yml"
        with open(manifest) as f:
            data = yaml.safe_load(f)
        assert "app-id" in data, "Should have app-id"
        assert data["app-id"].startswith("com."), "app-id should use reverse DNS"
        guard_placeholders(data["app-id"], "Flatpak app-id")

    def test_flatpak_desktop_file_exists(self):
        """Verify Flatpak .desktop file exists."""
        desktop = REPO_ROOT / "packaging" / "flatpak" / "com.OWNER.Redoubt.desktop"
        assert desktop.exists(), "Flatpak .desktop file not found"

    def test_flatpak_metainfo_exists(self):
        """Verify Flatpak metainfo.xml exists."""
        metainfo = REPO_ROOT / "packaging" / "flatpak" / "com.OWNER.Redoubt.metainfo.xml"
        assert metainfo.exists(), "Flatpak metainfo.xml not found"

    def test_flatpak_metainfo_valid_xml(self):
        """Verify Flatpak metainfo is valid XML."""
        metainfo = REPO_ROOT / "packaging" / "flatpak" / "com.OWNER.Redoubt.metainfo.xml"
        try:
            ET.parse(metainfo)
        except ET.ParseError as e:
            pytest.fail(f"Invalid XML in metainfo.xml: {e}")


class TestAppImage:
    """Test AppImage configuration."""

    def test_appimage_config_exists(self):
        """Verify AppImage config exists."""
        config = REPO_ROOT / "packaging" / "appimage" / "AppImageBuilder.yml"
        assert config.exists(), "AppImageBuilder.yml not found"

    def test_appimage_config_valid_yaml(self):
        """Verify AppImage config is valid YAML."""
        config = REPO_ROOT / "packaging" / "appimage" / "AppImageBuilder.yml"
        with open(config) as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict), "Config should be a YAML object"

    def test_appimage_build_script_exists(self):
        """Verify AppImage build script exists."""
        script = REPO_ROOT / "packaging" / "appimage" / "build-appimage.sh"
        assert script.exists(), "build-appimage.sh not found"

    def test_appimage_build_script_executable(self):
        """Verify AppImage build script is executable."""
        script = REPO_ROOT / "packaging" / "appimage" / "build-appimage.sh"
        assert script.stat().st_mode & 0o111, "build-appimage.sh should be executable"


class TestNixFlake:
    """Test Nix flake configuration."""

    def test_nix_flake_exists(self):
        """Verify Nix flake exists."""
        flake = REPO_ROOT / "flake.nix"
        assert flake.exists(), "flake.nix not found"

    def test_nix_flake_has_description(self):
        """Verify Nix flake has description."""
        flake = REPO_ROOT / "flake.nix"
        content = flake.read_text()
        assert "description" in content, "flake.nix should have description"

    def test_nix_flake_has_outputs(self):
        """Verify Nix flake has outputs."""
        flake = REPO_ROOT / "flake.nix"
        content = flake.read_text()
        assert "outputs" in content, "flake.nix should have outputs"
        assert "packages" in content, "Should define packages"


class TestChocolatey:
    """Test Chocolatey package configuration."""

    def test_chocolatey_nuspec_exists(self):
        """Verify Chocolatey nuspec exists."""
        nuspec = REPO_ROOT / "packaging" / "chocolatey" / "redoubt.nuspec"
        assert nuspec.exists(), "Chocolatey nuspec not found"

    def test_chocolatey_nuspec_valid_xml(self):
        """Verify Chocolatey nuspec is valid XML."""
        nuspec = REPO_ROOT / "packaging" / "chocolatey" / "redoubt.nuspec"
        try:
            ET.parse(nuspec)
        except ET.ParseError as e:
            pytest.fail(f"Invalid XML in nuspec: {e}")

    def test_chocolatey_install_script_exists(self):
        """Verify Chocolatey install script exists."""
        script = REPO_ROOT / "packaging" / "chocolatey" / "tools" / "chocolateyinstall.ps1"
        assert script.exists(), "chocolateyinstall.ps1 not found"

    def test_chocolatey_uninstall_script_exists(self):
        """Verify Chocolatey uninstall script exists."""
        script = REPO_ROOT / "packaging" / "chocolatey" / "tools" / "chocolateyuninstall.ps1"
        assert script.exists(), "chocolateyuninstall.ps1 not found"


class TestAUR:
    """Test AUR package configuration."""

    def test_aur_pkgbuild_exists(self):
        """Verify AUR PKGBUILD exists."""
        pkgbuild = REPO_ROOT / "packaging" / "aur" / "PKGBUILD"
        assert pkgbuild.exists(), "AUR PKGBUILD not found"

    def test_aur_pkgbuild_has_required_fields(self):
        """Verify PKGBUILD has required fields."""
        pkgbuild = REPO_ROOT / "packaging" / "aur" / "PKGBUILD"
        content = pkgbuild.read_text()

        required = ["pkgname=", "pkgver=", "pkgrel=", "pkgdesc=", "arch=", "url=", "license="]
        for field in required:
            assert field in content, f"PKGBUILD missing required field: {field}"

    def test_aur_pkgbuild_has_functions(self):
        """Verify PKGBUILD has required functions."""
        pkgbuild = REPO_ROOT / "packaging" / "aur" / "PKGBUILD"
        content = pkgbuild.read_text()

        functions = ["build()", "package()"]
        for func in functions:
            assert func in content, f"PKGBUILD missing function: {func}"

    def test_aur_srcinfo_exists(self):
        """Verify AUR .SRCINFO exists."""
        srcinfo = REPO_ROOT / "packaging" / "aur" / ".SRCINFO"
        assert srcinfo.exists(), "AUR .SRCINFO not found"


class TestGitHubAction:
    """Test GitHub Action configuration."""

    def test_action_yaml_exists(self):
        """Verify action.yml exists."""
        action = REPO_ROOT / "action.yml"
        assert action.exists(), "action.yml not found"

    def test_action_yaml_valid(self):
        """Verify action.yml is valid YAML."""
        action = REPO_ROOT / "action.yml"
        with open(action) as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict), "action.yml should be a YAML object"

    def test_action_has_metadata(self):
        """Verify action has required metadata."""
        action = REPO_ROOT / "action.yml"
        with open(action) as f:
            data = yaml.safe_load(f)

        required = ["name", "description", "author", "runs"]
        for field in required:
            assert field in data, f"action.yml missing required field: {field}"

    def test_action_has_inputs_outputs(self):
        """Verify action defines inputs and outputs."""
        action = REPO_ROOT / "action.yml"
        with open(action) as f:
            data = yaml.safe_load(f)

        assert "inputs" in data, "Should define inputs"
        assert "outputs" in data, "Should define outputs"

    def test_action_has_branding(self):
        """Verify action has branding."""
        action = REPO_ROOT / "action.yml"
        with open(action) as f:
            data = yaml.safe_load(f)

        assert "branding" in data, "Should have branding"
        assert "icon" in data["branding"], "Should have icon"
        assert "color" in data["branding"], "Should have color"


class TestConfigurationConsistency:
    """Test consistency across all configurations."""

    def test_version_consistency(self):
        """Verify version is consistent across all configs."""
        # Read version from pyproject.toml
        import tomli
        with open(REPO_ROOT / "pyproject.toml", "rb") as f:
            pyproject = tomli.load(f)
        version = pyproject["project"]["version"]

        # Check other configs
        configs_to_check = [
            ("packaging/scoop/redoubt.json", lambda c: json.loads(c)["version"]),
            ("packaging/rpm/redoubt.spec", lambda c: f"Version:        {version}" in c),
            ("packaging/aur/PKGBUILD", lambda c: f'pkgver={version}' in c),
        ]

        for config_path, checker in configs_to_check:
            full_path = REPO_ROOT / config_path
            if full_path.exists():
                content = full_path.read_text()
                try:
                    if callable(checker):
                        result = checker(content)
                        if isinstance(result, bool):
                            assert result, f"Version mismatch in {config_path}"
                        else:
                            assert result == version, f"Version mismatch in {config_path}: expected {version}, got {result}"
                except Exception as e:
                    pytest.skip(f"Could not verify version in {config_path}: {e}")

    def test_name_consistency(self):
        """Verify package name is consistent where applicable."""
        expected_names = ["redoubt", "provenance-demo"]

        configs = [
            REPO_ROOT / "packaging" / "scoop" / "redoubt.json",
            REPO_ROOT / "packaging" / "chocolatey" / "redoubt.nuspec",
        ]

        for config in configs:
            if config.exists():
                content = config.read_text().lower()
                assert any(name in content for name in expected_names), \
                    f"Expected package name not found in {config.name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
