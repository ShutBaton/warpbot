# WarpBot
A repository used for development of the experimental WarpBot AI-powered Discord Bot using [Google Gemini™](https://gemini.google.com/) LLMs & LRMs.

WarpBot has now been succeeded by my new agent harness for discord, EncoreBot, allowing a GPT-6 Luna instance to act ambiently and agentically across channels, creating memories, starting conversations, and helping with existing ones. It is based on the OpenAI library, and uses Exa for search (so much more modern).

> [!CAUTION]
> I have not been maintaining this repo in several months to a year - there are some known changes that must be made for this Bot to function correctly - this includes updating voice to the new voice protocols required by Discord.py and the Discord API, and updating to work with the ever-evolving Gemini™ API. It might be worth getting this moved to the OpenAI library, as Gemini™ supports this (afaik).

## Dependencies / Install
> [!IMPORTANT]  
> This is designed ONLY for use on a Raspberry Pi 5 - it may work elsewhere - provided you remove or change the `/hardware` command since it makes use of `vcgencmd`, which seems very specicfic on what hardware it runs on.

There are a few dependencies for `bot.py`, mainly `gTTS`, `google-genai`, `discord.py[voice]`, `asyncio`, `vcgencmd`, `PyNaCl` and `dotenv`. Just `pip install` those listed and you *should* be fine. I couldn't be bothered to make a requirements.txt. My bad.

`safeguard.py` however, uses `detoxify`. This is again installed in the same way as above - `pip install [module name here]`.

Similarly, `ffmpeg` is a requirement for the `Voice + Text` feature. I installed `ffmpeg` (Raspberry Pi OS) using `sudo apt install -y ffmpeg`.

Run as a python file, and dont forget to fill out your `.env` (a template is provided) with the `DISCORD_BOT_TOKEN` and `GEMINI_API_KEY`!. A python virtual environment for installation and execution is recommended. 😄

> [!TIP]
> The use of a python virtual environment is highly recommended. I made a shell script (named `start_warpbot.sh`) that I use to quickly startup the bot, which involves moving to the correct directiory, activating the virtual environment and starting `bot.py`.

> [!WARNING]
> You will need to make context files (in a `context_files` directory) and swap them out in the code! (and possibly make the directory for temp audio files, `/temp_audio`). In the code, near the top just swap out the variables for the file location (which you should fill in the `.env` and import from) and their mime-types (check they work with Gemini too!).

If you decide to change the object's name too, be sure to change them in the response function in the ask command.

## Hardware
Hardware being used to run the bot:
- Raspberry Pi 5 8GB
- Raspberry Pi Active Cooler
- Raspberry Pi M.2 HAT+, Official 512GB SSD
- [3D Printed Case by pixel_design on Makerworld](https://makerworld.com/en/models/1063966-raspberry-pi-5-ai-m-2-hat-snap-case), printed in Bambu PLA Basic Black, 100% Infill, Arachne, 0.12mm Layer Height, on a Bambu Lab P1S with a Hardened Steel 0.4mm Nozzle.

## Commands
`/help`
- Provides some help (a command list for this bot).

`/about`
- Provides some information about the Bot and its origins/capabilities.

`/ask`
- Ask WarpBot anything (sensible)! If in a voice channel, a UI will be shown where you can opt to have it read it aloud to you.

`/avatar`
- Returns URL to a selected user's discord avatar.

`/hardware`
- Supplies current CPU temperature, CPU-arm clock, GPU-core (2D) clock, GPU-v3d (3D) clock speed and if the Pi is throttling.

`/ping` & `/pong`
- Ping or Pongs!

`/uptime`
- Tells you how long the bot has had a continous uptime! The Pi however, never turns off...

## Todo
- [x] Add `/hardware` for hardware monitoring, `/uptime`, and latency to `/ping` & `/pong`
- [x] Add `/avatar` as a meme function, also allows for quick access to Warp logo.
- [x] Update all references to Gemini™ to mention trademark!
- [x] Use `google-genai` instead of `google-generativeai`
- [x] Make uptime use discord's support of `<t:[UNIX TIMESTAMP]:R>` to show that something is `[some amount of time] ago` instead of the use of `time` for `/uptime` so far.
- [x] Add GPU clocks to `/hardware`.
- [x] Add high-accuracy harmful content detection and removal.
- [x] Research how `google-genai` handles API errors and make the bot display them better, instead of discord showing an "application not responding" error.
- [x] Make the bot ground to own provided context files as part of an optional argument for levels of knowledge about Warp.
- [x] Use Gemini™ Voice Generation for TTS instead of regular Google TTS.
- [x] Add "Pro" users that are allowed to pick which Gemini™ model they want to use, and have access to Gemini™ Voice Generation.
- [x] The current `startup_time` is actually the time since the bot disconnected and reconnected to discord. Track this AND original program startup seperately. Maybe call the current metric "time since API reconnection"
- [x] You can DM the bot but it isn't built to handle that, discord shows `••• WarpBot is thinking...` and after a long time throws `The application did not respond`! Maybe make it autoreply saying DMs are unsupported (for Gemini™ ToS abiding reasons) or block people from DM-ing it at all? <- actually ended up just removing the ability to use commands in its DMs.
- [x] When using a reasoning model, show the rolling thinking summaries. <- Gemini™ doesn't have a clean way for this to happen, I just show the latest 50 characters of thoughts while it thinks.
- [x] Make use of embeds (looks more polished + 6k max char count instead of 2k with a regular message). ADD GOOGLE SEARCH AND GOOGLE MAPS GROUNDING!
- [x] Hide portfolio context behind "Pro".
- [x] Move entire ask command into a modal?
- [ ] (Needs research to see if it is possible to do simply and securely) Allow for uploading of 1 extra file for analysis from the AI.
- [ ] Add Gemini™ Live support in voice channels through a new `/live` command. Make this "Pro" only due to the cost. [This](https://github.com/2187Nick/discord-voice-to-voice-gemini) repo has an interesting implementation.
- [ ] Add support for Gemini™ API File Search, reduces input token usage for RAG (Retrieval Augmented Generation) AKA grounding to files.

## [Legal Attribution](https://about.google/brand-resource-center/guidance/apis/#legal-attribution)
Gemini™ is a trademark of Google LLC.
