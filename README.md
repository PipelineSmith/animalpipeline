AnimalPipeline

This is a small automation project I built to generate cute animal posts and send them straight to a Telegram group.

It creates:

a short, wholesome animal fact

a matching AI-generated image

and posts both together as a single Telegram message

I mainly use it as a low-effort content bot, but it’s easy to extend for other platforms.

What it does

Picks a random animal 

Generates a short, social-media-friendly fact

Generates a cute image of the same animal

Sends the image + text to a Telegram group

No manual work once it’s set up.

Why I built it

I wanted:

a simple Telegram bot that posts regularly

something cheap to run

a clean example of text + image generation with OpenAI

This ended up being a nice, compact pipeline that’s easy to tweak and reuse.

Tech used

Python

OpenAI API

GPT-4o for text

GPT Image models for images

python-telegram-bot

dotenv

Nothing fancy — just practical stuff.
