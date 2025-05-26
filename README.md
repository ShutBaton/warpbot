# WarpBot
A repository used for development of the experimental WarpBot AI-powered Discord Bot.

## Dependencies / Install
This is designed ONLY for use on a Raspberry Pi 5 - it may work elsewhere - provided you remove or change the `/hardware` command since it makes use of `vcgencmd`, which seems very specicfic on what it runs on. The use of a python virtual environment is highly recommended.

There are a few dependencies, mainly `gTTS`, `google-genai`, `discord`, `asyncio`, `vcgencmd`, `PyNaCl` and `dotenv`. Just `pip install` those listed and you *should* be fine.

Similarly, `ffmpeg` is a requirement for the `Voice + Text` feature. I installed `ffmpeg` (Raspberry Pi OS) using `sudo apt install -y ffmpeg`.

Run as a python file, and dont forget to fill out your `.env` (a template is provided) with the `DISCORD_TOKEN` and `GEMINI_API_KEY`!. A python virtual environment for installation and execution is recommended. 😄

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
- [ ] Add finance tracking.
- [ ] Research how `google-genai` handles API errors and make the bot display them better, instead of discord showing a "application not responding" error.

Gemini™ is a trademark of Google LLC.
