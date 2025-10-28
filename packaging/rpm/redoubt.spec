Name:           provenance-demo
Version:        0.1.0
Release:        1%{?dist}
Summary:        Demo CLI showcasing supply chain security and provenance

License:        MIT
URL:            https://github.com/redoubt-cysec/provenance-template
Source0:        https://github.com/redoubt-cysec/provenance-template/archive/v%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3 >= 3.10
BuildRequires:  python3-pip
BuildRequires:  python3-devel
BuildRequires:  rsync
Requires:       python3 >= 3.10

%description
Provenance Demo demonstrates production-grade supply chain security.

Features:
- Reproducible, deterministic builds
- Sigstore signatures and GitHub attestations
- SLSA provenance and SBOM generation
- OSV vulnerability scanning
- Complete supply chain security validation

Run 'provenance-demo verify' to validate all security attestations!

%prep
%setup -q -n provenance-template-%{version}

%build
# Set reproducible build environment
export TZ=UTC
export LC_ALL=C
export LANG=C
export PYTHONHASHSEED=0
export SOURCE_DATE_EPOCH=$(date +%s)

# Build the .pyz
./scripts/build_pyz.sh

%install
# Install the .pyz to /usr/bin
install -D -m 755 dist/provenance-demo.pyz %{buildroot}%{_bindir}/provenance-demo

%files
%license LICENSE
%doc README.md
%{_bindir}/provenance-demo

%changelog
* Mon Oct 14 2024 Your Name <your.email@example.com> - 0.1.0-1
- Initial RPM package
- Self-verifying CLI with complete supply chain security
- Reproducible builds with SOURCE_DATE_EPOCH
- Sigstore keyless signing support
- GitHub attestations and SLSA provenance
- SBOM generation with CycloneDX
- OSV vulnerability scanning
- Comprehensive security test suite (100+ tests)
