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
      in
      rec {
        formatter = pkgs.nixpkgs-fmt;

        defaultPackage = packages.discord-bot;

        packages = flake-utils.lib.flattenTree rec {

          discordpy_2 = pkgs.python3Packages.callPackage ./nix/packages/discordpy/default.nix { };

          discord-bot = pkgs.python3Packages.callPackage ./nix/packages/discord-role-selection { inherit discordpy_2; };

        };

      });
}
