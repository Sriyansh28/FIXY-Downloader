import yt_dlp
import os

def download(url):
    download_path = os.path.join(os.getcwd(), 'static', 'downloads')
    os.makedirs(download_path, exist_ok=True)

    final_filename = {"name": None}

    def progress_hook(d):
        if d['status'] == 'downloading':
            downloaded = d.get('_percent_str', '').strip()
            speed = d.get('_speed_str', '')
            eta = d.get('_eta_str', '')
            print(f"📥 {downloaded} at {speed} - ETA {eta}", end='\r')
        elif d['status'] == 'finished':
            filename = os.path.basename(d['filename'])
            filepath = os.path.join(download_path, filename)

            # Remove any existing file to avoid duplicates like filename(1).mp4
            if os.path.exists(filepath):
                os.remove(filepath)

            final_filename["name"] = filename
            print(f"\n✅ Download finished: {filename}")

    ydl_opts = {
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': False,
        'noplaylist': True,
        'progress_hooks': [progress_hook],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        return None

    return final_filename["name"]
