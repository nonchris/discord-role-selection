{ lib
, buildPythonPackage
, fetchFromGitHub
, discordpy
}:

buildPythonPackage rec {
  pname = "discord-bot";
  version = "2.0.0";

  src = ../../../.;

  propagatedBuildInputs = [
    (discordpy.overrideAttrs
      (old: rec {
        pname = "discord.py";
        version = "2.0.0a4370+g868476c9";
        src = fetchFromGitHub {
          owner = "Rapptz";
          repo = pname;
          rev = "903e2e64e9182b8d3330ef565af7bb46ff9f04da";
          sha256 = "sha256-u17sG3mjJf19euZ0CHvJwnvhb16F3WyAQt/w+RZFu1Y=";
        };
      }))
  ];

  doCheck = false;

  # removes install_requires from the setup.py
  # version numbers of discord.py are still broken
  preBuild = ''
    sed -i '32d' setup.py
  '';

  meta = with lib; {
    description =
      "A role selection bot using drop down menus";
    homepage = "https://github.com/nonchris/discord-role-selection";
    platforms = platforms.unix;
    maintainers = with maintainers; [ nonchris ];
  };
}
