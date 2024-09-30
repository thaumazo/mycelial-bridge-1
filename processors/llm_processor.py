from utils.llm_config import get_llm_config

# Load the LLM configuration from .env
llm_config = get_llm_config()

def process_article_with_llm(article_text):
    prompt = load_prompt("process_article_with_llm.txt")

    # Replace placeholder with actual article text
    prompt_with_article = prompt.replace("{{article_text}}", article_text)

    # Call the appropriate LLM based on the configuration
    if llm_config["provider"] == "openai":
        return process_with_openai(prompt_with_article)
    elif llm_config["provider"] == "gpt4all":
        return process_with_gpt4all(prompt_with_article)
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_config['provider']}")

def load_prompt(prompt_file):
    # Load the prompt from the file in the prompts directory
    with open(f"prompts/{prompt_file}", "r") as file:
        return file.read()

import openai

def process_with_openai(prompt):
    # If using a GPT-3.5-turbo or GPT-4 model (chat-based models)
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # You can switch this to "gpt-4" if needed
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )

    # Extract the generated response
    return response['choices'][0]['message']['content']

def process_with_gpt4all(prompt):
    # Implement processing using GPT4All or another local model
    from gpt4all import GPT4All
    model = GPT4All(llm_config["model_path"])
    response = model.generate(prompt)
    return response.strip()
