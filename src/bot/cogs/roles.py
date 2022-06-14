import json
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from ..environment import ROLES_JSON


class RoleDropdown(discord.ui.Select):
    def __init__(self, guild: discord.Guild, member: discord.Member,
                 roles_to_choose: list[discord.Role], name="", is_enumeration=True, number=0, min_values=0,
                 max_values=25):

        self.roles: list[discord.Role] = roles_to_choose

        # options specific for member
        self.sel_options = self.make_options(member)

        super().__init__(placeholder=f"{f'#{number}' if is_enumeration > 1 else ''} Choose the {name} you want :)",
                         min_values=min_values,
                         max_values=max_values,
                         options=self.sel_options)

    def make_options(self, member: discord.Member) -> list[discord.SelectOption]:
        """ Make options specific for member from select options """
        # wrap each role inside an SelectOption
        self.sel_options = []
        for role in self.roles:
            option = discord.SelectOption(label=f"{role.name}", value=str(role.id),
                                          description=f"See the #{role.name} channel", emoji=role.unicode_emoji)

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
    def __init__(self, guild: discord.Guild, member: discord.Member,
                 roles_menu="character",
                 path_to_roles_json="data/roles.json"):
        self.guild = guild
        self.member = member
        self.name = roles_menu
        self.roles_json: dict[str, list[int]] = {}

        self.role_ids: list[int] = self.read_json(path_to_roles_json, guild, key=roles_menu)

        self.roles: list[discord.Role] = self.convert_ids_to_roles(guild)

    def read_json(self, file: str, guild: discord.Guild, key: str) -> list[int]:
        with open(file, "r") as f:
            self.roles_json = json.load(f)

        self.role_ids = self.roles_json[str(guild.id)]["roles"][key]
        return self.role_ids

    def convert_ids_to_roles(self, guild: discord.Guild) -> list[discord.Role]:
        self.roles = [guild.get_role(r_id) for r_id in self.role_ids]
        return self.roles

    def get_role_menus(self, max_len=25, min_values=0, max_values=None) -> list[RoleDropdown]:
        # if no limit is set, assume that all options can be chosen
        if max_values is None:
            max_values = max_len

        # holds list in which the whole list of options is split into
        # these lists will be used to generate the drop down menus
        divided_options_list = []

        # holds the options that will be wrapped inside a single DropDown menu
        menu_items = []
        for i, role in enumerate(self.roles):

            # add role to menu_items
            menu_items.append(role)

            # menu is full, add it to list or this was the last element, so we need to add this un-full option menu
            if len(menu_items) == max_len or i == len(self.roles) - 1:
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

    def __init__(self, *drop_down_items: discord.ui.Select):
        super(DropdownView, self).__init__()
        for item in drop_down_items:
            self.add_item(item)


class AutoRoleMenu(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(name="roles", help="Roles roles roles")
    async def colour(self, ctx: commands.Context):
        """Select roles you wanna have"""

        # Create the view containing our dropdown
        menu = RoleDropdown(ctx.guild, ctx.author)
        view = DropdownView(menu)

        # Sending a message containing our view
        await ctx.send('Pick the roles you want:', view=view)


async def setup(bot):
    await bot.add_cog(AutoRoleMenu(bot))
