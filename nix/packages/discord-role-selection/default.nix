{ lib
, buildPythonPackage
, discordpy_2
}:

buildPythonPackage rec {
  pname = "discord-bot";
  version = "2.0.0";

  src = ../../../.;
  propagatedBuildInputs = [ discordpy_2 ];
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
