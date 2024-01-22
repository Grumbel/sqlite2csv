{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonPackages = pkgs.python3Packages;
      in {
        packages = rec {
          default = sqlite2csv;

          sqlite2csv = pythonPackages.buildPythonPackage rec {
            pname = "sqlite2csv";
            version = "0.0.0";

            src = ./.;

            doCheck = true;

            checkPhase = ''
              runHook preCheck
              flake8 --max-line-length 120
              pyright sqlite2csv  # tests
              MYPYPATH=src mypy -p sqlite2csv  # -p tests
              pylint sqlite2csv  # tests
              # python3 -m unittest discover -v -s tests/
              runHook postCheck
            '';

            nativeCheckInputs = [
              pythonPackages.flake8
              pythonPackages.mypy
              pythonPackages.pylint
              pkgs.pyright
            ];
          };
        };
      }
    );
}
