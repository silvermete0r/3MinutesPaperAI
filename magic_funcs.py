import google.generativeai as genai
from google.api_core import retry
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from gtts import gTTS
import requests
import os

load_dotenv()

client = OpenAI()
language = 'en'

def initialize_genai(model_name = 'gemini-pro'):
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    return genai.GenerativeModel(model_name)

prompt_template = 'System Prompt:\n {}\n\nUser Prompt:\n {}'

def generate_response_from_text(user_prompt, system_prompt, creativity_level = 0.5, model = 'gemini-pro', max_output_tokens=16000, top_p=0.8, top_k=30):
    gemini_model = initialize_genai(model)
    
    response = gemini_model.generate_content(
        contents = prompt_template.format(system_prompt, user_prompt),
        generation_config = genai.types.GenerationConfig(
            max_output_tokens = max_output_tokens, # limit on the total number of words generated
            temperature = creativity_level, # creativity level of the model ~ controls the randomness of the generated text
            top_p = top_p, # influences the model to choose the next word based on its probability
            top_k = top_k, # considers only the top K most probable words at each step    
        )
    )
    return response.text

def generate_image_from_text(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1792x1024",
        quality="standard",
        n=1
    )
    return response.data[0].url

def generate_response_from_image(prompt, image_blob):
    model = initialize_genai('gemini-pro-vision')
    response = model.generate_content(
        prompt,
        {'inline_data': image_blob}
    )
    output = ""
    for chunk in response:
        output += (chunk.text + '\n')
    return output

def read_scenario_by_voice(scenario, path='media/audio.wav'):
    tts = gTTS(scenario, lang=language, slow=False)
    tts.save(path)
    # os.system('start media/audio.wav')

def send_simple_message(email):
	return requests.post(
		"https://api.mailgun.net/v3/sandboxebd1ff2187ca4bf6a7610daf43c30c0a.mailgun.org/messages",
		auth=("api", os.getenv('MAILGUN_API_KEY')),
        files=[("attachment", open("media/video.mp4", "rb"))],
		data={"from": "Excited User <mailgun@sandboxebd1ff2187ca4bf6a7610daf43c30c0a.mailgun.org>",
			"to": [email, "supwithproject@sandboxebd1ff2187ca4bf6a7610daf43c30c0a.mailgun.org"],
			"subject": f"Research Summary 🚀",
			"text": "Here is the research summary you requested. Enjoy! 🎉"})

def main():
    pass
    # url = generate_image_from_text('Generate an image of a cat.', 'A cat sitting on a chair.')
    # print(generate_response_from_text('What means `batyr` in Kazakh?'))

if __name__ == '__main__':
    main()