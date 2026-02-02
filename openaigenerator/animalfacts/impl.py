import os
import random
import logging
from openai import OpenAI
from dotenv import load_dotenv
from openaigenerator.animalfacts.const import CuteAnimal
from openaigenerator.animalfacts.imagegen import generate_animal_image


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
)


def generate_cute_post():
    # Load environment variables
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Pick a random cute animal
    chosen_animal = random.choice(CuteAnimal.list())

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
