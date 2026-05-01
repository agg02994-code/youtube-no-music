from flask import Flask, request, jsonify, send_file
import yt_dlp
import subprocess
import os
import uuid

app = Flask(__name__)

@app.post("/process")
def process():
    data = request.get_json()
    url = data["url"]

    file_id = str(uuid.uuid4())
    video_file = f"{file_id}.mp4"
    audio_file = f"{file_id}.mp3"
    output_dir = f"separated/{file_id}"
    final_video = f"{file_id}_nomusic.mp4"

    ydl_opts = {
        "format": "bestvideo+bestaudio",
        "outtmpl": file_id,
        "merge_output_format": "mp4"
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    subprocess.run([
        "ffmpeg", "-i", f"{file_id}.mp4", "-q:a", "0", "-map", "a", audio_file
    ])

    subprocess.run(["demucs", audio_file, "-o", "separated"])

    vocal_path = f"{output_dir}/htdemucs/vocals.wav"

    subprocess.run([
        "ffmpeg", "-i", f"{file_id}.mp4", "-i", vocal_path,
        "-c:v", "copy", "-map", "0:v:0", "-map", "1:a:0",
        final_video
    ])

    return jsonify({"video": final_video})

@app.get("/<path:path>")
def serve_file(path):
    return send_file(path)

app.run(host="0.0.0.0", port=5000)
