# openai.py
from openai import OpenAI

# Environment variable
from config import OPENAI_API_KEY
def summarize_comments(comments, prompt):
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Join the comments into a single string
    comments_text = "\n".join(comments)

    new_prompt = f"{prompt}\n\nComments:\n{comments_text}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": new_prompt},
        ],
        #max_tokens=200,Adjust based on the length of summary you want
        temperature=1.3,  # Adjust for creativity in the response
    )
    
    # Generate the summary
    summary = response.choices[0].message.content
    return summary
