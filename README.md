# WarpBot
A repository used for development of the experimental WarpBot AI-powered Discord Bot.

## Dependencies / Install
This is designed ONLY for use on a Raspberry Pi 5 - it may work elsewhere - provided you remove or change the `/hardware` command since it makes use of `vcgencmd`, which seems very specicfic on what hardware it runs on. The use of a python virtual environment is highly recommended. I made a shell script (named `start_warpbot.sh`) that I use to quickly startup the bot, which involves moving to the correct directiory, activating the virtual environment and starting `bot.py`.

There are a few dependencies for `bot.py`, mainly `gTTS`, `google-genai`, `discord.py[voice]`, `asyncio`, `vcgencmd`, `PyNaCl` and `dotenv`. Just `pip install` those listed and you *should* be fine.

`safeguard.py` however, uses `detoxify`. This is again installed in the same way as above - `pip install [module name here]`.

Similarly, `ffmpeg` is a requirement for the `Voice + Text` feature. I installed `ffmpeg` (Raspberry Pi OS) using `sudo apt install -y ffmpeg`.

Run as a python file, and dont forget to fill out your `.env` (a template is provided) with the `DISCORD_BOT_TOKEN` and `GEMINI_API_KEY`!. A python virtual environment for installation and execution is recommended. 😄

You will need to make context files (in a `context_files` directory) and swap them out in the code! (and possibly make the directory for temp audio files, `/temp_audio`). In the code, near the top just swap out the variables for the file location (which you should fill in the `.env` and import from) and their mime-types (check they work with Gemini too!). If you decide to change the object's name too, be sure to change them in the response function in the ask command.

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
- [x] Use Gemini Voice Generation for TTS instead of regular Google TTS.
- [x] Add "Pro" users that are allowed to pick which Gemini™ model they want to use, and have access to Gemini Voice Generation.
- [ ] (Needs more thought before implementation) Tell the bot to give more concise answers, more like a chatbot. When extended answers are given, try to make it split between multiple messages instead of truncating.
- [ ] (Needs research to see if it is possible to do simply and securely) Allow for uploading of 1 extra file for analysis from the AI.
- [ ] Hide portfolio context behind "Pro".

Gemini™ is a trademark of Google LLC.
