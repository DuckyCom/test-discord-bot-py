import discord
import os
from dotenv import load_dotenv
from flask import Flask
import threading

import plugins.dwbapi as dwb
from embedBuilder import buildEmbed as emb
from handlers.commandManager import commandManager
from plugins.shrineoforder import order
from plugins.analytics import plot_breakdown

intents = discord.Intents.default()
intents.message_content = True

#constants
load_dotenv()
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
client = discord.Client(intents=intents)
commands = commandManager(client)
commands.loadCommands()

# Flask app for UptimeRobot pings
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running", 200

@client.event
async def on_ready():
    print(f'Im fucking poa at {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith(commands.PREFIX):
        await message.channel.send(embed = commands.processCommand(message), reference = message)
    
    if message.type == discord.MessageType.reply:
        referenced = message.reference
        if referenced and referenced.resolved:
            replied_msg = referenced.resolved
            if 'https://deepwoken.co/builder?id=' in replied_msg.content:
                try:
                    link = replied_msg.content.split('https://deepwoken.co/builder?id=')[1].split()[0]
                    build_id = link.split('&')[0]
                    build = dwb.dwbBuild(build_id)
                    if message.content.strip().lower() == 'analytics':

                        buf = plot_breakdown(build, talentBase=dwb.talentBase)
                        file = discord.File(buf, filename="ehp_plot.png")
                        embed = discord.Embed(color=0xffffff)
                        embed.set_image(url="attachment://ehp_plot.png")
                        await message.channel.send(embed=embed, file=file, reference = message)

                    elif message.content.strip().lower() == 'display':
                        embeds = emb.get_deepwoken_build_embed(build_id)
                        for embed in embeds:
                            await message.channel.send(embed=embed, reference = message)
                except Exception as e:
                    await message.channel.send(f'Error fetching build: {str(e)}')

# Run Discord bot in a thread
def run_bot():
    client.run(BOT_TOKEN)

bot_thread = threading.Thread(target=run_bot)
bot_thread.start()

# Run Flask app
app.run(host='0.0.0.0', port=10000)
