import os
import sys
import zipfile
import tarfile
import argparse
from tqdm import tqdm
import requests

def IsValidUrl(url):
    try:
        with tqdm(total=100, desc="Verifying URL", unit="%") as progress_bar:
            response = requests.head(url, allow_redirects=True, timeout=5)
            progress_bar.update(100)
        return response.status_code == 200, int(response.headers.get("content-length", 0))
    except requests.exceptions.RequestException:
        return False, 0

def GetFinalUrl(url):
    try:
        session = requests.Session()
        response = session.head(url, allow_redirects=True)
        return response.url
    except requests.exceptions.RequestException:
        return url

def GetFileName(response, url):
    content_disposition = response.headers.get("content-disposition")
    if content_disposition:
        parts = content_disposition.split(";")
        for part in parts:
            if "filename=" in part:
                return part.split("=")[1].strip().strip('"')
    return os.path.basename(url.split("?")[0])

def DownloadFile(url, destination, expected_size):
    try:
        real_url = GetFinalUrl(url)
        response = requests.get(real_url, stream=True)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()
        if "text" in content_type or "html" in content_type:
            return None

        file_name = GetFileName(response, real_url)
        file_path = os.path.join(destination, file_name)

        total_length = int(response.headers.get("content-length", 0))

        with open(file_path, "wb") as f, tqdm(
            total=total_length, unit="B", unit_scale=True, desc="Downloading", dynamic_ncols=True
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))

        downloaded_size = os.path.getsize(file_path)

        with tqdm(total=100, desc="Verifying Download", unit="%") as progress_bar:
            if expected_size and downloaded_size != expected_size:
                os.remove(file_path)
                return None
            progress_bar.update(100)

        return file_path if os.path.exists(file_path) else None

    except requests.exceptions.RequestException:
        return None

def ExtractFile(filePath, destination, force):
    if not os.path.exists(filePath):
        return False

    extract_methods = {
        ".zip": lambda: zipfile.ZipFile(filePath, "r"),
        ".tar.gz": lambda: tarfile.open(filePath, "r:gz"),
        ".tgz": lambda: tarfile.open(filePath, "r:gz"),
        ".tar": lambda: tarfile.open(filePath, "r:")
    }

    ext = next((ext for ext in extract_methods if filePath.endswith(ext)), None)

    if force or ext:
        try:
            archive = extract_methods[ext]()
            members = archive.namelist() if ext == ".zip" else archive.getnames()
            
            with tqdm(total=len(members), desc="Extracting", unit="files") as progress_bar:
                for member in members:
                    archive.extract(member, destination)
                    progress_bar.update(1)

            archive.close()
            os.remove(filePath)

            return True
        except:
            return False
    return False

def Main():
    parser = argparse.ArgumentParser(description="Download and extract an archive from a URL")
    parser.add_argument("-u", "--url", type=str, required=True, help="URL of the archive")
    parser.add_argument("-d", "--destination", type=str, default="extracted_files", help="Extraction destination")
    parser.add_argument("-f", "--force", action="store_true", help="Force extraction without checking the file extension")
    args = parser.parse_args()
    
    is_valid, expected_size = IsValidUrl(args.url)
    if not is_valid:
        sys.exit(1)

    os.makedirs(args.destination, exist_ok=True)
    
    filePath = DownloadFile(args.url, args.destination, expected_size)
    if filePath:
        ExtractFile(filePath, args.destination, args.force)

if __name__ == "__main__":
    Main()
