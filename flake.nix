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
          ];

          # No runtime dependencies for this simple CLI
          propagatedBuildInputs = [ ];

          postInstall = ''
            # Create a .pyz zipapp from the installed package
            export TZ=UTC
            export LC_ALL=C
            export LANG=C
            export PYTHONHASHSEED=0
            export SOURCE_DATE_EPOCH=315532800

            echo "Creating zipapp from installed package..."
            mkdir -p /build/zipapp-source
            cp -r $out/${python.sitePackages}/demo_cli /build/zipapp-source/

            ${python}/bin/python -m zipapp /build/zipapp-source \
              -m "demo_cli.cli:main" \
              -p "/usr/bin/env python3" \
              -o $out/bin/provenance-demo

            chmod +x $out/bin/provenance-demo
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
