

import streamlit as st
import requests

# Define the Flask API endpoints
ANALYZE_URL = "http://localhost:5000/analyze"
ASK_URL = "http://localhost:5000/ask"

def analyze_video(video_url):
    response = requests.post(ANALYZE_URL, json={'video_url': video_url})
    if response.status_code == 200:
        data = response.json()
        return data['transcript']
    else:
        st.error("Failed to analyze video")
        return None

def ask_question(question, transcript):
    response = requests.post(ASK_URL, json={'question': question, 'transcript': transcript})
    if response.status_code == 200:
        data = response.json()
        return data['answer']
    else:
        st.error("Failed to get answer")
        return None

def main():
    st.markdown(
        """
        <style>
        .main-title {
            font-size: 3em;
            color: #4CAF50;
            text-align: center;
            margin-bottom: 0.5em;
        }
        .sub-title {
            font-size: 1.5em;
            color: #2196F3;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }
        .transcript-box, .answer-box {
            background-color: #f0f0f5;
            color:black;
            padding: 1em;
            border-radius: 5px;
            margin-bottom: 1em;
        }
        .warning-box {
            background-color: #ffcccb;
            padding: 1em;
            border-radius: 5px;
            margin-bottom: 1em;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

    st.markdown('<h1 class="main-title">YouTube Video Analysis</h1>', unsafe_allow_html=True)

    video_url = st.text_input("Enter YouTube Video URL:")
    analyze_button = st.button("Analyze Video")

    # Check if analyze button is clicked and video_url is provided
    if analyze_button and video_url:
        transcript = analyze_video(video_url)
        if transcript:
            st.session_state['transcript'] = transcript
        else:
            st.markdown('<div class="warning-box">Failed to analyze video. Please check the video URL.</div>', unsafe_allow_html=True)

    # Display transcript if available in session state
    if 'transcript' in st.session_state:
        st.markdown('<h2 class="sub-title">Transcript:</h2>', unsafe_allow_html=True)
        st.markdown(f'<div class="transcript-box">{st.session_state["transcript"]}</div>', unsafe_allow_html=True)

        question = st.text_input("Ask a question about the video:")
        ask_button = st.button("Ask")

        # Check if ask button is clicked and question is provided
        if ask_button and question:
            answer = ask_question(question, st.session_state['transcript'])
            if answer:
                st.markdown('<h2 class="sub-title">Answer:</h2>', unsafe_allow_html=True)
                st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="warning-box">No answer received or answer is empty.</div>', unsafe_allow_html=True)
        elif ask_button:
            st.markdown('<div class="warning-box">Please enter a question.</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
