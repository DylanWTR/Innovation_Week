import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.all()
intents.reactions = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

@bot.command(name='start')
async def game(ctx):
    message = await ctx.send("Réagissez à l'emoji pour commencer le jeu.")
    await message.add_reaction('🚀')

@bot.event
async def on_reaction_add(reaction, user):
    channel_name = "aventure"
    if user == bot.user:
        return
    if reaction.message.content == "Réagissez à l'emoji pour commencer le jeu.":
        await asyncio.sleep(10)
        role = discord.utils.get(reaction.message.guild.roles, name='aventure')
        if role:
            await user.add_roles(role)
            overwrites = {
                reaction.message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                role: discord.PermissionOverwrite(read_messages=True)
            }
            channel = await reaction.message.guild.create_text_channel(channel_name, overwrites=overwrites)
            await channel.send(f"{user.mention}, Bienvenue dans l'aventure")
        else:
            print("Rôle 'aventure' introuvable.")

bot.run('MTE2NjM1MzI5Mjg0MzAyODUwMA.G3M7zZ.OBilbgmhY9pGcUdRq0BG539U7nGyj0B38ZCdLs')
