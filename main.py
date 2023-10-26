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

@bot.command(name='start')
async def game(ctx):
    message = await ctx.send("La partie de Loup Garou va commencer dans **5 secondes**, réagissez à l'emoji pour être dans la partie!")
    await message.add_reaction('🚀')

@bot.event
async def on_reaction_add(reaction, user):
    channel_name = "aventure"
    if user == bot.user:
        return
    if reaction.message.content == "La partie de Loup Garou va commencer dans **5 secondes**, réagissez à l'emoji pour être dans la partie!":
        await asyncio.sleep(5)
        role = discord.utils.get(reaction.message.guild.roles, name='aventure')
        if role:
            await user.add_roles(role)

            overwrites = {
                reaction.message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                role: discord.PermissionOverwrite(read_messages=True)
            }
            channel = await reaction.message.guild.create_text_channel(channel_name, overwrites=overwrites)

            if len(available_roles) > 0:
                assigned_role_name = random.choice(available_roles)
                available_roles.remove(assigned_role_name)
                user_roles[user.id] = assigned_role_name

                await send_role_and_image(user, assigned_role_name)

                await start_game(channel)

async def start_game(channel):

    await channel.send("**BIENVENUE A TOUS** dans le village de Neopolis. Ce village a récemment été perturbé par la présence de **3 Criminels** qui rôdent la nuit, terrorisant la population. Heureusement, ce village a aussi ses protecteurs, dont **Le Détective**, **Le Garde du corps**, **La Pharmacienne**, **L'Informateur**, **Le Traître**, **L'Avocat**, et **Le Chasseur urbain**. Aujourd'hui, le village se réunit pour tenter de démasquer les Criminels et protéger leurs habitants.\n")
    await asyncio.sleep(2)
    await channel.send("**----------------------------------**\nLes rôles ont été soigneusement mélangés et attribués au hasard. Qui parmi vous jouera le rôle de protecteur, de détective, de criminel ou de traître ? C'est le moment de le découvrir.")
    await asyncio.sleep(2)
    await channel.send("**----------------------------------**\n**Phase de nuit :**\n\nLe soleil se couche sur le village, et la lune prend sa place. Tous les villageois ferment leurs yeux, sauf les Criminels, les Détectives et les Gardes du corps.")
    await asyncio.sleep(2)
    await channel.send("C'est le moment où les Criminels se concertent silencieusement pour choisir leur proie...")
    await asyncio.sleep(2)

    fake_players = ["Alice", "Bob", "Carol", "David", "Emily", "Frank", "Grace", "Henry", "Isabella", "Jack"]

    player_reactions = {}
    voting_message = "C'est l'heure du vote des Criminels ! Choisissez votre cible en réagissant avec l'emoji correspondant.\nVous avez **10 secondes** !\n\n"

    numbered_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    for i, player in enumerate(fake_players):
        if i < len(numbered_emojis):
            emoji = numbered_emojis[i]
            player_reactions[emoji] = player
            voting_message += f"{emoji} {player}\n"

    voting_message = await channel.send(voting_message)

    for emoji in player_reactions.keys():
        await voting_message.add_reaction(emoji)

    await asyncio.sleep(10)
    await channel.send("Les Criminels ont voté. Le joueur le plus voté est **David**.")
    await channel.send("**David** était **L'informateur** !")
    await asyncio.sleep(2)
    await channel.send("**----------------------------------**\n**Phase de jour :**\n\nLe soleil se lève sur le village, révélant les horreurs de la nuit. Les villageois discutent de l'élimination de **David**, partageant leurs soupçons et leurs doutes.\n\n")


@bot.command(name='end', aliases=['$end'])
async def end_game(ctx):
    if ctx.channel.name == "aventure":
        await ctx.channel.delete()

async def send_role_and_image(user, role):
    if role in role_images:
        image_url = role_images[role]
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_bytes = await resp.read()
                    file = discord.File(io.BytesIO(image_bytes), filename="role_image.png")
                    description = role_descriptions.get(role, "No description available.")
                    await user.send(f"Votre rôle dans l'aventure est **{role}**.\n\n{description}", file=file)

                else:
                    await user.send(f"Votre rôle dans l'aventure est **{role}**. (Image not found)")
    else:
        await user.send(f"Votre rôle dans l'aventure est **{role}**.")

bot.run(BOT_TOKEN)


        # "**-- INTRODUCTION DES PERSONNAGES --**\n\n"
        # "**Les Criminels** : Ils choisissent une victime à éliminer chaque nuit. Leur objectif est de devenir majoritaires dans le village.\n\n"
        # "**Le Détective** : Il enquête sur un joueur chaque nuit pour découvrir son vrai rôle. Son but est de démasquer les Criminels et protéger les citoyens.\n\n"
        # "**Le Garde du corps** : Il peut protéger un joueur des Criminels chaque nuit. Son rôle est de sauver les citoyens des attaques nocturnes.\n\n"
        # "**La Pharmacienne** : Elle possède deux médicaments - un pour sauver une victime et l'autre pour éliminer un joueur. Elle doit choisir judicieusement quand utiliser ses pouvoirs.\n\n"
        # "**L'Informateur** : Il recueille des informations sur un groupe de 3 personnes pour voir s'il y a des Criminels parmi eux. Sa capacité peut aider à identifier les Criminels.\n\n"
        # "**Le Traître** : Son objectif est d'être le dernier joueur en vie. Il peut trahir et éliminer un autre Criminel pour atteindre son but.\n\n"
        # "**L'Avocat** : Il peut immuniser un joueur contre les votes. Son rôle est de manipuler les votes de jour pour protéger son équipe.\n\n"
        # "**Le Chasseur Urbain** : S'il est éliminé par les citoyens, ceux qui ont des pouvoirs les perdent. Il survit à la première attaque des Criminels et peut être un atout précieux pour les citoyens.\n\n"
