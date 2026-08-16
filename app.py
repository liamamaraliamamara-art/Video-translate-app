import streamlit as st
import os
from openai import OpenAI
from moviepy.editor import VideoFileClip
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Universal AI Video Translator", page_icon="🎥", layout="centered")

st.title("🎥 အစုံလိုက် AI ဗီဒီယို ဘာသာပြန်အက်ပ် (Universal Video Translator)")
st.write("မည်သည့် ဘာသာစကားဖြင့် ပြုလုပ်ထားသော ဗီဒီယိုကိုမဆို မြန်မာဘာသာသို့ တိုက်ရိုက် ဘာသာပြန်ဆိုနိုင်ပါပြီ။")

# Sidebar - API Key ထည့်ရန်
st.sidebar.header("⚙️ ဆက်တင်များ (Settings)")
api_key = st.sidebar.text_input("OpenAI API Key ထည့်ပါ", type="password")

if not api_key:
    st.warning("⚠️ ကျေးဇူးပြု၍ ဘယ်ဘက် ဘေးဘောင် (Sidebar) တွင် OpenAI API Key ထည့်သွင်းပေးပါ။")

# ဗီဒီယိုဖိုင် တင်ရန်
video_file = st.file_uploader("ဗီဒီယိုဖိုင်ကို ရွေးချယ်ပါ (MP4, MOV, AVI, MKV)", type=["mp4", "mov", "avi", "mkv"])

if video_file is not None and api_key:
    # ဗီဒီယိုကို ပြသရန်
    st.video(video_file)
    
    # ဗီဒီယိုဖိုင်ကို ယာယီသိမ်းဆည်းခြင်း
    input_video_path = "temp_input_video.mp4"
    with open(input_video_path, "wb") as f:
        f.write(video_file.getbuffer())
        
    if st.button("🚀 ဗီဒီယိုကို မြန်မာလို စတင်ဘာသာပြန်ရန်"):
        client = OpenAI(api_key=api_key)
        
        try:
            with st.spinner("⏳ ဗီဒီယိုမှ အသံဖိုင်ကို ထုတ်ယူနေပါပြီ..."):
                # Moviepy ဖြင့် ဗီဒီယိုမှ အသံ (mp3) ထုတ်ယူခြင်း
                video_clip = VideoFileClip(input_video_path)
                audio_path = "temp_audio.mp3"
                video_clip.audio.write_audiofile(audio_path, codec='mp3')
                video_clip.close()
            
            with st.spinner("🎙️ AI ဖြင့် အသံများကို စာသားပြောင်းဆိုနေပါပြီ (Whisper API)..."):
                # OpenAI Whisper API ဖြင့် အသံကို စာသားထုတ်ယူခြင်း (ဘာသာစကား အလိုအလျောက် ခွဲခြားပေးမည်)
                with open(audio_path, "rb") as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json"
                    )
            
            st.success("✅ အသံဖမ်းယူမှု ပြီးစီးပါပြီ! မြန်မာဘာသာသို့ ဘာသာပြန်ဆိုနေ습니다...")
            
            # ဘာသာပြန်ရလဒ်များကို ဖော်ပြရန်
            st.subheader("📝 ဘာသာပြန်ရလဒ်များ (Subtitles & Translation):")
            
            # කොටස් (Segments) တစ်ခုချင်းစီကို ဘာသာပြန်ခြင်း
            segments = getattr(transcript, 'segments', [])
            
            if segments:
                for seg in segments:
                    start_time = int(seg['start'])
                    end_time = int(seg['end'])
                    original_text = seg['text']
                    
                    # Google Translator သုံးပြီး မြန်မာလို ဘာသာပြန်ခြင်း
                    try:
                        myanmar_text = GoogleTranslator(source='auto', target='my').translate(original_text)
                    except Exception:
                        myanmar_text = "ဘာသာပြန်ဆိုရန် အခက်အခဲရှိပါသည်။"
                        
                    # အချိန်အလိုက် ထွက်လာသည့် ရလဒ်များကို ပြသခြင်း
                    start_str = f"{start_time // 60:02d}:{start_time % 60:02d}"
                    end_str = f"{end_time // 60:02d}:{end_time % 60:02d}"
                    
                    st.markdown(f"""
                    - **[{start_str} - {end_str}]**
                      - **မူရင်း:** {original_text}
                      - **မြန်မာ:** **{myanmar_text}**
                    """)
            else:
                # Segment မရှိပါက တစ်ခုလုံးကို ဘာသာပြန်ရန်
                full_text = transcript.text
                myanmar_full = GoogleTranslator(source='auto', target='my').translate(full_text)
                st.write(f"**မူရင်းစာသား:** {full_text}")
                st.write(f"**မြန်မာဘာသာပြန်:** {myanmar_full}")
                
            # ယာယီဖိုင်များကို ရှင်းလင်းခြင်း
            if os.path.exists(input_video_path):
                os.remove(input_video_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)
                
        except Exception as e:
            st.error(f"❌ အမှားအယွင်း ဖြစ်ပေါ်သွားပါသည်: {e}")
