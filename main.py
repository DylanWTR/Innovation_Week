import discord
from discord.ext import commands
import asyncio
import random
from collections import Counter
import aiohttp
import io

from decouple import config

BOT_TOKEN = config('BOT_TOKEN')

user_roles = {}
available_roles = [
    "Criminel", "Criminel", "Criminel",
    "Le Détective", "Le Garde du corps", "La Pharmacienne",
    "L'Informateur", "Le Traître", "L'Avocat", "Le Chasseur urbain"
]

assigned_roles_counter = Counter()

role_images = {
    "Criminel": "https://i.imgur.com/zBUL9WZ.png",
    "Le Détective": "https://i.imgur.com/EwXpxtf.png",
    "Le Garde du corps": "https://i.imgur.com/ML9XCwr.png",
    "La Pharmacienne": "https://i.imgur.com/bGbT13H.png",
    "L'Informateur": "https://i.imgur.com/TXZzDUI.png",
    "Le Traître": "https://i.imgur.com/tMClEIF.png",
    "L'Avocat": "https://i.imgur.com/DxboWUE.png",
    "Le Chasseur urbain": "https://i.imgur.com/UDPWZyj.png",
}

role_descriptions = {
    "Criminel": "**Criminels** : Ils représentent la menace principale pour les citoyens et doivent être équilibrés en nombre pour ne pas être trop dominants ni trop faibles.",
    "Le Détective": "**Détective** : Pour permettre aux citoyens de gagner des informations chaque nuit.",
    "Le Garde du corps": "**Garde du corps** : Pour protéger un citoyen des Criminels chaque nuit.",
    "La Pharmacienne": "**Pharmacienne** : Elle ajoute un élément de stratégie en décidant quand utiliser ses médicaments pour sauver ou éliminer un joueur.",
    "L'Informateur": "**Informateur** : Pour avoir une chance supplémentaire de découvrir un Criminel.",
    "Le Traître": "**Traître** : Ajoute de la tension en ayant un joueur dont l'objectif diffère des Criminels habituels.",
    "L'Avocat": "**Avocat** : Pour ajouter un élément de stratégie lors des votes de jour.",
    "Le Chasseur urbain": "**Chasseur urbain** : Un élément dissuasif contre le vote impulsif et une protection supplémentaire contre les attaques nocturnes.",
}

intents = discord.Intents.all()
intents.reactions = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

@bot.command(name='startgame', aliases=['$startgame'])
async def start_game(ctx):
    if ctx.channel.name == "aventure":
        await ctx.send("Le jeu a commencé avec une phase de nuit !")
        await night_phase(ctx)

async def night_phase(ctx):
    fake_players = ["Joueur1", "Joueur2", "Joueur3", "Joueur4", "Joueur5", "Joueur6", "Joueur7", "Joueur8", "Joueur9", "Joueur10"]
    for player in fake_players:
        role = random.choice(available_roles)

        if assigned_roles_counter[role] >= available_roles.count(role):
            available_roles.remove(role)
            if not available_roles:
                await ctx.send("Tous les rôles ont été distribués.")
                break

        user_roles[player] = role
        assigned_roles_counter[role] += 1
        await send_role_and_image(ctx, player, role)
        await asyncio.sleep(1)

    await ctx.send("---------------------------------------------------------")
    await ctx.send("Phase de nuit : Les Criminels éliminent un joueur.")
    eliminated_player = random.choice(fake_players)
    await ctx.send(f"Les Criminels ont éliminé {eliminated_player}.")
    fake_players.remove(eliminated_player)
    del user_roles[eliminated_player]
    await ctx.send(f"Joueurs restants : {', '.join(fake_players)}")
    await asyncio.sleep(1)

    await asyncio.sleep(1)
    await day_phase(ctx)

async def day_phase(ctx):
    await ctx.send("---------------------------------------------------------")
    await ctx.send("Phase de jour : Discussion, vote, et élimination.")
    await asyncio.sleep(1)
    await asyncio.sleep(1)

    if "Criminel" not in user_roles.values():
        await ctx.send("Les Villageois gagnent ! Tous les Criminels ont été éliminés.")
    elif list(user_roles.values()).count("Criminel") >= len(user_roles) - list(user_roles.values()).count("Criminel"):
        await ctx.send("Les Criminels gagnent ! Ils ont pris le contrôle du village.")

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

            if len(available_roles) > 0:
                assigned_role_name = random.choice(available_roles)
                available_roles.remove(assigned_role_name)
                user_roles[user.id] = assigned_role_name

                await send_role_and_image(user, user.display_name, assigned_role_name)

@bot.command(name='end', aliases=['$end'])
async def end_game(ctx):
    if ctx.channel.name == "aventure":
        await ctx.channel.delete()

async def send_role_and_image(user, player, role):
    if role in role_images:
        image_url = role_images[role]
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_bytes = await resp.read()
                    file = discord.File(io.BytesIO(image_bytes), filename="role_image.png")
                    description = role_descriptions.get(role, "No description available.")
                    await user.send(f"Votre rôle dans l'aventure est **{role}**.")
                    await user.send(file=file)
                    await user.send(description)
                    await user.send("---------------------------------------------------------")
                else:
                    await user.send(f"Votre rôle dans l'aventure est **{role}**. (Image not found)")
    else:
        await user.send(f"Votre rôle dans l'aventure est **{role}**.")

bot.run(BOT_TOKEN)
