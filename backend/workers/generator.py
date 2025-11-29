# backend/workers/generator.py

from typing import Optional
from transformers import pipeline

# Hugging Face text-generation pipeline
generator = pipeline("text-generation", model="gpt2")


def generate_block(prompt: Optional[str] = None):
    """
    Generate a story block.

    If `prompt` is None, we use a default kid-friendly instruction.
    If `prompt` is provided, we continue the story from that text.
    Returns:
        text: the generated paragraph (string)
        options: dict with choices for the child, e.g. {"A": "...", "B": "..."}
    """

    if prompt is None:
        prompt_text = (
            "Write a child-friendly story paragraph for kids. "
            "Use simple language and end the paragraph naturally. "
            "Do not include choices; just tell the story.\n\nStory:"
        )
    else:
        # continue from previous block + choice
        prompt_text = prompt

    # Call the HF pipeline
    result = generator(
        prompt_text,
        max_new_tokens=150,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.9,
        pad_token_id=generator.tokenizer.eos_token_id,  # avoid warnings with gpt2
    )[0]["generated_text"]

    # Strip off the prompt from the front so we only keep the new story bit
    generated = result[len(prompt_text):].strip()

    # Story text for this block
    text = generated

    # Simple fixed options for now (you can make these smarter later)
    options = {
        "A": "Continue the story",
        "B": "Choose a different path"
    }

    return text, options
