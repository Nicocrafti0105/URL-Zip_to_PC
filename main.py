import os
import sys
import time
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


def DownloadFile(url, destination, progressCallback):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_length = response.headers.get('content-length')
        if total_length is None:
            print("Warning: No content length provided by the server.")
            return response.content

        total_length = int(total_length)
        downloaded = 0
        file_name = os.path.join(destination, url.split('/')[-1]) if destination else url.split('/')[-1]

        if os.path.exists(file_name):
            print(f"File already exists: {file_name}")
            return file_name, os.path.getsize(file_name)

        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    progressCallback(int(downloaded / total_length * 100))

        if os.path.exists(file_name):
            file_size = os.path.getsize(file_name)
            return file_name, file_size
        else:
            raise Exception("Error: Downloaded file not saved.")
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to download file. {e}")
    except Exception as e:
        print(f"Error: {e}")
    return None, None


def VerifyDownload(filePath, expectedSize, progressCallback):
    if os.path.exists(filePath):
        actual_size = os.path.getsize(filePath)
        for i in range(101):
            time.sleep(0.05)
            progressCallback(i)

        if actual_size == expectedSize:
            return True
        else:
            print("Error: File size mismatch during verification.")
            os.remove(filePath)
            return False
    else:
        print("Error: File not found for verification.")
        os.remove(filePath)
        return False


def ExtractFile(filePath, destination, progressCallback):
    try:
        if filePath.endswith(".zip"):
            with zipfile.ZipFile(filePath, 'r') as zip_ref:
                try:
                    zip_ref.testzip()
                except zipfile.BadZipFile:
                    print(f"Error: The ZIP file {filePath} is corrupted.")
                    return False

                total_files = len(zip_ref.namelist())
                for i, file in enumerate(zip_ref.namelist()):
                    zip_ref.extract(file, destination)
                    progressCallback(int((i + 1) / total_files * 100))

        elif filePath.endswith(".tar.gz") or filePath.endswith(".tgz"):
            with tarfile.open(filePath, "r:gz") as tar_ref:
                try:
                    tar_ref.test()
                except tarfile.TarError:
                    print(f"Error: The TAR file {filePath} is corrupted.")
                    return False

                total_files = len(tar_ref.getnames())
                for i, file in enumerate(tar_ref.getnames()):
                    tar_ref.extract(file, destination)
                    progressCallback(int((i + 1) / total_files * 100))

        elif filePath.endswith(".tar"):
            with tarfile.open(filePath, "r:") as tar_ref:
                try:
                    tar_ref.test()
                except tarfile.TarError:
                    print(f"Error: The TAR file {filePath} is corrupted.")
                    return False

                total_files = len(tar_ref.getnames())
                for i, file in enumerate(tar_ref.getnames()):
                    tar_ref.extract(file, destination)
                    progressCallback(int((i + 1) / total_files * 100))

        elif filePath.endswith(".gz"):
            print("Unsupported archive type: .gz. Only .zip and .tar.gz are supported.")
            return False

        return True
    except (zipfile.BadZipFile, tarfile.TarError) as e:
        print(f"Error: File extraction failed: {e}")
        return False
    except PermissionError as e:
        print(f"Error: Permission denied when extracting files: {e}")
        return False


def DeleteFile(filePath):
    try:
        if os.path.exists(filePath):
            os.remove(filePath)
    except PermissionError as e:
        print(f"Error: Permission denied when deleting file: {e}")


def DownloadProgressBar(totalLength):
    return tqdm(total=totalLength, desc="Downloading", unit="B", unit_scale=True)


def VerifyProgressBar():
    return tqdm(total=100, desc="Verifying", unit="%", unit_scale=True)


def StartDownload(url, destination):
    filePath, fileSize = DownloadFile(url, destination, DownloadProgress)

    if filePath:
        if VerifyDownload(filePath, fileSize, VerifyProgress):
            if ExtractFile(filePath, destination, ExtractProgress):
                DeleteFile(filePath)
        else:
            print("\nVerification failed, retrying...")
            RetryDownload(url, destination)
    else:
        print("\nDownload failed, retrying...")
        RetryDownload(url, destination)


def RetryDownload(url, destination):
    print("\nRetrying download...")
    filePath, fileSize = DownloadFile(url, destination, DownloadProgress)
    if filePath:
        if VerifyDownload(filePath, fileSize, VerifyProgress):
            if ExtractFile(filePath, destination, ExtractProgress):
                DeleteFile(filePath)
        else:
            print("\nVerification failed.")
    else:
        print("\nFailed to download after retry.")
        sys.exit(1)


def DownloadProgress(downloaded):
    downloadBar.update(downloaded - downloadBar.n)


def VerifyProgress(percentage):
    verifyBar.update(percentage - verifyBar.n)


def ExtractProgress(percentage):
    extractBar.update(percentage - extractBar.n)


def Main():
    parser = argparse.ArgumentParser(description="Download and extract a zip or tar.gz file from a URL")
    
    defaultDest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted_files")
    
    parser.add_argument("-u", "--url", type=str, required=True, help="URL path [str]")
    parser.add_argument("-d", "--destination", type=str, default=defaultDest, help="Path where zip is extracted [str]")
    
    args = parser.parse_args()

    if not IsValidUrl(args.url):
        print("Invalid URL.")
        sys.exit(1)

    if not os.path.exists(args.destination):
        try:
            os.makedirs(args.destination)
        except PermissionError as e:
            print(f"Error: Permission denied when creating destination folder: {e}")
            sys.exit(1)

    global downloadBar, verifyBar, extractBar

    downloadBar = DownloadProgressBar(totalLength=100)
    verifyBar = VerifyProgressBar()
    extractBar = tqdm(total=100, desc="Extracting", unit="%", unit_scale=True)

    StartDownload(args.url, args.destination)


if __name__ == "__main__":
    Main()
