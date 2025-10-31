{
  description = "Provenance Demo - Demo CLI showcasing supply chain security and provenance";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python310;
      in
      {
        packages.default = python.pkgs.buildPythonApplication {
          pname = "provenance-demo";
          version = "0.1.0";
          format = "pyproject";

          src = ./.;

          nativeBuildInputs = with python.pkgs; [
            hatchling
            hatch-vcs
          ];

          # No runtime dependencies for this simple CLI
          propagatedBuildInputs = [ ];

          postInstall = ''
            # Create a .pyz zipapp from the installed package with reproducible timestamps
            export TZ=UTC
            export LC_ALL=C
            export LANG=C
            export PYTHONHASHSEED=0
            export SOURCE_DATE_EPOCH=315532800

            echo "Creating zipapp from installed package..."
            mkdir -p $TMP/zipapp-source
            cp -r $out/${python.sitePackages}/demo_cli $TMP/zipapp-source/

            # Create reproducible zipapp using zipfile directly
            ${python}/bin/python3 << 'EOF'
import zipfile
import os
import time
from pathlib import Path

sde = int(os.environ.get('SOURCE_DATE_EPOCH', time.time()))
date_time = time.gmtime(sde)[:6]

output = os.environ['out'] + '/bin/provenance-demo'
os.makedirs(os.path.dirname(output), exist_ok=True)

with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
    # Add __main__.py with deterministic timestamp
    main_content = 'from demo_cli.cli import main\nmain()\n'
    zinfo = zipfile.ZipInfo('__main__.py', date_time=date_time)
    zinfo.external_attr = 0o644 << 16
    zf.writestr(zinfo, main_content, compress_type=zipfile.ZIP_DEFLATED)

    # Add all source files in sorted order with deterministic timestamps
    src_dir = Path(os.environ['TMP'] + '/zipapp-source')
    for file_path in sorted(src_dir.rglob('*')):
        if file_path.is_file():
            arcname = str(file_path.relative_to(src_dir))
            zinfo = zipfile.ZipInfo(arcname, date_time=date_time)
            zinfo.external_attr = 0o644 << 16
            with open(file_path, 'rb') as f:
                zf.writestr(zinfo, f.read(), compress_type=zipfile.ZIP_DEFLATED)

# Add shebang
with open(output, 'rb') as f:
    content = f.read()
with open(output, 'wb') as f:
    f.write(b'#!/usr/bin/env python3\n' + content)

os.chmod(output, 0o755)
EOF
          '';

          meta = with pkgs.lib; {
            description = "Demo CLI showcasing supply chain security and provenance";
            homepage = "https://github.com/redoubt-cysec/provenance-template";
            license = licenses.mit;
            maintainers = [ ];
            platforms = platforms.unix;
          };
        };

        # Development shell
        devShells.default = pkgs.mkShell {
          buildInputs = [
            python
            pkgs.rsync
            pkgs.uv  # Required for build_pyz.sh
            pkgs.git
            pkgs.cosign
            pkgs.gh
          ];

          shellHook = ''
            echo "Provenance Demo development environment"
            echo "Run: ./scripts/build_pyz.sh to build"
            echo "Run: ./dist/provenance-demo.pyz verify to test"
          '';
        };

        # Expose the app
        apps.default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/provenance-demo";
        };
      }
    );
}
