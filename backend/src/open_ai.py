from openai import OpenAI
import logging

from config import OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def summarize_comments(comments, prompt):
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    comments_text = "\n".join(comments)
    new_prompt = f"{prompt}\n\nComments:\n{comments_text}"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Changed from "gpt-4o-mini" to "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": new_prompt},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        
        summary = response.choices[0].message.content
        return summary
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in summarize_comments: {str(e)}")
        raise