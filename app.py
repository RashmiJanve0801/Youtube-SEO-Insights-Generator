import os
from dotenv import load_dotenv
import streamlit as st

from src.utils.video_extractor import get_video_metadata
from src.core.seo_engine import SEOEngine

from src.common.logger import get_logger
from src.common.custom_exception import CustomException

load_dotenv()

logger = get_logger(__name__)

st.set_page_config(page_title="AI YT SEO Insights", layout="wide")
st.title("YT SEO Insights Generator")
st.write("Generate Tags, Audience Analysis, Timestamps AI Generated, Flaws Suggestions")

with st.sidebar:
    st.header("API Settings")
    api_key = st.text_input("Google API Key", type="password")

    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        logger.info("API Key added to environment variables.")

st.divider()

url = st.text_input("Enter the YT URL")

if "seo_data" not in st.session_state:
    st.session_state.seo_data=None

if url:
    try:
        metadata = get_video_metadata(url)

        st.subheader("Video Details")
        st.write(f"**Title:** {metadata['title']}")
        st.write(f"**Creator:** {metadata['author']}")
        st.write(f"**Views:** {metadata['views']}")

        duration = metadata['duration']
        minutes = duration // 60
        st.write(f"**Duration:** {minutes} minutes")

        st.image(metadata['thumbnail_url'], width=400)

        if st.button("Generate Insights"):
            if not os.getenv("GOGLE_API_KEY"):
                st.error("Add the API Key first")

            with st.spinner("Analyzing with AI... "):
                seo_engine = SEOEngine()
                st.session_state.seo_data = seo_engine.generate(metadata)
                logger.info("SEO Insights Generated successfully.. ")

    except Exception as e:
        logger.error(f"Unexpected Error : {str(e)}")
        st.error("Unexpected error. Check logs for more details")


data = st.session_state.seo_data
if data:
    st.subheader("SEO Friendly Tags")
    cols = st.columns(3)

    for i, tag in enumerate(data["tags"]):
        with cols[i%3]:
            st.write(tag)

    if st.button("Copy Tags"):
        st.code(" ".join([f'#{t}' for t in data["tags"]]))
        logger.info("Tags copied by user")

    st.divider()
    

    st.subheader("Target Audience Analysis")
    st.write(data["audience"])

    st.divider()


    st.subheader("AI Generated Timestamps")
    for ts in data["timestamps"]:
        st.markdown(f"**{ts['time']} - {ts['description']}**")

    st.info("Generated Timestamps for the video")

    st.divider()

    st.subheader("Flaws and Improvements")
    st.write("These issues can hurt your SEO rankings")

    for flaw in data["flaws"]:
        st.markdown(f"""
            **❌ Issue:**  {flaw['issue']}  

            **⚡Why It Hurts:** {flaw['why_it_hurts']}  
            
            **✅ Fix:** {flaw['fix']}  
        """)



