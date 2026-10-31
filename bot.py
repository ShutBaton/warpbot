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
import sqlite3
from datetime import datetime
print("Done")

########## SETUP ##########

startup_time = time.time()

print("Loading SQL Database... ", end="")
def setup_database():
    with sqlite3.connect("warpbot_logs.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ask_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_id INTEGER,
                username TEXT,
                query TEXT
            )
        """)

setup_database()
print("Done")

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
warp_system_instruction = "You are an AI Helper discord bot created by the F1 in Schools (now called STEM Racing) competition team Warp Racing. The user querying you is a discord user interested in the team not necessarily affiliated with Warp Racing, and you are to help them with their task or provide information about Warp. Your responses may occasionally be used in a voice channel via text-to-speech. Any files attached are not from the user (they are not aware of their existence), but instead contain information so you can give an informed answer to them."
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
        f"Hello {interaction.user.mention}. I am WarpBot, a AI helper created by Warp Racing using the Google Gemini™ 2.5 Flash Large Language Model (by default). I have knowledge of events up to **January 2025**, and scan all inputted queries and generated results for toxicity using Warp's Safeguard system.\n*Please note that each `/ask` command is individual, and does not include previous context.*\n\nConcerned about a word in a reponse? Let us know so we can add it to our filters using [this email](mailto:ai@warp-racing.com?subject=WarpBot%20Message%20Report).\n\nGemini™ is a trademark of Google LLC.",
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

    embed = discord.Embed(description=f"Hardware information from <t:{int(time.time())}:R>. WarpBot is hosted on a Raspberry Pi 5 8GB with 512GB of NVMe SSD Storage running Pi OS.", color=discord.Color(0x4245A0))
    embed.set_author(name="System Status", icon_url="https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/raspberry-pi-icon.png")

    embed.add_field(name="Temperature", value=f"`{temp}°C`", inline=True)
    embed.add_field(name="Throttled", value=f"`{throttled}`", inline=True)
    embed.add_field(name="Clock Speeds (CPU / System / GPU-3D)", value=f"`{clock_arm}MHz` / `{clock_core}MHz` / `{clock_v3d}MHz`", inline=False)

    await interaction.response.send_message(embed=embed)

# Uptime Information
@bot.tree.command(name="uptime", description="Provides basic uptime information.")
@app_commands.guild_only()
async def uptime(interaction: discord.Interaction):
    if reconnection_time:
        await interaction.response.send_message(f"Bot startup was <t:{int(startup_time)}:R>.\nLast API reconnection was <t:{int(reconnection_time)}:R>.")
    else:
        await interaction.response.send_message("Uptime could not be determined.")

# Get the avatar of a user
@bot.tree.command(name="avatar", description="Returns a URL to a user's avatar image.")
@app_commands.guild_only()
async def avatar(interaction: discord.Interaction, user: discord.User = None):
    if user is None:
        user = interaction.user

    avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
    await interaction.response.send_message(f"{user.mention}'s avatar: {avatar_url}")

########## ASK MODAL ##########

class AskModal(discord.ui.Modal, title="Ask WarpBot"):
    # Input field for the query
    query_input = discord.ui.TextInput(
        label="What do you want to know?",
        style=discord.TextStyle.paragraph,
        placeholder="Type your question here...",
        required=True,
        max_length=256
    )

    async def on_submit(self, interaction: discord.Interaction):
        query = self.query_input.value

        try:
            with sqlite3.connect("warpbot_logs.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO ask_logs (timestamp, user_id, username, query) VALUES (?, ?, ?, ?)",
                    (
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Timestamp
                        interaction.user.id,                          # User ID
                        interaction.user.name,                        # Username
                        query                                         # The Question
                    )
                )
                conn.commit()
        except Exception as e:
            print(f"Failed to log query to database: {e}")
        
        try:

        ########## RESPONSE LOGIC ##########

            # Updated signature to accept a message object to overwrite
            async def respond(is_voice, advanced_voice, message_to_overwrite=None):
                try:

                    ########## TEXT GENERATION ##########
                    
                    # Default settings
                    context_value = "standard"
                    model_to_use = "gemini-2.5-flash"
                    model_to_use_label = "Gemini™ 2.5 Flash"
                    
                    # Placeholder for the message currently being displayed (Voice Menu or Pro Menu)
                    current_ui_message = message_to_overwrite

                    if str(interaction.user.id) in pro_user_ids:
                        
                        class ConfigurationView(discord.ui.View):
                            def __init__(self):
                                super().__init__(timeout=60)
                                self.model_choice = "gemini-2.5-flash"
                                self.model_label = "Gemini™ 2.5 Flash"
                                self.context_choice = "standard"
                                self.confirmed = False

                            @discord.ui.select(
                                placeholder="Choose a Gemini model...",
                                row=0,
                                options=[
                                    discord.SelectOption(
                                        label="Gemini™ 3 Flash Preview",
                                        value="gemini-3-flash-preview",
                                        description="Frontier intelligence. No Search/Maps."
                                    ),
                                    discord.SelectOption(
                                        label="Gemini™ 2.5 Flash",
                                        value="gemini-2.5-flash",
                                        description="Hybrid reasoning, 1M context. Supports Search/Maps.",
                                        default=True
                                    ),
                                    discord.SelectOption(
                                        label="Gemini™ 2.5 Flash-Lite",
                                        value="gemini-2.5-flash-lite",
                                        description="Cost effective, built for scale. Supports Search/Maps."
                                    )
                                ]
                            )
                            async def model_callback(self, select_interaction: discord.Interaction, select: discord.ui.Select):
                                if select_interaction.user.id != interaction.user.id:
                                    await select_interaction.response.send_message("You are not authorized to use this menu.", ephemeral=True)
                                    return
                                
                                self.model_choice = select.values[0]
                                self.model_label = next(opt.label for opt in select.options if opt.value == self.model_choice)
                                await select_interaction.response.defer()

                            @discord.ui.select(
                                placeholder="Choose Warp Context...",
                                row=1,
                                options=[
                                    discord.SelectOption(
                                        label="None", 
                                        value="none",
                                        description="Standard AI response without WarpBot specific knowledge."
                                    ),
                                    discord.SelectOption(
                                        label="Standard Context (recommended)", 
                                        value="standard",
                                        description="Includes general team information.",
                                        default=True
                                    ),
                                    discord.SelectOption(
                                        label="Full Context", 
                                        value="full", 
                                        description="Includes team, design/engineering, and enterprise data."
                                    )
                                ]
                            )
                            async def context_callback(self, select_interaction: discord.Interaction, select: discord.ui.Select):
                                if select_interaction.user.id != interaction.user.id:
                                    await select_interaction.response.send_message("You are not authorized to use this menu.", ephemeral=True)
                                    return
                                
                                self.context_choice = select.values[0]
                                await select_interaction.response.defer()

                            @discord.ui.button(label="Generate", style=discord.ButtonStyle.primary, row=2)
                            async def confirm_callback(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                                if button_interaction.user.id != interaction.user.id:
                                    await button_interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)
                                    return
                                
                                self.confirmed = True
                                await button_interaction.response.edit_message(content="Configuration confirmed.", view=None)
                                self.stop()

                        view = ConfigurationView()
                        
                        if current_ui_message:
                            selection_message = await current_ui_message.edit(content="As a Pro user, please configure your generation settings:", view=view)
                        else:
                            selection_message = await interaction.followup.send("As a Pro user, please configure your generation settings:", view=view)
                        
                        # Update current_ui_message to point to this new state so subsequent logic edits the right thing
                        current_ui_message = selection_message

                        timed_out = await view.wait()

                        if timed_out or not view.confirmed:
                            await selection_message.edit(content="Selection timed out or cancelled. Proceeding with defaults.", view=None)
                        else:
                            model_to_use = view.model_choice
                            model_to_use_label = view.model_label
                            context_value = view.context_choice

                    text_prompt = f"{interaction.user.mention}'s query: {query}"
                    API_prompt = [text_prompt]

                    if context_value == "standard":
                        API_prompt.append(team_ctx)
                    
                    elif context_value == "full":
                        API_prompt.append(team_ctx)
                        API_prompt.append(deseng_ctx)
                        API_prompt.append(enterprise_ctx)

                    embed = discord.Embed(title=query, description="Thinking...", color=discord.Color(0x4245A0))
                    embed.set_author(name=model_to_use_label, icon_url="https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/google-gemini-icon.png")
                    
                    if current_ui_message:
                        sent_message = await current_ui_message.edit(content=None, embed=embed, view=None)
                    else:
                        sent_message = await interaction.followup.send(embed=embed)

                    google_search_tool=types.Tool(googleSearch=types.GoogleSearch())
                    google_maps_tool=types.Tool(google_maps=types.GoogleMaps())

                    model_tools_config = {
                        "gemini-2.5-flash": [google_search_tool, google_maps_tool],
                        "gemini-2.5-flash-lite": [google_search_tool, google_maps_tool],
                        "gemini-3-flash-preview": None
                    }

                    tools_to_use = model_tools_config.get(model_to_use, None)

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
                            tools=tools_to_use
                        )
                    )

                    current_response = ""

                    for chunk in response:
                        if not chunk.text:
                            thoughts = ""
                            for part in chunk.candidates[0].content.parts:
                                if part.thought:
                                    thoughts += part.text
                                    embed.description = f"Thinking... `{thoughts.strip()[-50:]}`"
                                    await sent_message.edit(embed=embed)
                            continue

                        current_response += chunk.text
                        
                        if not current_response.strip():
                            continue

                        if len(current_response) >= 4000:
                            view = discord.ui.View()
                            view.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label="Donate to Warp!", url="https://www.gofundme.com/f/help-warp-get-to-the-uk-national-finals"))

                            warning_text = "WarpBot's response is too large for Discord's character count. The message has been truncated."

                            if is_voice:
                                warning_text = "WarpBot's response is too large for Discord's character count. The message has been truncated and **verbal is unavailable**."
                                is_voice = False
                        
                            warning_text += " Consider donating to support Warp's jouney and fund WarpBot."

                            embed.description = current_response[:4000]+"... (too long)"
                            embed.add_field(name="⚠️ Response Truncated", value=warning_text, inline=False)

                            await sent_message.edit(embed=embed, view=view)
                            break

                        embed.description = current_response
                        await sent_message.edit(embed=embed)
                    
                    if not current_response.strip():
                        await sent_message.edit(content="The model returned an empty response!")
                        is_voice = False

                except errors.APIError as e:
                    print(f"API Error: {str(e)}")
                    
                    status_names = {
                        400: "Bad Request (Invalid Argument)",
                        401: "Unauthorized (Check API Key)",
                        402: "Payment Required",
                        403: "Forbidden (Permission Denied)",
                        404: "Model Not Found",
                        405: "Method Not Allowed",
                        406: "Not Acceptable",
                        408: "Request Timeout",
                        409: "Conflict (Aborted/Already Exists)",
                        410: "Gone",
                        411: "Length Required",
                        412: "Precondition Failed",
                        413: "Payload Too Large",
                        414: "URI Too Long",
                        415: "Unsupported Media Type",
                        429: "Resource Exhausted (Rate Limit for Environmental Reasons)",
                        499: "Client Closed Request",
                        500: "Internal Server Error",
                        501: "Not Implemented",
                        502: "Bad Gateway",
                        503: "Service Unavailable",
                        504: "Gateway Timeout (Deadline Exceeded)"
                    }

                    try:
                        code_key = int(e.code)
                    except (ValueError, TypeError):
                        code_key = e.code

                    status_text = status_names.get(code_key, None)

                    error_title = f"{e.code} - {status_text}" if status_text else str(e.code)

                    embed = discord.Embed(title=error_title, description=e.message, color=discord.Color(0xFF0000))
                    embed.set_author(name="Gemini™ API Error", icon_url="https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/google-gemini-icon.png")

                    await sent_message.edit(embed=embed)

                try:

                    ########## CONTENT SCAN ##########

                    if safeguard.scan_content(current_response):
                        embed.description = "Unsafe content was generated. Safeguard has **blocked** this content."
                        await sent_message.edit(embed=embed)
                        is_voice = False

                    ########## VOICE GENERATION ##########

                    if is_voice:
                        embed.add_field(name="🔊 Voice Generation Status", value="Generating Voice Files (this can take up to 20s)...", inline=False)
                        await sent_message.edit(embed=embed)

                        if advanced_voice:
                            response = client.models.generate_content(
                            model="gemini-2.5-flash-preview-tts",
                            contents=f"Say helpfully: {current_response}",
                            config=types.GenerateContentConfig(
                                response_modalities=["AUDIO"],
                                speech_config=types.SpeechConfig(
                                    voice_config=types.VoiceConfig(
                                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name='Zephyr',
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
                        
                        embed.set_field_at(index=-1, name="🔊 Voice Generation Status", value="Speaking...", inline=False)
                        await sent_message.edit(embed=embed)

                        if interaction.guild.voice_client:
                            await interaction.guild.voice_client.disconnect(force=True)
                            await asyncio.sleep(2)
                        
                        voice_channel = interaction.user.voice.channel
                        
                        if not voice_channel:
                            embed.set_field_at(index=-1, name="🔊 Voice Generation Status", value="Error: You need to be in a voice channel.", inline=False)
                            await sent_message.edit(embed=embed)
                            return
                        
                        permissions = voice_channel.permissions_for(interaction.guild.me)
                        if not permissions.connect or not permissions.speak:
                            embed.set_field_at(index=-1, name="🔊 Voice Generation Status", value="Error: I cannot join that channel!", inline=False)
                            await sent_message.edit(embed=embed)
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
                        
                        embed.set_field_at(index=-1, name="🔊 Voice Generation Status", value="Speech Complete.", inline=False)
                        await sent_message.edit(embed=embed)
                        
                        await connected_voice_channel.disconnect(force=True)

                except Exception as e:
                    await interaction.followup.send("An error occurred while handling the response. Please try again later.")

            ########## UI LOGIC ##########

            await interaction.response.defer(thinking=True)
            
            if len(query) > 256:
                await interaction.followup.send(content="This query is too long (max. 256 characters). Safeguard has **blocked** this query from being generated.")
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
                        if button_interaction.user.id != interaction.user.id:
                            await button_interaction.response.send_message("You cannot interact with this button.", ephemeral=True)
                            return
                        
                        # Just defer, the editing happens in respond()
                        await button_interaction.response.defer()
                        
                        # Pass button_message to be overwritten
                        await respond(True, True, button_message)
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
                        
                        await button_interaction.response.defer()
                        
                        # Pass button_message to be overwritten
                        await respond(True, False, button_message)
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

                        await button_interaction.response.defer()
                        
                        # Pass button_message to be overwritten
                        await respond(False, False, button_message)
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

########## ASK COMMAND ##########

def ask_limit_check(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
    
    if str(interaction.user.id) in pro_user_ids:
        return None
    
    return app_commands.Cooldown(rate=3, per=86400)

@bot.tree.command(name="ask", description="Ask WarpBot anything! Join a Voice Channel to hear it speak.")
@app_commands.guild_only()
@app_commands.checks.dynamic_cooldown(ask_limit_check)
async def ask(interaction: discord.Interaction):
    await interaction.response.send_modal(AskModal())

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        hours, remainder = divmod(int(error.retry_after), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        await interaction.response.send_message(
            f"⚠️ You have reached your daily limit (3). You can ask again in {hours}h {minutes}m. Please note WarpBot has set limits for maximum API calls a day for environmental reasons.", 
            ephemeral=True
        )
    else:
        print(f"Command Error: {error}")

print("Done")
bot.run(TOKEN)
