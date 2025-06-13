from playwright.sync_api import sync_playwright
import requests
import os
from tqdm import tqdm
from urllib.parse import urlparse, unquote
import ntpath

def download(url):
    download_path = os.path.join(os.getcwd(), 'static', 'downloads')
    os.makedirs(download_path, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        page.wait_for_timeout(3000)
        video_elements = page.locator("video")

        if video_elements.count() == 0:
            print("❌ No video tag found on the page.")
            browser.close()
            return None

        video_url = video_elements.first.get_attribute("src")
        browser.close()

        if not video_url:
            print("❌ Video src attribute not found.")
            return None

        print(f"📥 Downloading video from: {video_url}")

        # Extract filename from URL
        parsed_url = urlparse(video_url)
        basename = ntpath.basename(parsed_url.path)
        filename = unquote(basename.split("?")[0] or "instagram_video.mp4")

        # Remove existing file to avoid duplicates like video(1).mp4
        file_path = os.path.join(download_path, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        success = download_file(video_url, filename, download_path)
        return filename if success else None

def download_file(url, filename, save_dir):
    try:
        response = requests.get(url, stream=True, timeout=20)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
    except Exception as e:
        print(f"❌ Error downloading file: {e}")
        return False

    file_path = os.path.join(save_dir, filename)
    try:
        with open(file_path, "wb") as f, tqdm(
            desc=filename,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
            colour='cyan'
        ) as bar:
            for chunk in response.iter_content(block_size):
                f.write(chunk)
                bar.update(len(chunk))
        print(f"✅ Download complete: {os.path.abspath(file_path)}")
        return True
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return False
