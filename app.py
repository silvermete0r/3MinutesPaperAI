import streamlit as st
from magic_funcs import generate_response_from_text, read_scenario_by_voice, generate_image_from_text, send_simple_message, generate_response_from_image
from converter_funcs import image_from_url
import google.generativeai as genai
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from PIL import Image
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip
import json
import os

def merge_video_with_music(video_path, music_path, output_path):
    video = VideoFileClip(video_path)
    video_without_audio = video.without_audio()
    music = AudioFileClip(music_path)
    video_with_music = video_without_audio.set_audio(music)
    video_with_music.write_videofile(output_path, codec='libx264', audio_codec='aac')
    video.close()
    video_without_audio.close()
    music.close()
    video_with_music.close()

st.set_page_config(
    page_title = '3MinutesPaperAI',
    page_icon = '🧾',
    layout = 'wide',
    initial_sidebar_state = 'auto',
)

@st.cache_data()
def load_prompts_json():
    with open("prompts.json", "r") as f:
        prompts = json.load(f)
    return prompts

prompts = load_prompts_json()

# Extract text from a list of PDF documents.
@st.cache_data
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            add = page.extract_text()
            text += add if add else ""
    return text

if 'isBotDisabled' not in st.session_state:
    st.session_state['isBotDisabled'] = True

def main():
    st.title('📜 3MinutesPaperAI')

    st.markdown('''
        LLM application that generates 3-minute summaries (video, document & audio) of research articles from PDF documents.
    ''')
    st.write('---')

    with st.sidebar:
        st.image('media/logo.png', use_column_width=True)

        st.title("Menu:")
        pdf_file = st.file_uploader('Upload a PDF file', type=['pdf'], accept_multiple_files=True, key='pdf_file')
        if not pdf_file:
            st.info('Please upload a PDF file.')

        additional_data = st.text_area('Additional data:', placeholder='Enter additional data here...', value="")

        st.subheader('Settings:')

        creativity_level = st.slider('Creativity level:', 0.0, 1.0, 0.5, 0.1) 
        
        model = st.selectbox('Model: ', ['gemini-pro', 'gemini-1.5-flash-latest', 'gemini-1.5-pro-latest'], index=0)

    if st.sidebar.button("Generate 🌟"):
        with st.spinner('Processing PDF file(s)...'):
            raw_text = get_pdf_text(pdf_file) + '\n' + additional_data
        
        st.subheader('3-minute Summary:')

        with st.spinner('Generating 3 minute-summary...'):
            scenario = generate_response_from_text(prompts['scenario_generation'], raw_text, creativity_level, model)
            sections = scenario.split('#####')
            topic = sections[0].replace('#', '').replace('Topic', '').strip()
            sections.pop(-1)
            audio_text = "".join(sections)
            img_url = generate_image_from_text('Creative scetch on topic: ' + topic)
            img = image_from_url(img_url)
            st.image(img, width=600, caption='Creative scetch by Dall-E')
            st.markdown(scenario)
     
        with st.spinner('Generating audio summary...'):
            to_say = prompts['welcome_words'] + audio_text.replace('#', '').replace('*', '') + prompts['goodbye_words']
            read_scenario_by_voice(to_say, 'media/audio.wav')
            st.audio('media/audio.wav', format='audio/wav')

        with st.spinner('Generating video summary...'):
            merge_video_with_music('media/videoplayback.mp4', 'media/audio.wav', 'media/video.mp4')
            st.video('media/video.mp4')
        
        st.session_state['isBotDisabled'] = False

        st.success('Done! 🎉')

    if not st.session_state['isBotDisabled']:
        st.subheader('Send me:')
        email = st.text_input('Email:', placeholder='Enter your email address...')
        st.button('Send', key='send')
        if st.session_state['send']:
            send_simple_message(email)
            st.success('Email sent! 🚀')

        st.subheader('Download:')

        aCol, bCol, cCol, _, _ = st.columns(5)
        aCol.download_button(
            label='Download text-summary',
            data=scenario,
            file_name='text-summary.txt',
            mime='text/plain'
        )

        with open('media/audio.wav', 'rb') as audio_file:
            bCol.download_button(
                label='Download audio-summary',
                data=audio_file,
                file_name='audio-summary.wav',
                mime='audio/wav'
            )

        with open('media/video.mp4', 'rb') as video_file:
            cCol.download_button(
                label='Download video-summary',
                data=video_file,
                file_name='video-summary.mp4',
                mime='video/mp4'
            )

    with st.sidebar:
        st.image('media/gemini_logo.png')

        st.info('3MinutesPaperAI app research-to-video-summary (also auido + document support) based on [Streamlit](https://streamlit.io).')
        st.caption('Made with ❤️ by [silvermete0r](https://github.com/silvermete0r)')

if __name__ == '__main__':
    main()
