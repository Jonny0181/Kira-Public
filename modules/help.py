import discord
from discord.ext import commands
from utils import checks

class Help(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="help")
	@commands.check(checks.can_embed)
	async def _help(self, ctx, *, command: str=None):
		"""Shows you a list of commands when a module is specified after."""
		modules = ['music', 'Music', 'Dev', 'dev', 'Info', 'info', 'Mod', 'mod', 'Fun', 'fun', '1', '2', '3', '4', '5']
		if command is None:
			e = discord.Embed(colour=0x36393E)
			e.set_author(icon_url=self.bot.user.avatar_url, name=f"Kira's Modules:")
			e.description = "\n**1)** Dev\n**2)** Info\n**3)** Music\n**4)** Mod\n**5)** Fun\n"
			e.description += f"\nNeed help on on how to use the help command? Use {ctx.prefix}help help."
			e.set_thumbnail(url=self.bot.user.avatar_url)
			await ctx.send(embed=e)
			return
		if command is not None:
			if command == "help":
				e = discord.Embed()
				e.colour = 0x36393E
				e.set_author(icon_url=self.bot.user.avatar_url, name=f"Command Help:")
				e.description = "Well, looks like someone needs help on how to use this command.\n"
				e.description += "No problem, let's get started.\n"
				e.description += f"First, you need to know the basics. The command starter is {ctx.prefix}help.\n\n"
				e.description += f"__**Examples:**__\n{ctx.prefix}help play\n{ctx.prefix}help Music\n{ctx.prefix}help myplaylists show\n\n"
				e.description += "Well that's about it! If you still are not getting it, take a look at the gif attached below. 👇"
				e.set_image(url="http://lolis.is-my-k.ink/3c562961dc.gif")
				await ctx.send(embed=e)
				return
			elif command in modules:
				if command in ('1', 'Dev', 'dev'):
					module = "Dev"
				elif command in ('2', 'Info', 'info'):
					module = "Info"
				elif command in ('3', 'Music', 'music'):
					module = "Music"
				elif command in ('4', 'Mod', 'mod'):
					module = "Mod"
				elif command in ('5', 'Fun', 'fun'):
					module = "Fun"
				await self.send_module_help(ctx, module)
			else:
				cmd = ctx.bot.get_command('{}'.format(command))
				if cmd:
					a = discord.Embed(colour=0x36393E)
					a.set_author(icon_url=self.bot.user.avatar_url, name=f"Command Help:")
					a.description = f"{cmd.name} {cmd.signature}\n"
					a.description += f"{cmd.short_doc}\n\n"
					try:
						if cmd.group:
							a.description += "__**Sub Commands:**__\n"
							e = cmd.commands
							m = ""
							for f in e:
								m += f"**{f.name} -** {f.short_doc}\n"
							a.description += m
					except:
						pass
					a.set_thumbnail(url=self.bot.user.avatar_url)
					return await ctx.send(embed=a)
				else:
					return await ctx.send("<:uncheck:433159805117399050> Sorry, I couldn't find that command.")
		
	async def send_module_help(self, ctx, module):
		"""You can't access this command list..."""
		if module == "Dev":
			if ctx.author.id == 170619078401196032:
				cmds = await self.buildCogHelp('Dev', 'REPL', 'Jishaku')
			else:
				return await ctx.send("Oof, you're not a dev. No need to see the commands if you can't use them.")
		elif module == "Mod":
			cmds = await self.buildCogHelp('Mod', 'Settings')
		elif module == "Info":
			cmds = await self.buildCogHelp('Info')
		elif module == "Music":
			cmds = await self.buildCogHelp('Music')
		elif module  == "Fun":
			cmds = await self.buildCogHelp('Fun', 'Sounds')
		e = discord.Embed(colour=0x36393E)
		e.description = f"{cmds}"
		e.set_author(name=f"{module} Commands:", icon_url=ctx.author.avatar_url)
		e.set_thumbnail(url=self.bot.user.avatar_url)
		return await ctx.send(embed=e)
		
	async def buildCogHelp(self, *modules):
		formatted = ""
		cog_fmt = "**{cmd_name} -** {doc}\n"
		for m in modules:
			for c in self.bot.commands:
				if c.cog_name == m and not (c.hidden):
					if c.short_doc == '':
						doc = "No doc specified."
					else:
						doc = c.short_doc
					formatted += cog_fmt.format(cmd_name=c.name, doc=doc)
			return formatted.replace("```", "")
			
def setup(bot):
	bot.remove_command("help")
	bot.add_cog(Help(bot))
