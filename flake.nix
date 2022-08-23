{
  description = "A role selection bot using drop down menus";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:

    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        lib = pkgs.lib;
      in
      rec {
        formatter = pkgs.nixpkgs-fmt;

        defaultPackage = packages.discord-bot;

        packages = flake-utils.lib.flattenTree rec {

          discord-bot = pkgs.python3Packages.buildPythonPackage rec {
            pname = "discord-bot";
            version = "2.0.0";

            src = self;
            doCheck = false;
            propagatedBuildInputs = with pkgs.python3Packages;[
              discordpy
            ];

            meta = with lib; {
              description =
                "A role selection bot using drop down menus";
              homepage = "https://github.com/nonchris/discord-role-selection";
              platforms = platforms.unix;
              maintainers = with maintainers; [ MayNiklas ];
            };
          };

        };

      });
}
