print("Loading imports... ", end="")
import asyncio
import discord                                  # Discord
from discord import app_commands                # Discord
from discord.ext import commands                # Discord
from discord.voice_client import VoiceClient    # Discord
from discord.ui import View, Button             # Discord
import typing                                   # Type Hints
from google import genai                        # Google Gemini
from google.genai import types, errors          # Google Gemini
import pathlib                                  # Object Oriented Paths
import wave                                     # Saving .wav files
from gtts import gTTS                           # Google Text-To-Speech
import safeguard                                # Harmful content detection
import os
from dotenv import load_dotenv
import time
from vcgencmd import Vcgencmd                   # Hardware Monitoring
print("Done")

########## SETUP ##########

startup_time = time.time()

print("Loading API Keys... ", end="")
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
print("Done")

print("Loading Basic Context... ", end="")
team_ctx_path = pathlib.Path(os.getenv("TEAM_CTX_PATH"))
team_ctx = types.Part.from_bytes(
    data=team_ctx_path.read_bytes(),
    mime_type='text/plain',
)
print("Done")

print("Loading DesEng Context... ", end="")
deseng_ctx_path = pathlib.Path(os.getenv("DESENG_CTX_PATH"))
deseng_ctx = types.Part.from_bytes(
    data=deseng_ctx_path.read_bytes(),
    mime_type='application/pdf',
)
print("Done")

print("Loading Enterprise Context... ", end="")
enterprise_ctx_path = pathlib.Path(os.getenv("ENTERPRISE_CTX_PATH"))
enterprise_ctx = types.Part.from_bytes(
    data=enterprise_ctx_path.read_bytes(),
    mime_type='application/pdf',
)
print("Done")

print("Loading .wav file functions... ", end="")
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)
print("Done")

print("Loading Pro Userlist... ", end="")
with open("pro_userlist.csv", "r") as f:
    pro_user_ids = f.read().strip().split(",")
print("Done")

print("Loading Discord Client... ", end="")
warp_system_instruction = "You are an AI Helper discord bot created by the F1 in Schools (now called STEM Racing) competition team Warp Racing. Warp Racing consists of a team of boys from St. Olave's Grammar School in Orpington, Kent, UK. They won the Lenovo F1 in Schools National Finals (Development Class) in March 2024, gaining the awards of \"1st Place (National Dev. Class Champions)\", \"Fastest Car\", \"Best Engineered Car\" and \"Research and Development\". The user querying you is a discord user interested in the team not necessarily affiliated with Warp Racing, and you are to help them with their task or provide information. Your responses may occasionally be used in a voice channel via text-to-speech. Any files attached are not from the user (they are not aware of their existence), but instead contain information so you can give an informed answer."
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents, activity=discord.Game(name='WarpGame'), help_command=None)

reconnection_time = None

@bot.event
async def on_ready():
    try:
        print("WarpBot is now online.")
        synced = await bot.tree.sync()
        print(f"All {len(synced)} command(s) have been synced.")
        global reconnection_time
        reconnection_time = time.time()
    except Exception as e:
        print(e)

########## GENERAL COMMANDS ##########

# Respond with Command List
@bot.tree.command(name="help", description="Provides a detailed command list.")
@app_commands.guild_only()
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(f"**Commands List**\n\n`/help`\n- Provides some help (a command list for this bot).\n\n`/about`\n- Provides some information about the Bot and its origins/capabilities.\n\n`/ask`\n- Ask WarpBot anything (sensible)! If in a voice channel, a UI will be shown where you can opt to have it read it aloud to you.\n\n`/avatar`\n- Returns URL to a selected user's discord avatar.\n\n`/hardware`\n- Supplies current CPU temperature, CPU-arm clock, GPU-core (2D) clock, GPU-v3d (3D) clock speed and if the Pi is throttling.\n\n`/ping` & `/pong`\n- Ping or Pongs!\n\n`/uptime`\n- Tells you how long the bot has had a continous uptime! The Pi however, never turns off...", ephemeral=True)

# Respond with Pong + Round Trip Latency
@bot.tree.command(name="ping", description="Pong! Provides latency")
@app_commands.guild_only()
async def ping(interaction: discord.Interaction):
    latency = round(interaction.client.latency * 1000)
    await interaction.response.send_message(f"Pong! Latency: {latency}ms", ephemeral=True)

# Respond with Ping + Round Trip Latency
@bot.tree.command(name="pong", description="Ping! Provides latency.")
@app_commands.guild_only()
async def pong(interaction: discord.Interaction):
    latency = round(interaction.client.latency * 1000)
    await interaction.response.send_message(f"Ping! Latency: {latency}ms", ephemeral=True)

# Provide about information regarding Bot
@bot.tree.command(name="about", description="Provides Bot information. Useful to know!")
@app_commands.guild_only()
async def about(interaction: discord.Interaction):
    view = discord.ui.View()
    view.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label="Warp Racing website", url="https://warp-racing.com"))
    view.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label="Donate to Warp!", url="https://www.gofundme.com/f/help-warp-get-to-the-uk-national-finals"))
    await interaction.response.send_message(
        f"Hello {interaction.user.mention}. I am WarpBot, a AI helper created by Warp Racing using the Google Gemini™ 2.5 Flash Large Language Model. I have knowledge of events up to **January 2025**, and scan all inputted queries and generated results for toxicity using Warp's Safeguard system.\n*Please note that each `/ask` command is individual, and does not include previous context.*\n\nGemini™ is a trademark of Google LLC.",
        ephemeral=True,
        view=view
    )

# Raspberry Pi 5 Hardware Information
@bot.tree.command(name="hardware", description="Bot feeling slow? See server clocks and temperatues!")
@app_commands.guild_only()
async def hardware(interaction: discord.Interaction):
    vcgm = Vcgencmd()
    temp = vcgm.measure_temp()
    clock_arm = int(vcgm.measure_clock('arm')/1000000)
    clock_core = int(vcgm.measure_clock('core')/1000000)
    clock_v3d = int(vcgm.measure_clock('v3d')/1000000)
    throttled = vcgm.get_throttled()['breakdown']['2']
    await interaction.response.send_message(f"WarpBot is running on a **Raspberry Pi 5 8GB with 512GB of M.2 NVMe SSD Storage**.\n\n*Current Hardware Info:*\nTemperature: `{temp}C`\nClock (CPU-arm, GPU-core, GPU-v3d): `{clock_arm}Mhz`, `{clock_core}MHz`, `{clock_v3d}MHz`\nThrottled: `{throttled}`", ephemeral=True)

# Uptime Information
@bot.tree.command(name="uptime", description="Provides basic uptime information.")
@app_commands.guild_only()
async def uptime(interaction: discord.Interaction):
    if reconnection_time:
        await interaction.response.send_message(f"Bot startup was <t:{int(startup_time)}:R>.\nLast API reconnection was <t:{int(reconnection_time)}:R>.", ephemeral=True)
    else:
        await interaction.response.send_message("Uptime could not be determined.", ephemeral=True)

# Get the avatar of a user
@bot.tree.command(name="avatar", description="Returns a URL to a user's avatar image.")
@app_commands.guild_only()
async def avatar(interaction: discord.Interaction, user: discord.User = None):
    if user is None:
        user = interaction.user

    avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
    await interaction.response.send_message(f"{user.mention}'s avatar: {avatar_url}", ephemeral=True)

########## ASK COMMAND ##########

@bot.tree.command(name="ask", description="Ask WarpBot anything! Join a Voice Channel to hear it speak.")
@app_commands.guild_only()
@app_commands.describe(context="Decide if WarpBot is to respond using Warp Context material")
@app_commands.choices(context = [
    app_commands.Choice(name="None",value="none"),
    app_commands.Choice(name="Basic Context",value="basic"),
    app_commands.Choice(name="Full (Portfolio) Context",value="full")
])
@app_commands.describe(query = "What do you want to know?")
async def ask(interaction: discord.Interaction, query: str, context: typing.Optional[app_commands.Choice[str]]):
    try:

        ########## RESPONSE LOGIC ##########

        async def respond(is_voice, advanced_voice):
            try:

                ########## TEXT GENERATION ##########
                
                context_value = context.value if context else "full"

                text_prompt = f"{interaction.user.mention}'s query: {query}"
                API_prompt = [text_prompt]

                if context_value == "basic":
                    API_prompt.append(team_ctx)
                
                elif context_value == "full":
                    API_prompt.append(team_ctx)
                    API_prompt.append(deseng_ctx)
                    API_prompt.append(enterprise_ctx)

                model_to_use = "gemini-2.5-flash"

                if str(interaction.user.id) in pro_user_ids:
                    
                    class ModelSelectionView(discord.ui.View):
                        def __init__(self):
                            super().__init__(timeout=60) # 1 minute timeout
                            self.model_choice = None

                        @discord.ui.select(
                            placeholder="Choose a Gemini model to use...",
                            options=[
                                discord.SelectOption(
                                    label="Gemini™ 2.5 Flash",
                                    value="gemini-2.5-flash",
                                    description="Google's hybrid reasoning model, with a 1M token context window.",
                                ),
                                discord.SelectOption(
                                    label="Gemini™ 2.5 Flash-Lite",
                                    value="gemini-2.5-flash-lite",
                                    description="Google's smallest and most cost effective model, built for at scale usage."
                                )
                            ]
                        )
                        async def select_callback(self, select_interaction: discord.Interaction, select: discord.ui.Select):
                            if select_interaction.user.id != interaction.user.id:
                                await select_interaction.response.send_message("You are not authorized to use this menu.", ephemeral=True)
                                return

                            self.model_choice = select.values[0]

                            model_label = next(opt.label for opt in select.options if opt.value == self.model_choice)

                            await select_interaction.response.edit_message(content=f"Model choice (`{model_label}`) confirmed.",  view=None)

                            self.stop()

                    view = ModelSelectionView()
                    selection_message = await interaction.followup.send("As a Pro user, you may select a generation model:", view=view)
                    
                    timed_out = await view.wait()

                    if timed_out:
                        await selection_message.edit(content="Model selection timed out. Proceeding with the default model.", view=None)
                    else:
                        model_to_use = view.model_choice

                sent_message = await interaction.followup.send("Thinking...")

                grounding_tool=types.Tool(googleSearch=types.GoogleSearch())

                response = client.models.generate_content_stream(
                    model=model_to_use,
                    contents=API_prompt,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(
                            thinking_budget=-1,
                            include_thoughts=True
                        ),
                        temperature=0.3,
                        response_mime_type="text/plain",
                        system_instruction=warp_system_instruction,
                        tools=[grounding_tool]
                    )
                )

                current_response = ""

                for chunk in response:
                    if not chunk.text:
                        thoughts = ""
                        for part in chunk.candidates[0].content.parts:
                            if part.thought:
                                thoughts += part.text
                                await sent_message.edit(content=f"Thinking... `{thoughts.strip()[-50:]}`")
                        continue

                    current_response += chunk.text
                    
                    if not current_response.strip():
                        continue

                    if len(current_response) >= 2000:
                        view = discord.ui.View()
                        view.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label="Donate to Warp!", url="https://www.gofundme.com/f/warp-racing"))
                        if is_voice:
                            await interaction.followup.send("WarpBot's response is too large for Discord's character count. The message has been truncated and **verbal is unavailable**.\n\nConsider donating to support Warp's jouney and fund WarpBot:", view=view)
                            is_voice = False
                        else:
                            await interaction.followup.send("WarpBot's response is too large for Discord's character count. The message has been truncated.\n\nConsider donating to support Warp's jouney and fund WarpBot:", view=view)
                        await sent_message.edit(content=current_response[:2000])
                        break
                    
                    await sent_message.edit(content=current_response)
                
                if not current_response.strip():
                    await sent_message.edit(content="The model returned an empty response!")
                    is_voice = False

            except errors.APIError as e:
                print(f"API Error: {str(e)}")
                await sent_message.edit(content=f"An error occurred while generating the response. Please try again later.\n\n{e.code}: {e.message}")

            try:

                ########## CONTENT SCAN ##########

                if safeguard.scan_content(current_response):
                    await sent_message.edit(content="Unsafe content was generated. Safeguard has **blocked** this content.")
                    is_voice = False

                ########## VOICE GENERATION ##########

                if is_voice:
                    voice_status_message = await interaction.followup.send("Generating Voice Files (this can take a up to 20s).")
                    if advanced_voice:
                        response = client.models.generate_content(
                        model="gemini-2.5-flash-preview-tts",
                        contents=f"Say helpfully: {current_response}",
                        config=types.GenerateContentConfig(
                            response_modalities=["AUDIO"],
                            speech_config=types.SpeechConfig(
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name='Puck',
                                    )
                                )
                            ),
                        )
                        )

                        data = response.candidates[0].content.parts[0].inline_data.data

                        wave_file("temp_audio/ask_voice_gemini.wav", data)
                    else:
                        speech = gTTS(text=current_response, slow=False)
                        speech.save("temp_audio/ask_voice_gTTS.mp3")
                    
                    await voice_status_message.edit(content="Speaking.")

                    if interaction.guild.voice_client:
                        await interaction.guild.voice_client.disconnect(force=True)
                        await asyncio.sleep(2)
                    
                    voice_channel = interaction.user.voice.channel
                    
                    if not voice_channel:
                        await voice_status_message.edit(content="You need to be in a voice channel for me to speak!")
                        return

                    connected_voice_channel = await voice_channel.connect()
                    await asyncio.sleep(1)

                    if advanced_voice:
                        audio_source = discord.FFmpegPCMAudio("temp_audio/ask_voice_gemini.wav")
                    else:
                        audio_source = discord.FFmpegPCMAudio("temp_audio/ask_voice_gTTS.mp3")
                    
                    connected_voice_channel.play(audio_source)

                    while connected_voice_channel.is_playing():
                        await asyncio.sleep(0.5)
                    await voice_status_message.edit(content="Speech Complete.")
                    await connected_voice_channel.disconnect(force=True)

            except Exception as e:
                await interaction.followup.send("An error occurred while handling the response. Please try again later.")

        ########## UI LOGIC ##########

        await interaction.response.defer(thinking=True)
        
        if len(query) > 500:
            await interaction.followup.send(content="This query is too long (max. 500 characters). Safeguard has **blocked** this query from being generated.")
            return

        if safeguard.scan_content(query):
            await interaction.followup.send(content="Unsafe content was queried. Safeguard has **blocked** this query from being generated.")
            return

        if interaction.user.voice:
            button_message = None

            view = View(timeout=None)

            button_verbal = Button(label="Adv. Verbal", style=discord.ButtonStyle.primary)
            async def button_verbal_callback(button_interaction: discord.Interaction):
                try:
                    if (button_interaction.user.id != interaction.user.id) or (str(button_interaction.user.id) not in pro_user_ids):
                        await button_interaction.response.send_message("You cannot interact with this button. Only Pro users have access to Adv. Verbal due to the large amount of processing power that is needed.", ephemeral=True)
                        return

                    for item in view.children:
                        item.disabled = True
                    await button_message.edit(content="I noticed you are in a voice channel. Decision recieved (Adv. Voice).", view=view)

                    await button_interaction.response.defer()
                    await respond(True, True)
                except Exception as e:
                    print(f"An error occurred: {str(e)}")
            button_verbal.callback = button_verbal_callback
            view.add_item(button_verbal)

            button_verbal = Button(label="Verbal", style=discord.ButtonStyle.primary)
            async def button_verbal_callback(button_interaction: discord.Interaction):
                try:
                    if button_interaction.user.id != interaction.user.id:
                        await button_interaction.response.send_message("You cannot interact with this button.", ephemeral=True)
                        return

                    for item in view.children:
                        item.disabled = True
                    await button_message.edit(content="I noticed you are in a voice channel. Decision recieved (Voice).", view=view)

                    await button_interaction.response.defer()
                    await respond(True, False)
                except Exception as e:
                    print(f"An error occurred: {str(e)}")
            button_verbal.callback = button_verbal_callback
            view.add_item(button_verbal)

            button_text = Button(label="Text Only", style=discord.ButtonStyle.secondary)
            async def button_text_callback(button_interaction: discord.Interaction):
                try:
                    if button_interaction.user.id != interaction.user.id:
                        await button_interaction.response.send_message("You cannot interact with this button.", ephemeral=True)
                        return

                    for item in view.children:
                        item.disabled = True
                    await button_message.edit(content="I noticed you are in a voice channel. Decision recieved (text).", view=view)

                    await button_interaction.response.defer()
                    await respond(False, False)
                except Exception as e:
                    print(f"An error occurred: {str(e)}")
            button_text.callback = button_text_callback
            view.add_item(button_text)

            button_message = await interaction.followup.send(
                content="I noticed you are in a voice channel. How do I respond?",
                view=view,
                ephemeral=True
            )
        else:
            await respond(False, False)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    print(f"Command Error: {error}")

print("Done")
bot.run(TOKEN)
