import os
import json
import requests
import argparse
from typing import Dict, List

def create_document(name: str, embedding_model: str, file_ids: List[int], base_url: str = "http://localhost:9876") -> Dict:
    """
    Create a document with the given name and embedding model, using the provided file IDs
    """
    data = {
        "name": name,
        "embedding_model": embedding_model,
        "file_ids": file_ids
    }
    
    response = requests.post(f"{base_url}/documents/", json=data)
    response.raise_for_status()
    return response.json()

def load_file_ids(json_file: str) -> List[int]:
    """
    Load file IDs from the uploaded_files.json
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
    return [item['id'] for item in data]

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Create a document from uploaded files')
    parser.add_argument('--name', required=True, help='Name of the document')
    parser.add_argument('--embedding-model', default='openai/text-embedding-3-large',
                      help='Embedding model to use (default: openai/text-embedding-3-large)')
    parser.add_argument('--json-file', default='uploaded_files.json',
                      help='Path to the JSON file containing uploaded files info (default: uploaded_files.json)')
    
    args = parser.parse_args()
    
    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct full path to JSON file
    json_file = os.path.join(script_dir, args.json_file)
    
    if not os.path.exists(json_file):
        print(f"Error: File {json_file} not found!")
        return
    
    try:
        # Load file IDs from JSON
        file_ids = load_file_ids(json_file)
        
        if not file_ids:
            print("No file IDs found in the JSON file!")
            return
        
        print(f"Found {len(file_ids)} files to include in the document")
        
        # Create the document
        print(f"\nCreating document '{args.name}' with embedding model '{args.embedding_model}'...")
        response = create_document(args.name, args.embedding_model, file_ids)
        
        print("\nDocument creation initiated!")
        print(f"Document ID: {response.get('document_id')}")
        print(f"Task ID: {response.get('task_id')}")
        print("\nNote: Document processing will continue in the background.")
        print("You can check the document status through the API or frontend.")
        
    except requests.exceptions.RequestException as e:
        print(f"Error creating document: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main() 