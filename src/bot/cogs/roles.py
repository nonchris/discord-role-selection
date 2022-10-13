import json
from typing import Literal, Union, Optional, Any

import discord
from discord import app_commands
from discord.ext import commands

from ..log_setup import logger
from ..environment import ROLES_JSON
from ..utils import utils as utl


class RoleDropdown(discord.ui.Select):
    def __init__(self, guild: discord.Guild, member: discord.Member,
                 roles_to_choose: list[dict[str, Union[int]]], name="", is_enumeration=True, number=0, min_values=0,
                 max_values=25):

        self.pool_roles: list[dict[str, Union[int]]] = roles_to_choose
        self.roles = self.convert_ids_to_roles(guild)

        # options specific for member
        self.sel_options = self.make_options(member)

        super().__init__(placeholder=f"{f'#{number}' if is_enumeration > 1 else ''} Choose the {name} you want :)",
                         min_values=min_values,
                         max_values=max_values,
                         options=self.sel_options)

    def convert_ids_to_roles(self, guild: discord.Guild) -> list[discord.Role]:
        self.roles = [guild.get_role(role["id"]) for role in self.pool_roles]
        return self.roles

    def make_options(self, member: discord.Member) -> list[discord.SelectOption]:
        """ Make options specific for member from select options """
        # wrap each role inside an SelectOption
        self.sel_options = []
        for role_dict in self.pool_roles:
            guild: discord.Guild = member.guild
            role: discord.Role = guild.get_role(role_dict["id"])

            # decide where to get the emoji from
            emoji = role.unicode_emoji or utl.get_emote(guild, role_dict["emoji"])
            option = discord.SelectOption(label=f"{role.name}",
                                          value=str(role.id),
                                          description=f"See the #{role.name} channel",
                                          emoji=emoji)

            # see if role shall be selected because user has this role already
            if role in member.roles:
                option.default = True

            self.sel_options.append(option)

        return self.sel_options

    async def callback(self, interaction: discord.Interaction, reason="User chosen using dropdown menu"):
        guild = interaction.guild
        member: discord.Member = interaction.user

        # all roles from that menu the user has at the moment (roles not given trough that menu removed via intersect)
        member_roles_set = set(member.roles).intersection(self.roles)
        selected_roles_set = set([guild.get_role(int(selection)) for selection in self.values])

        # roles member selected but does not have yet
        to_give = selected_roles_set.difference(member_roles_set)
        await member.add_roles(*to_give, reason=reason)

        # roles member has but does not want
        to_remove = member_roles_set.difference(selected_roles_set)
        await member.remove_roles(*to_remove, reason=reason)

        await interaction.response.send_message(f"Your roles were updated", ephemeral=True)


class DropdownMaker:
    def __init__(self, guild: discord.Guild,member: discord.Member,
                 pool="character",
                 path_to_roles_json=ROLES_JSON):
        self.guild = guild
        self.member = member
        self.name = pool
        self.roles_json: dict[str, list[int]] = {}

        # read in json and get the according roles
        self.pool_roles: list[dict] = self.read_json(path_to_roles_json, guild, key=pool)

        # self.roles: list[discord.Role] = self.convert_ids_to_roles(guild)

    def read_json(self, file: str, guild: discord.Guild, key: str) -> list[dict[str, Any]]:
        """ Read json and return role IDs """
        with open(file, "r") as f:
            self.roles_json = json.load(f)

        # convert roles-keys into integers
        self.pool_roles = list(self.roles_json[str(guild.id)]["roles"][key].values())
        return self.pool_roles

    def get_role_menus(self, max_len=25, min_values=0, max_values=None) -> list[RoleDropdown]:
        # if no limit is set, assume that all options can be chosen
        if max_values is None:
            max_values = max_len

        # holds list in which the whole list of options is split into
        # these lists will be used to generate the drop down menus
        divided_options_list = []

        # holds the options that will be wrapped inside a single DropDown menu
        menu_items = []
        for i, role in enumerate(self.pool_roles):

            # add role to menu_items
            menu_items.append(role)

            # menu is full, add it to list or this was the last element, so we need to add this un-full option menu
            if len(menu_items) == max_len or i == len(self.pool_roles) - 1:
                divided_options_list.append(menu_items)

                menu_items = []  # reset list, elements from that list are now options

        # only enumerate when more than one menu is generated
        is_enumeration = True if len(divided_options_list) > 1 else False
        # holds all dropdown-menu items created
        dropdown_list = []
        for i, divided_option in enumerate(divided_options_list):
            dropdown_list.append(RoleDropdown(self.guild, self.member, divided_option,
                                              name=self.name,
                                              is_enumeration=is_enumeration,
                                              number=i + 1,  # start counting at one
                                              min_values=min_values,
                                              # max options is either the allowed max or all options in dropdown
                                              max_values=min(max_values, len(divided_option))))

        return dropdown_list


class DropdownView(discord.ui.View):
    """ UI helper that warps the options"""

    def __init__(self, *drop_down_items: discord.ui.Select, timeout=None):
        super(DropdownView, self).__init__(timeout=timeout)
        for item in drop_down_items:
            self.add_item(item)


"""
Menu to select which drop-down is wanted
"""


class DropDownSendButton(discord.ui.Button):
    """ Button representing a pool """
    def __init__(self, pool: str):
        super().__init__()
        self.label = pool
        self.style = discord.ButtonStyle.green

    async def callback(self, interaction: discord.Interaction):
        """ Send a dropdown for the selected pool """

        # issue sending of the selected drop-down menu
        await AutoRoleMenu.send_select_roles(interaction, pool=self.label, max_len=20)


class RoleMenuButtons(discord.ui.View):
    """ Buttons that represent all pools to select from """
    def __init__(self, bot: commands.Bot, guild_id_str: str, timeout=None):
        super().__init__(timeout=timeout)
        self.bot = bot

        # add buttons for all pools on this server
        for pool in get_roles_dict()[guild_id_str]["roles"].keys():
            self.add_item(DropDownSendButton(pool))


"""
Manage json
"""

RolesJson = dict[str, dict[str, dict[str, Union[list[int], dict[str, dict[str, Any]]]]]]


def get_roles_dict() -> RolesJson:
    """ Wrapper to read the json"""
    with open(ROLES_JSON, "r") as f:
        return json.load(f)


def ensure_latest_json_format():
    """ Function that migrates old json formats to newer structures """

    roles_json = get_roles_dict()
    was_changed = False

    # sanitize first change:
    # pools contain no longer a list of role-ids
    # they contain dicts, one per role containing even deeper dicts that hold id and more information
    for guild, guild_dict in roles_json.items():
        guild_roles_dict = guild_dict["roles"]
        # zoom into pools
        for pool, roles_array in guild_roles_dict.items():
            # check if this is still a list, if yes build new dict with deeper dicts
            if isinstance(roles_array, list):
                guild_roles_dict[pool] = {str(role): {"id": role, "emoji": None} for role in roles_array}
                was_changed = True

    if was_changed:
        with open(ROLES_JSON, "w") as f:
            json.dump(roles_json, f, indent=4)



def get_dict_ensure_guild_entry(inter: discord.Interaction) -> tuple[RolesJson, str]:
    """
    returns: read json with potentially added hey and guild key
    """

    # make sure that the read in data is up-to-date
    ensure_latest_json_format()

    with open(ROLES_JSON, "r") as f:
        roles_json = json.load(f)

    # check if json has already the needed structure
    was_changed = False  # track if keys were added

    guild_key = utl.extract_guild_id_str_from_interaction(inter)
    if guild_key not in roles_json:
        roles_json[guild_key] = {}
        was_changed = True

    if "roles" not in roles_json[guild_key]:
        roles_json[guild_key]["roles"] = {}
        was_changed = True

    # only write if contents were changed
    if was_changed:
        with open(ROLES_JSON, "w") as f:
            json.dump(roles_json, f, indent=4)

    return roles_json, guild_key


class AutoRoleMenu(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @staticmethod
    async def send_select_roles(interaction: discord.Interaction,
                                pool="character",
                                path_to_roles_json=ROLES_JSON,
                                max_len=25,
                                min_values=0,
                                max_values=25,
                                ephemeral=True):
        """ Generate role dropdowns """

        # create the view containing our dropdown
        # get an object that can generate as much dropdowns as we need
        options_maker = DropdownMaker(interaction.guild, interaction.user,
                                      pool=pool,
                                      path_to_roles_json=path_to_roles_json)
        # get option menus
        options = options_maker.get_role_menus(max_len=max_len, min_values=min_values, max_values=max_values)
        # create view
        view = DropdownView(*options)

        # sending a message containing our view
        extra_info = (f"There are {len(options)} menus to select roles from, "
                      f"because they don't fit in one single menu :)" if len(options) > 1 else "")
        await interaction.response.send_message(
            'Pick the roles you want:\n' + extra_info, view=view, ephemeral=ephemeral)

    @app_commands.command(name="roles", description="Get a menu with all role-menus that are available")
    async def send_roles_menu(self, interaction: discord.Interaction, ephemeral: Optional[bool] = True):
        """Get a menu with all role-menus that are available"""
        get_dict_ensure_guild_entry(interaction)  # ensure that dict is there  # TODO: maybe just do it on join of bot
        roles_buttons = RoleMenuButtons(self.bot, utl.extract_guild_id_str_from_interaction(interaction))

        # check if there are any buttons/ pools to send
        if len(roles_buttons.children) < 1:
            await interaction.response.send_message(
                "There are no role pools setup yet. Please ask an administrator to set it up."
            )
            return

        # if there is only one pool, we can skip the buttons
        if len(child := roles_buttons.children) == 1:
            await child[0].callback(interaction)
            return

        # send buttons for selection
        await interaction.response.send_message('Select your menu:\n', view=roles_buttons, ephemeral=ephemeral)

    @app_commands.command(
        name="update_roles",
        description="Add or remove a roles and pools from the selection database")
    @app_commands.guild_only
    async def add_role(self, interaction: discord.Interaction, role: discord.Role,
                       pool: str, action: Literal["add", "remove"]):
        """ Add or remove a key from the selection database """

        member: discord.Member = interaction.guild.get_member(interaction.user.id)
        if not member.guild_permissions.ban_members:
            await interaction.response.send_message("Only users with ban permissions can do this.", ephemeral=False)
            return

        roles_json, guild_key = get_dict_ensure_guild_entry(interaction)

        pool_info = ""  # may contain extra info if a pool was added or deleted
        # TODO: validate if pool has it's own slash command so it can be addressed from the user via discord
        # TODO: validate that there are only as many pools as fitting into one button menu
        # add pool if operation is 'add' and key does not exist
        if pool not in roles_json[guild_key]["roles"] and action == "add":
            roles_json[guild_key]["roles"][pool] = {}
            logger.info(f"Pool '{pool}' was created, invoked by '{interaction.user.id}'")
            pool_info = f"New pool was created: '{pool}'"

        # reject if pool does not exist and action is remove
        if pool not in roles_json[guild_key]["roles"] and action == "remove":
            await interaction.response.send_message(f"Pool '{pool}' does not exist")
            return

        # zoom in
        target: dict[str, dict[str, Any]] = roles_json[guild_key]["roles"][pool]
        # okay, shall be added
        if action == "add":
            print(roles_json[guild_key]["roles"])
            print(target)
            # TODO: Check if already entered
            target[str(role.id)] = {"id": role.id, "emoji": None}
            logger.info(f"Pool '{pool}': Added '{role.name}' with id ({role.id}), invoked by '{interaction.user.id}'")

        # shall be removed
        # test if object is in list
        if action == "remove":
            if not target.get(str(role.id), None):
                await interaction.response.send_message(f"Role '{role.name}' in not in pool '{pool}'")
                return

            # trigger removal
            del target[str(role.id)]
            logger.info(f"Pool '{pool}': Removed '{role.name}' with id ({role.id}), invoked by '{interaction.user.id}'")

            # delete pool if empty
            if len(target) < 1:
                del roles_json[guild_key]["roles"][pool]
                logger.info(f"Deleted empty pool '{pool}' on guild '{guild_key}'")
                pool_info = f"Empty pool was deleted: '{pool}'"

        # write changes
        with open(ROLES_JSON, "w") as f:
            json.dump(roles_json, f, indent=4)

        # response
        await interaction.response.send_message(
            f"The role {role.mention} was {'added to' if action == 'add' else 'removed from'} '{pool}'\n{pool_info}",
            ephemeral=False)


async def setup(bot):
    await bot.add_cog(AutoRoleMenu(bot))
