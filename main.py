import os
import sys
import zipfile
import tarfile
import argparse
from tqdm import tqdm
import requests

def IsValidUrl(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error: Invalid URL or network issue. {e}")
        return False

def GetFinalUrl(url):
    try:
        session = requests.Session()
        response = session.head(url, allow_redirects=True)
        return response.url  # Get the final URL after redirections
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to resolve final URL. {e}")
        return url  # Return original URL if it fails

def GetFileName(response, url):
    content_disposition = response.headers.get("content-disposition")
    if content_disposition:
        parts = content_disposition.split(";")
        for part in parts:
            if "filename=" in part:
                return part.split("=")[1].strip().strip('"')
    return os.path.basename(url.split("?")[0])

def DownloadFile(url, destination):
    try:
        real_url = GetFinalUrl(url)  # Get the actual file URL
        response = requests.get(real_url, stream=True)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()
        if "text" in content_type or "html" in content_type:
            print("Error: URL is not returning a file.")
            print("Response Preview:", response.text[:500])  # Debugging output
            return None

        file_name = GetFileName(response, real_url)
        file_path = os.path.join(destination, file_name)

        total_length = response.headers.get("content-length")
        total_length = int(total_length) if total_length else None

        with open(file_path, "wb") as f, tqdm(
            total=total_length, unit="B", unit_scale=True, desc="Downloading"
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))

        return file_path if os.path.exists(file_path) else None

    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to download file. {e}")
    return None

def ExtractFile(filePath, destination, force):
    if not os.path.exists(filePath):
        print(f"Error: File '{filePath}' not found for extraction.")
        return False

    extract_methods = {
        ".zip": lambda: zipfile.ZipFile(filePath, "r").extractall(destination),
        ".tar.gz": lambda: tarfile.open(filePath, "r:gz").extractall(destination),
        ".tgz": lambda: tarfile.open(filePath, "r:gz").extractall(destination),
        ".tar": lambda: tarfile.open(filePath, "r:").extractall(destination),
    }

    ext = next((ext for ext in extract_methods if filePath.endswith(ext)), None)

    if force or ext:
        with tqdm(total=100, desc="Extracting", unit="%") as progress_bar:
            extract_methods.get(ext, lambda: print("Unsupported file type."))()
            progress_bar.update(100)
        return True
    else:
        print("Unsupported file type.")
        return False

def Main():
    parser = argparse.ArgumentParser(description="Download and extract an archive from a URL")
    parser.add_argument("-u", "--url", type=str, required=True, help="URL of the archive")
    parser.add_argument("-d", "--destination", type=str, default="extracted_files", help="Extraction destination")
    parser.add_argument("-f", "--force", action="store_true", help="Force extraction without checking the file extension")
    args = parser.parse_args()
    
    if not IsValidUrl(args.url):
        print("Invalid URL.")
        sys.exit(1)

    os.makedirs(args.destination, exist_ok=True)
    
    filePath = DownloadFile(args.url, args.destination)
    if filePath:
        ExtractFile(filePath, args.destination, args.force)

if __name__ == "__main__":
    Main()
