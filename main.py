import re
from pathlib import Path
import pytesseract
from PIL import Image, ImageFilter, ImageOps
import requests
import json
import os
from openai import OpenAI

OLLAMA_URL = "http://localhost:11434/api/generate"
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
IMAGES_FOLDER = "samples"
MODEL_NAME = "deepseek-r1:7b"
# MODEL_NAME = "qwen3:8b"
IS_OPENAI = False

if IS_OPENAI:
    client = OpenAI(api_key=OPENAI_API_KEY)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image_path: str) -> str:
    image = Image.open(image_path)
    image = image.convert("L")
    image = ImageOps.autocontrast(image)
    image = image.resize((image.width * 2, image.height * 2))
    image = image.filter(ImageFilter.SHARPEN)
    text = pytesseract.image_to_string(
        image,
        lang="kor+eng",
        config="--psm 6"
    )
    return text

def extract_name(text: str):
    if text[0] == '<': # instagram
        return text.splitlines()[0].replace("<", "").strip().split()[0]
    else: # tiktok
        return text.splitlines()[0].strip()

def extract_emails(text: str) -> list[str]:
    emails = re.findall(EMAIL_REGEX, text)
    return sorted(set(emails))


def save_emails(emails: list[str], output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("[Emails]\n")
        for email in emails:
            f.write(email + "\n")

def build_prompt(system_prompt, prompt) -> str:
    full_prompt = f"""
{system_prompt}

User request:
{prompt}
"""
    return full_prompt

def generate_article(full_prompt:str, model_name) -> str:
    
    if IS_OPENAI:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=full_prompt,
        )
        return response.output_text
    
    payload = {
        "model": model_name,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            # "num_predict": 800,
        },
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=300)
    response.raise_for_status()

    data = response.json()
    return data.get("response", "")


def main():
    for idx, filename in enumerate(os.listdir(IMAGES_FOLDER)):
        gen_text_name = filename + "_generated_article.txt"
        image_path = os.path.join(IMAGES_FOLDER, filename)
        text = extract_text_from_image(image_path)

        emails = extract_emails(text)
        name = extract_name(text)
        if not emails:
            print("이메일 주소를 찾지 못했습니다.")
            return
        save_emails(emails, gen_text_name)

        with open("prompt/prompts.json", "r", encoding="utf-8") as f:
            p_data =json.load(f)
        system_prompt = p_data["system_prompt"]
        user_prompt = p_data["user_prompt"].replace("influencer", name)
        prompt = build_prompt(system_prompt=system_prompt, prompt=user_prompt)
        article = generate_article(prompt, model_name=MODEL_NAME)
        with open(gen_text_name, "a", encoding="utf-8") as f:
            f.write('\n[Context]\n' + article)

        print(f"<{idx} case>\n")
        print("추출된 이메일:")
        print(emails)
        print("\n생성된 글:")
        print(article + "\n\n\n")


if __name__ == "__main__":
    main()