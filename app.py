from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import google.generativeai as genai
from flask_cors import CORS
import requests
import os


# Configure Google Gemini API
genai.configure(api_key="AIzaSyC8r16Um9YYeBP-_GOSSZDDMHxDgBa4N2s")

# Initialize Flask app
app = Flask(__name__)
CORS(app) 

# Define a prompt for summary generation
PROMPT = "You are given the captions of a video. Summarize its content comprehensively."

# Function to extract YouTube transcript
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[-1]
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)

        # Concatenate transcript segments
        transcript = " ".join(segment['text'] for segment in transcript_data)
        return transcript

    except TranscriptsDisabled:
        raise Exception("Captions are disabled for this video.")
    except NoTranscriptFound:
        raise Exception("No captions or subtitles were found for this video.")
    except VideoUnavailable:
        raise Exception("The video is unavailable. Please check the URL.")
    except Exception as e:
        raise Exception(f"Unexpected error fetching transcripts: {str(e)}")

# Function to generate content using Google Gemini
def generate_gemini_content(transcript_text, prompt):
    try:
        input_text = (transcript_text + prompt)[300:]  # Ensure input length is manageable
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(input_text)
        return response.text
    except Exception as e:
        raise Exception(f"Error generating summary with Gemini API: {str(e)}")

# Function to fetch video details (title, thumbnail)
def fetch_video_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[-1]
        api_key = "AIzaSyC8r16Um9YYeBP-_GOSSZDDMHxDgBa4N2s"
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}"

        response = requests.get(url)
        if response.status_code == 200:
            video_data = response.json()
            if video_data["items"]:
                title = video_data["items"][0]["snippet"]["title"]
                thumbnail = video_data["items"][0]["snippet"]["thumbnails"]["high"]["url"]
                return title, thumbnail
            else:
                raise Exception("Video details not found.")
        else:
            raise Exception(f"Failed to fetch video details: {response.status_code}")
    except Exception as e:
        raise Exception(f"Error fetching video details: {str(e)}")

# Route to summarize video
@app.route('/summarize', methods=['POST'])
def summarize_video():
    try:
        # Get YouTube URL from the request body
        data = request.json
        youtube_link = data.get('youtube_url')

        if not youtube_link:
            return jsonify({"error": "YouTube URL is required."}), 400

        # Extract transcript
        transcript_text = extract_transcript_details(youtube_link)
        if not transcript_text:
            return jsonify({"error": "Could not retrieve transcript for the provided URL."}), 400

        # Fetch video details
        title, thumbnail = fetch_video_details(youtube_link)

        # Generate summary
        summary = generate_gemini_content(transcript_text, PROMPT)

        return jsonify({
            "title": title,
            "thumbnail": thumbnail,
            "summary": summary
        }), 200

    except TranscriptsDisabled:
        return jsonify({"error": "Captions are disabled for this video."}), 400
    except NoTranscriptFound:
        return jsonify({"error": "No subtitles or captions were found for this video."}), 400
    except VideoUnavailable:
        return jsonify({"error": "The video is unavailable. Please check the URL."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    # Production-ready configurations
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)