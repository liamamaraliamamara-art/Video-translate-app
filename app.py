import streamlit as st
import os
import speech_recognition as sr
from moviepy.editor import VideoFileClip
from deep_translator import GoogleTranslator

st.title("🎥 အခမဲ့ ဗီဒီယို ဘာသာပြန်အက်ပ်")
st.write("API Key မလိုဘဲ အခမဲ့ အသုံးပြုနိုင်ပါသည်။")

# မူရင်းဘာသာစကား ရွေးရန်
lang_code = st.selectbox("ဗီဒီယိုဘာသာစကားကို ရွေးပါ", ["zh-CN", "en-US", "ko-KR", "ja-JP", "th-TH"], format_func=lambda x: {"zh-CN": "တရုတ်", "en-US": "အင်္ဂလိပ်", "ko-KR": "ကိုရီးယား", "ja-JP": "ဂျပန်", "th-TH": "ထိုင်း"}[x])

video_file = st.file_uploader("ဗီဒီယိုတင်ရန်", type=["mp4"])

if video_file:
    st.video(video_file)
    if st.button("ဘာသာပြန်မည်"):
        # ဗီဒီယိုသိမ်းရန်
        with open("input.mp4", "wb") as f:
            f.write(video_file.getbuffer())
        
        # အသံထုတ်ရန်
        clip = VideoFileClip("input.mp4")
        clip.audio.write_audiofile("audio.wav", logger=None)
        
        # ဘာသာပြန်ရန်
        r = sr.Recognizer()
        with sr.AudioFile("audio.wav") as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language=lang_code)
            myanmar_text = GoogleTranslator(source='auto', target='my').translate(text)
            
            st.write("မူရင်းစာသား:", text)
            st.write("မြန်မာဘာသာပြန်:", myanmar_text)
