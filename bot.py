import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord.ui import View, Button
import google.generativeai as genai #Google Gemini API
from gtts import gTTS #Google Text-To-Speech API

import os
from dotenv import load_dotenv

from vcgencmd import Vcgencmd

########## SETUP ##########

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

system_instruction = "You are an AI Helper discord bot created by the F1 in Schools (now called STEM Racing) competition team Warp Racing. Warp Racing consists of a team of boys from St. Olave's Grammar School in Orpington, Kent, UK. They won the Lenovo F1 in Schools National Finals (Development Class) in March 2024, gaining the awards of \"1st Place (National Dev. Class Champions)\", \"Fastest Car\", \"Best Engineered Car\" and \"Research and Development\". The user querying you is a discord user, and you are to help them with their task or provide information. Your responses may occasionally be used in a voice channel via text-to-speech."
model = genai.GenerativeModel(model_name="gemini-2.0-flash", system_instruction=system_instruction)
intents = discord.Intents().all()

bot = commands.Bot(command_prefix='!', intents=intents, activity=discord.Game(name='WarpGame'))

@bot.event
async def on_ready():
    try:
        print("WarpBot has risen.")
        synced = await bot.tree.sync()
        print(f"All {len(synced)} command(s) have been synced.")
    except Exception as e:
        print(e)

########## GENERAL COMMANDS ##########

# Respond with Pong!
@bot.tree.command(name='ping')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong!", ephemeral=True)

# Respond with Ping!
@bot.tree.command(name='pong')
async def pong(interaction: discord.Interaction):
    await interaction.response.send_message(f"Ping!", ephemeral=True)

# Provide about information regarding bot
@bot.tree.command(name='about')
async def about(interaction: discord.Interaction):
    view = discord.ui.View()
    view.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label="warp-racing.com", url="https://warp-racing.com"))
    await interaction.response.send_message(
        f"Hello {interaction.user.mention}. I am WarpBot, a AI helper created by Warp Racing and powered by the Google Gemini 2.0 Flash Large Language Model. I am multilingual and have knowledge of events up to **August 2024**.\n*Please note that each `/ask` command is individual, and does not include previous context.*",
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
    await interaction.response.send_message(f"This Bot is running on a **Raspberry Pi 5 8GB with 512GB of SSD Storage**.\n\n*Current Hardware Info:*\nTemperature: `{temp}C`\nClock: `{clock}MHz`\nThrottled: `{throttled}`", silent=True)

########## ASK COMMAND ##########

@bot.tree.command(name='ask')
@app_commands.describe(query = "What do you want to know?")
async def ask(interaction: discord.Interaction, query: str):
    try:

        ########## RESPONSE LOGIC ##########

        async def respond(is_voice):

            ########## TEXT GENERATION ##########

            response = model.generate_content(
                f"{interaction.user.mention}'s query: {query}",
                generation_config=genai.types.GenerationConfig(max_output_tokens=600, temperature=1, response_mime_type="text/plain"),
                stream=True,
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
                
                audio_source = discord.FFmpegPCMAudio("ask_voice_temp.mp3", executable=ffmpeg_path)
                
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
