{
  description = "Redoubt Release Demo - Self-verifying CLI with complete supply chain security";

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
        packages.default = pkgs.stdenv.mkDerivation {
          pname = "redoubt-release-template";
          version = "0.1.0";

          src = ./.;

          nativeBuildInputs = [
            python
            pkgs.rsync
            pkgs.uv  # Required for build_pyz.sh
          ];

          buildPhase = ''
            export TZ=UTC
            export LC_ALL=C
            export LANG=C
            export PYTHONHASHSEED=0
            # Use 1980-01-01 00:00:00 UTC as the epoch (315532800)
            # ZIP format requires timestamps >= 1980
            export SOURCE_DATE_EPOCH=315532800
            export HOME=$TMPDIR
            export UV_CACHE_DIR=$TMPDIR/.uv-cache

            # Create and activate a virtual environment to avoid PEP 668 issues
            # Use .venv so uv run recognizes it automatically
            echo "Creating virtual environment in .venv..."
            python -m venv .venv
            source .venv/bin/activate

            # Install required build tools in the venv
            # This ensures they're available when build_pyz.sh runs
            echo "Installing build dependencies in venv..."
            python -m pip install --upgrade pip build

            # Fix file timestamps to avoid ZIP < 1980 error
            # Nix sandbox files often have epoch timestamps (1970-01-01)
            # Touch all files to SOURCE_DATE_EPOCH (1980-01-01)
            echo "Fixing file timestamps for ZIP compatibility..."
            find . -exec touch -h -d @315532800 {} + 2>/dev/null || true

            # Now build with uv - it will use the .venv environment
            ./scripts/build_pyz.sh
          '';

          installPhase = ''
            mkdir -p $out/bin
            cp dist/redoubt-release-template.pyz $out/bin/redoubt
            chmod +x $out/bin/redoubt
          '';

          meta = with pkgs.lib; {
            description = "Self-verifying CLI with complete supply chain security";
            homepage = "https://github.com/OWNER/REPO";
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
            echo "Redoubt development environment"
            echo "Run: ./scripts/build_pyz.sh to build"
            echo "Run: ./dist/redoubt-release-template.pyz verify to test"
          '';
        };

        # Expose the app
        apps.default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/redoubt";
        };
      }
    );
}
