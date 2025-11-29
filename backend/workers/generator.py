import torch
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

def generate_block():
    base_text = generator(
        "Write a child-friendly story opening: ",
        max_length=60,
        num_return_sequences=1
    )[0]["generated_text"]

    options = {
        "A": "Continue the story",
        "B": "Choose a different path"
    }

    return base_text, options
