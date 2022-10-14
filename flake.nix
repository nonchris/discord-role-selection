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

          # Documenation for this feature: https://github.com/NixOS/nixpkgs/blob/master/pkgs/build-support/docker/examples.nix
          # nix build .#docker-image
          # docker load < result
          docker-image = pkgs.dockerTools.buildLayeredImage {

            name = "nonchris/discord-role-selection";
            tag = "latest";

            # Using "now" breaks reproducibility, the resulting image
            # will not be identical, but contain a useful timestamp:
            created = "now";

            contents = [
              # The GNU Core Utilities are the basic file,
              # shell and text manipulation utilities of the GNU operating system.
              # These are the core utilities which are expected to exist on every operating system.
              pkgs.coreutils

              # certificates, for http requests
              pkgs.cacert
            ];

            config.Entrypoint = [
              "${pkgs.coreutils}/bin/env"
              # Set the locale to UTF-8
              "LC_ALL=C.UTF–8"
              # set the nixpkgs-specific variable to the ssl certificate bundle.
              "SSL_CERT_FILE=${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
              "NIX_SSL_CERT_FILE=${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
            ];

            config.Volumes = {
              "/app/data/" = { };
            };

            config.WorkingDir = "/app";

            config.Cmd = [ "${self.packages."${pkgs.system}".discord-bot}/bin/discord-bot" ];

            config.Env = [
              "TOKEN=PASTE-TOKEN"
              "PREFIX=b!"
              "VERSION=unknown"
              "OWNER_NAME=unknwon"
              "OWNER_ID=100000000000000000"
              "ACTIVITY_NAME=f{PREFIX}help"
              "ROLES_JSON=data/roles.json"
            ];

          };


        };

      });
}
