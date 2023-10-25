import discord
from discord.ext import commands
import asyncio
import random

from decouple import config

# Load the bot token from the .env file
BOT_TOKEN = config('BOT_TOKEN')

# Define a dictionary to store user-role mappings
user_roles = {}

# Define a list of available roles
available_roles = [
    "Criminel", "Criminel", "Criminel",
    "Le Détective", "Le Garde du corps", "La Pharmacienne",
    "L'Informateur", "Le Traître", "L'Avocat", "Le Chasseur urbain"
]

intents = discord.Intents.all()
intents.reactions = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    # Print a message in the terminal when the bot is ready
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

@bot.command(name='start')
async def game(ctx):
    # Send a message to start the game
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
            # Add the 'aventure' role to the user
            await user.add_roles(role)

            # Set channel permissions to make it visible only to users with the 'aventure' role
            overwrites = {
                reaction.message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                role: discord.PermissionOverwrite(read_messages=True)
            }
            channel = await reaction.message.guild.create_text_channel(channel_name, overwrites=overwrites)
            await channel.send(f"{user.mention}, Bienvenue dans l'aventure")

            # Randomly assign a role to the user from the available roles list
            if len(available_roles) > 0:
                assigned_role_name = random.choice(available_roles)
                available_roles.remove(assigned_role_name)  # Remove the assigned role from the list
                user_roles[user.id] = assigned_role_name

                # Send a direct message to the user with their assigned role
                await user.send(f"Votre rôle dans l'aventure est {assigned_role_name}.")

@bot.command(name='end', aliases=['$end'])
async def end_game(ctx):
    # Check if the command was sent in the "aventure" channel
    if ctx.channel.name == "aventure":
        # Remove the channel
        await ctx.channel.delete()

bot.run(BOT_TOKEN)
