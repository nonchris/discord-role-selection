{ lib
, aiohttp
, buildPythonPackage
, fetchFromGitHub
, libopus
, pynacl
, pythonOlder
, withVoice ? true
, ffmpeg
}:

buildPythonPackage rec {
  pname = "discord.py";
  version = "2.0.0a4370+g868476c9";
  format = "setuptools";

  disabled = pythonOlder "3.8";

  src = fetchFromGitHub {
    owner = "Rapptz";
    repo = pname;
    rev = "903e2e64e9182b8d3330ef565af7bb46ff9f04da";
    sha256 = "sha256-u17sG3mjJf19euZ0CHvJwnvhb16F3WyAQt/w+RZFu1Y=";
  };

  propagatedBuildInputs = [
    aiohttp
  ] ++ lib.optionals withVoice [
    libopus
    pynacl
    ffmpeg
  ];

  patchPhase = ''
    substituteInPlace "discord/opus.py" \
      --replace "ctypes.util.find_library('opus')" "'${libopus}/lib/libopus.so.0'"
    substituteInPlace requirements.txt \
      --replace "aiohttp>=3.6.0,<3.8.0" "aiohttp>=3.6.0,<4"
  '' + lib.optionalString withVoice ''
    substituteInPlace "discord/player.py" \
      --replace "executable='ffmpeg'" "executable='${ffmpeg}/bin/ffmpeg'"
  '';

  # Only have integration tests with discord
  doCheck = false;

  pythonImportsCheck = [
    "discord"
    "discord.file"
    "discord.member"
    "discord.user"
    "discord.state"
    "discord.guild"
    "discord.webhook"
    "discord.ext.commands.bot"
  ];

  meta = with lib; {
    description = "Python wrapper for the Discord API";
    homepage = "https://discordpy.rtfd.org/";
    license = licenses.mit;
    maintainers = with maintainers; [ ivar ];
  };
}
