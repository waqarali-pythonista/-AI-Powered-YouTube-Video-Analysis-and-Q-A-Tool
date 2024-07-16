from flask import Flask, request, jsonify
import googleapiclient.discovery
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import re

my_key = ""
MODEL = "gpt-4"
client = OpenAI(api_key=my_key)

app = Flask(__name__)

# Configure your API keys
YOUTUBE_API_KEY = ""

def extract_video_id(url):
    pattern = re.compile(r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})')
    match = pattern.search(url)
    if match:
        return match.group(1)
    return None

def get_video_transcript(video_id):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    response = request.execute()
    
    transcript = ""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([t['text'] for t in transcript_list])
    except Exception as e:
        transcript = "Transcript not available."
    
    return response, transcript

def summarize_transcript(transcript):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": f"Summarize the following transcript:\n\n{transcript}"}],
        max_tokens=150
    )
    summary = response.choices[0].message.content.strip()
    return summary

@app.route('/analyze', methods=['POST'])
def analyze():
    video_url = request.json.get('video_url')
    video_id = extract_video_id(video_url)
    video_details, transcript = get_video_transcript(video_id)
    summary = summarize_transcript(transcript)
    return jsonify({'summary': summary, 'transcript': transcript, 'video_details': video_details})

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get('question')
    transcript = request.json.get('transcript')
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": f"Answer the following question based on the transcript:\n\nTranscript: {transcript}\n\nQuestion: {question}"}]
    )
    
    answer = response.choices[0].message.content.strip()
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)
