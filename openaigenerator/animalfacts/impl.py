import os
import random
import logging
import re
from openai import OpenAI
from dotenv import load_dotenv
from openaigenerator.animalfacts.const import CuteAnimal
from openaigenerator.animalfacts.imagegen import generate_animal_image


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
)


def _normalize_animal(text: str) -> str | None:
    if not text:
        return None

    stripped = text.strip()
    if not stripped:
        return None

    line = stripped.splitlines()[0].strip()
    line = line.strip("\"'`")
    line = re.split(r"[,/;]|\bor\b|\band\b", line, maxsplit=1, flags=re.IGNORECASE)[0]
    line = re.sub(r"[^a-zA-Z \-]", "", line)
    line = re.sub(r"\s+", " ", line).strip()
    line = re.sub(r"^(a|an|the) ", "", line, flags=re.IGNORECASE).strip()

    return line.lower() or None


def generate_random_animal(client: OpenAI) -> str | None:
    messages = [
        {
            "role": "system",
            "content": (
                "You return a single random real animal name. "
                "Return only the animal name, no punctuation, no quotes."
            ),
        },
        {
            "role": "user",
            "content": (
                "Pick one random real animal (cute or friendly). "
                "Return only the animal name."
            ),
        },
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=1.2,
            max_tokens=20,
        )
        raw = response.choices[0].message.content or ""
    except Exception as e:
        logging.error(f"Failed to generate random animal: {e}")
        return None

    animal = _normalize_animal(raw)
    if not animal:
        logging.warning("Random animal response was empty after normalization.")
        return None

    if len(animal) > 40:
        logging.warning("Random animal response too long: %s", animal)
        return None

    return animal


def generate_cute_post():
    # Load environment variables
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Pick a random animal via OpenAI, with a local fallback for safety
    chosen_animal = generate_random_animal(client)
    if not chosen_animal:
        chosen_animal = random.choice(CuteAnimal.list())
        logging.warning("Falling back to local animal list.")

    # Prompt for social-media-friendly text
    prompt = (
        f"Write a heartwarming, adorable fact or mini-story about a {chosen_animal}. "
        "Keep it under 100 characters. It should be short enough for an Instagram or Telegram post."
    )

    # Compose messages
    messages = [
        {"role": "system", "content": "You write extremely short and cute animal facts or stories for social media."},
        {"role": "user", "content": prompt}
    ]

    try:
        image_path = generate_animal_image(
            client=client,
            animal_name=str(chosen_animal),
            size="1024x1024",
            model="gpt-image-1.5",
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.8,
            max_tokens=200
        )
        output = response.choices[0].message.content.strip()

        logging.info(f"Chosen animal: {chosen_animal}")
        logging.info(f"Generated post: {output}")
        return chosen_animal, output, image_path

    except Exception as e:
        logging.error(f"Failed to generate content: {e}")


if __name__ == "__main__":
    generate_cute_post()
