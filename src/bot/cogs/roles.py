import json
from typing import Iterable

import discord
from discord.ext import commands


class RoleDropdown(discord.ui.Select):
    def __init__(self, guild: discord.Guild, member: discord.Member,
                 roles_menu="character",
                 path_to_roles_json="data/roles.json"):
        self.roles_json: dict[str, list[int]] = {}

        self.role_ids: list[int] = self.read_json(path_to_roles_json, key=roles_menu)

        self.roles: list[discord.Role] = self.convert_ids_to_roles(guild)

        self.sel_options = self.make_options(member)

        super().__init__(placeholder=f"Choose the {roles_menu} you want :)",
                         min_values=0,
                         max_values=len(self.sel_options) - 1,
                         options=self.sel_options),

    def read_json(self, file: str, key: str) -> list[int]:
        with open(file, "r") as f:
            self.roles_json = json.load(f)

        self.role_ids = self.roles_json["roles"][key]
        return self.role_ids

    def convert_ids_to_roles(self, guild: discord.Guild) -> list[discord.Role]:
        self.roles = [guild.get_role(r_id) for r_id in self.role_ids]
        return self.roles

    def make_options(self, member: discord.Member):
        self.sel_options = []
        print(self.roles)
        for role in self.roles:
            print(role)
            option = discord.SelectOption(label=str(role.id), description=f"{role.name}", emoji=role.unicode_emoji)
            if role in member.roles:
                option.default = True

            self.sel_options.append(option)

        return self.sel_options

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.message.author

        # all roles from that menu the user has at the moment (roles not given trough that menu removed via intersect)
        member_roles_set = set(member.roles).intersection(self.roles)
        selected_roles_set = set([guild.get_role(int(selection)) for selection in self.values])

        # roles member selected but does not have yet
        to_give = selected_roles_set.difference(member_roles_set)
        await member.add_roles(*to_give)

        # roles member has but does not want
        to_remove = member_roles_set.difference(selected_roles_set)
        await member.remove_roles(*to_remove)

        await interaction.response.send_message(f"Your roles were updated", ephemeral=True)


class DropdownView(discord.ui.View):
    def __init__(self, drop_down_item: discord.ui.Select):
        super(DropdownView, self).__init__()
        self.add_item(drop_down_item)


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
