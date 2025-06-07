import os
import json
import requests
from pathlib import Path
from typing import Dict, List

def upload_file(file_path: str, base_url: str = "http://localhost:9876") -> Dict:
    """
    Upload a single file to the server and return the response
    """
    with open(file_path, 'rb') as f:
        files = {'uploaded_file': (os.path.basename(file_path), f)}
        response = requests.post(f"{base_url}/files/", files=files)
        response.raise_for_status()
        return response.json()

def recursive_upload(directory: str, base_url: str = "http://localhost:9876") -> List[Dict]:
    """
    Recursively upload all files in a directory and return a list of responses
    """
    uploaded_files = []
    directory_path = Path(directory)

    # Walk through directory recursively
    for root, _, files in os.walk(directory_path):
        for file in files:
            # Skip the script itself and the output JSON file
            if file in ['recursive_upload.py', 'uploaded_files.json']:
                continue
                
            file_path = os.path.join(root, file)
            try:
                print(f"Uploading {file_path}...")
                response = upload_file(file_path, base_url)
                
                # Add relative path information to response
                response['relative_path'] = os.path.relpath(file_path, directory_path)
                uploaded_files.append(response)
                
                print(f"Successfully uploaded {file_path} with ID {response['id']}")
            except Exception as e:
                print(f"Failed to upload {file_path}: {str(e)}")

    return uploaded_files

def main():
    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Directory to upload (relative to script location)
    upload_dir = os.path.join(script_dir, "d4f/generated")
    
    # Make sure the directory exists
    if not os.path.exists(upload_dir):
        print(f"Directory {upload_dir} does not exist!")
        return

    # Upload all files
    results = recursive_upload(upload_dir)
    
    # Save results to JSON file in the same directory as the script
    output_file = os.path.join(script_dir, "uploaded_files.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nUpload complete! Results saved to {output_file}")
    print(f"Total files uploaded: {len(results)}")

if __name__ == "__main__":
    main() 