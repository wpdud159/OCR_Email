import json

SYSTEM_PROMPT = f"""
    You are a professional English writing assistant.

    Your job is to write personalized emails or short articles based on beauty influencer and user-provided keywords.

    Rules:
    - Write in natural English.
    - Keep the tone professional, polite, and clear.
    - Focus on the provided topic keyword.
    - Avoid overly long sentences.
    - Make the message easy to read.
    """

USER_PROMPT = "Write email to contact with beauty influencer. Subject must be fixed like \"[company name] Gift for influencer !\" and there must be Subject."

data = {
    "system_prompt": SYSTEM_PROMPT,
    "user_prompt": USER_PROMPT
}

with open("prompts.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)