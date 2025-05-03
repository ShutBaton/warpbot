import asyncio
import discord                                  # Discord
from discord import app_commands                # Discord
from discord.ext import commands                # Discord
from discord.voice_client import VoiceClient    # Discord
from discord.ui import View, Button             # Discord
from google import genai                        # Google Gemini
from google.genai import types                  # Google Gemini
from gtts import gTTS                           # Google Text-To-Speech

import os
from dotenv import load_dotenv
import time

from vcgencmd import Vcgencmd                   # Hardware Monitoring

########## SETUP ##########

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

warp_system_instruction = "You are an AI Helper discord bot created by the F1 in Schools (now called STEM Racing) competition team Warp Racing. Warp Racing consists of a team of boys from St. Olave's Grammar School in Orpington, Kent, UK. They won the Lenovo F1 in Schools National Finals (Development Class) in March 2024, gaining the awards of \"1st Place (National Dev. Class Champions)\", \"Fastest Car\", \"Best Engineered Car\" and \"Research and Development\". The user querying you is a discord user, and you are to help them with their task or provide information. Your responses may occasionally be used in a voice channel via text-to-speech."
intents = discord.Intents().all()

bot = commands.Bot(command_prefix='!', intents=intents, activity=discord.Game(name='WarpGame'))

startup_time = None

@bot.event
async def on_ready():
    try:
        print("WarpBot is now online.")
        synced = await bot.tree.sync()
        print(f"All {len(synced)} command(s) have been synced.")
        global startup_time
        startup_time = time.time()
    except Exception as e:
        print(e)

########## GENERAL COMMANDS ##########

# Respond with Pong + Round Trip Latency
@bot.tree.command(name='ping')
async def ping(interaction: discord.Interaction):
    latency = round(interaction.client.latency * 1000)
    await interaction.response.send_message(f"Pong! Latency: {latency}ms", ephemeral=True)

# Respond with Ping + Round Trip Latency
@bot.tree.command(name='pong')
async def pong(interaction: discord.Interaction):
    latency = round(interaction.client.latency * 1000)
    await interaction.response.send_message(f"Ping! Latency: {latency}ms", ephemeral=True)

# Provide about information regarding Bot
@bot.tree.command(name='about')
async def about(interaction: discord.Interaction):
    view = discord.ui.View()
    view.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label="warp-racing.com", url="https://warp-racing.com"))
    await interaction.response.send_message(
        f"Hello {interaction.user.mention}. I am WarpBot, a AI helper created by Warp Racing and powered by the Google Geminiâ¢ 2.0 Flash Large Language Model. I am multilingual and have knowledge of events up to **August 2024**.\n*Please note that each `/ask` command is individual, and does not include previous context.*\n\nGeminiâ¢ is a trademark of Google LLC.",
        ephemeral=True,
        view=view
    )

# Raspberry Pi 5 Hardware Information
@bot.tree.command(name='hardware')
async def hardware(interaction: discord.Interaction):
    vcgm = Vcgencmd()
    temp = vcgm.measure_temp()
    clock = int(vcgm.measure_clock('arm')/1000000)
    throttled = vcgm.get_throttled()['breakdown']['2']
    await interaction.response.send_message(f"This Bot is running on a **Raspberry Pi 5 8GB with 512GB of SSD Storage**.\n\n*Current Hardware Info:*\nTemperature: `{temp}C`\nClock: `{clock}MHz`\nThrottled: `{throttled}`", ephemeral=True)

# Uptime Information
@bot.tree.command(name='uptime')
async def uptime(interaction: discord.Interaction):
    if startup_time:
        uptime_seconds = int(time.time() - startup_time)
        
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        uptime_str = f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds"
        
        await interaction.response.send_message(f"Bot uptime: {uptime_str}", ephemeral=True)
    else:
        await interaction.response.send_message("Uptime could not be determined.", ephemeral=True)

# Get the avatar of a user
@bot.tree.command(name='avatar')
async def avatar(interaction: discord.Interaction, user: discord.User = None):
    if user is None:
        user = interaction.user

    avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
    await interaction.response.send_message(f"{user.mention}'s avatar: {avatar_url}", ephemeral=True)

########## ASK COMMAND ##########

@bot.tree.command(name='ask')
@app_commands.describe(query = "What do you want to know?")
async def ask(interaction: discord.Interaction, query: str):
    try:

        ########## RESPONSE LOGIC ##########

        async def respond(is_voice):

            ########## TEXT GENERATION ##########

            response = client.models.generate_content_stream(
                model="gemini-2.0-flash",
                contents=f"{interaction.user.mention}'s query: {query}",
                config=types.GenerateContentConfig(
                    max_output_tokens=600,
                    temperature=1,
                    safety_settings=[
                        types.SafetySetting(
                            category="HARM_CATEGORY_HARASSMENT",
                            threshold="BLOCK_MEDIUM_AND_ABOVE",  # Block some
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_HATE_SPEECH",
                            threshold="BLOCK_MEDIUM_AND_ABOVE",  # Block some
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold="BLOCK_LOW_AND_ABOVE",  # Block most
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold="BLOCK_MEDIUM_AND_ABOVE",  # Block some
                        ),
                    ],
                    response_mime_type="text/plain",
                    system_instruction=warp_system_instruction
                )
            )

            sent_message = await interaction.followup.send("Generating...")

            current_response = ""

            for chunk in response:
                current_response += chunk.text
                
                if len(current_response) >= 2000:
                    if is_voice:
                        await interaction.followup.send("WarpBot's Response is too large for Discord's character count. The message has been truncated and **verbal is unavailable**.")
                        is_voice = False
                    else:
                        await interaction.followup.send("WarpBot's Response is too large for Discord's character count. The message has been truncated.")
                    await sent_message.edit(content=current_response[:2000])
                    break
                
                await sent_message.edit(content=current_response)
            
            ########## VOICE GENERATION ##########

            if is_voice:
                speech = gTTS(text=current_response, lang="en", slow=False)
                speech.save("ask_voice_temp.mp3")
                
                if interaction.guild.voice_client:
                    await interaction.guild.voice_client.disconnect(force=True)
                
                voice_channel = interaction.user.voice.channel
                connected_voice_channel = await voice_channel.connect()
                
                audio_source = discord.FFmpegPCMAudio("ask_voice_temp.mp3")
                
                def after_playback(error):
                    coro = connected_voice_channel.disconnect()
                    asyncio.run_coroutine_threadsafe(coro, bot.loop)
                
                connected_voice_channel.play(audio_source, after=after_playback)

        ########## UI LOGIC ##########

        await interaction.response.defer(thinking=True)

        is_voice = False

        if interaction.user.voice:
            button_message = None

            view = View(timeout=None)

            button_verbal = Button(label="Verbal + Text", style=discord.ButtonStyle.primary)
            async def button_verbal_callback(button_interaction: discord.Interaction):
                if button_interaction.user.id != interaction.user.id:
                    await button_interaction.response.send_message("You cannot interact with this button.", ephemeral=True)
                    return

                for item in view.children:
                    item.disabled = True
                await button_message.edit(content="I noticed you are in a voice channel. Decision recieved.", view=view)

                await button_interaction.response.defer()
                await respond(True)
            button_verbal.callback = button_verbal_callback
            view.add_item(button_verbal)

            button_text = Button(label="Text Only", style=discord.ButtonStyle.secondary)
            async def button_text_callback(button_interaction: discord.Interaction):
                if button_interaction.user.id != interaction.user.id:
                    await button_interaction.response.send_message("You cannot interact with this button.", ephemeral=True)
                    return

                for item in view.children:
                    item.disabled = True
                await button_message.edit(content="I noticed you are in a voice channel. Decision recieved.", view=view)

                await button_interaction.response.defer()
                await respond(False)
            button_text.callback = button_text_callback
            view.add_item(button_text)

            button_message = await interaction.followup.send(
                content="I noticed you are in a voice channel. How do I respond?",
                view=view,
                ephemeral=True
            )
        else:
            await respond(False)

    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}")

bot.run(TOKEN)
