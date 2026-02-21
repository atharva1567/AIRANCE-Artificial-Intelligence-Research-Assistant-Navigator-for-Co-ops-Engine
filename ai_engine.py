import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_summary(job_text):
    prompt = f"""
    Summarize this internship posting:
    - Key responsibilities
    - Required skills
    - Who it is suited for
    - Technical difficulty level
    - Resume keywords to highlight

    Job:
    {job_text}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )

    return response.choices[0].message.content