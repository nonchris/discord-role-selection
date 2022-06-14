# role selection bot
A first approach to a role-selection-bot for discord using drop down menus and slash commands.  

## setup
##### Using pip to install the bot as editable package:  
` python3 -m pip install -e .`  
`export TOKEN="your-key"`  
`discord-bot`  
##### Or using the launch script:  
`pip install -r requirements.txt`  
`export TOKEN="your-key"`   
`python3 ~/git/discord-bot/launcher.py`  

#### optional env variables
| parameter |  description |
| ------ |  ------ |
| `PREFIX="b!"`  | Command prefix |
| `VERSION="unknown"` | Version the bot is running |
| `OWNER_NAME="unknwon"` | Name of the bot owner |
| `OWNER_ID="100000000000000000"` | ID of the bot owner |
| `ACTIVITY_NAME=f"{PREFIX}help"`| Activity bot plays |  
|`ROLES_JSON="data/roles.json"` | The file where the roles to select can be found |

The shown values are the default values that will be loaded if nothing else is specified.  
Expressions like `{PREFIX}` will be replaced by during loading the variable and can be used in specified env variables.

Set those variables using env-variables (suggested):  
`export PREFIX="b!"`  
Or use a json-file expected at: `./data/config.json` like:  
```json
{
  "TOKEN": "[your-token]",
  "PREFIX": "b!"
}
```

_If a variable is set using env and json the **the environment-variable replaces the json**!_

### example for roles.json
The first key is the server id, then the key `roles` and then the name of the menu.  
```json
{
    "446373739740004352": {
        "roles": {
            "character": [
                448617700386668574,
                448617700399382531
            ],
            "notification": [
                460073915327184900,
                570904869138071572
            ]
        }
    }
}
```

## features
This bot does 'nothing' but is completely functional!  
_What is does:_  
* setup logging
* scan env variables for a more customizable behaviour
* overwrite `on_ready()` function for information at startup
* make bot react to custom prefix and mention
* add more advanced help command
* register example cog with `b!ping` command
* util functions for easy embed creation, id extraction and more

Note:  
The bot uses all intents by default, those are required for such simple things like 'display member-count at startup'.  
You need to enable those intents in the discord developers portal under "Application/Bot/Privileged Gateway Intents".  
It's possible reconfigure the requested intents in `main.py` if you don't need them.  
But I'd suggest using them all for the beginning, especially if you're relatively new to discord.py.

### documentation
In order to render this documentation, just call `doxygen`
