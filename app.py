from flask import Flask, request, send_file, render_template, jsonify
import os
import yt_dlp

app = Flask(__name__)
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'temp_downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/download", methods=["POST"])
def download_video():
    url = request.json.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Setup output template
    output_template = os.path.join(DOWNLOAD_FOLDER, "%(title)s_%(id)s.%(ext)s")

    ydl_opts = {
        'outtmpl': output_template,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': True,
        'noplaylist': True,
    }

    # Extract and download the video
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".mp4")  # handle merge_output_format
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

    if not os.path.exists(filename):
        return jsonify({"error": "Downloaded file not found"}), 500

    return jsonify({"filename": os.path.basename(filename)})

@app.route("/api/file/<filename>")
def send_video_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    else:
        return "File not found", 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000);
