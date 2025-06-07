import os
import json
import requests
import argparse
from typing import Dict, List, Optional

def create_document(name: str, embedding_model: str, file_ids: List[int], repos: Optional[List[str]] = None, base_url: str = "http://localhost:9876") -> Dict:
    """
    Create a document with the given name and embedding model, using the provided file IDs and git repositories
    """
    data = {
        "name": name,
        "embedding_model": embedding_model,
        "file_ids": file_ids if file_ids else None
    }
    
    if repos:
        data["repos"] = repos
    
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

def get_available_repos(base_url: str = "http://localhost:9876") -> List[Dict]:
    """
    Get list of available repositories from the API
    """
    try:
        response = requests.get(f"{base_url}/repos/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not fetch available repositories: {e}")
        return []

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Create a document from uploaded files and/or git repositories')
    parser.add_argument('--name', required=True, help='Name of the document')
    parser.add_argument('--embedding-model', default='openai/text-embedding-3-large',
                      help='Embedding model to use (default: openai/text-embedding-3-large)')
    parser.add_argument('--json-file', default='uploaded_files.json',
                      help='Path to the JSON file containing uploaded files info (default: uploaded_files.json)')
    parser.add_argument('--repos', 
                      help='Comma-separated list of git repository names in data/repos folder (e.g., "school-admin,school-api")')
    parser.add_argument('--list-repos', action='store_true',
                      help='List available repositories and exit')
    parser.add_argument('--base-url', default='http://localhost:9876',
                      help='Base URL of the API (default: http://localhost:9876)')
    
    args = parser.parse_args()
    
    # If --list-repos is specified, show available repos and exit
    if args.list_repos:
        print("Available repositories:")
        repos = get_available_repos(args.base_url)
        if repos:
            for repo in repos:
                status = "✅ Git repo" if repo.get('is_git_repo') else "📁 Directory"
                print(f"  - {repo['name']} ({status})")
        else:
            print("  No repositories found or could not connect to API")
        return
    
    # Parse repos argument
    repos_list = []
    if args.repos:
        repos_list = [repo.strip() for repo in args.repos.split(',') if repo.strip()]
        print(f"Will include repositories: {repos_list}")
    
    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct full path to JSON file
    json_file = os.path.join(script_dir, args.json_file)
    
    file_ids = []
    if os.path.exists(json_file):
        try:
            # Load file IDs from JSON
            file_ids = load_file_ids(json_file)
            print(f"Found {len(file_ids)} files to include in the document")
        except Exception as e:
            print(f"Warning: Could not load file IDs from {json_file}: {e}")
    else:
        print(f"Note: File {json_file} not found - creating document without uploaded files")
    
    # Check if we have at least one source (files or repos)
    if not file_ids and not repos_list:
        print("Error: No sources specified! You must provide either:")
        print("  - Uploaded files (via --json-file)")
        print("  - Git repositories (via --repos)")
        print("  - Or both")
        print("\nUse --list-repos to see available repositories")
        return
    
    try:
        # Create the document
        print(f"\nCreating document '{args.name}' with embedding model '{args.embedding_model}'...")
        if repos_list:
            print(f"Including repositories: {repos_list}")
        if file_ids:
            print(f"Including {len(file_ids)} uploaded files")
            
        response = create_document(args.name, args.embedding_model, file_ids, repos_list, args.base_url)
        
        print("\nDocument creation initiated!")
        print(f"Document ID: {response.get('document_id')}")
        print(f"Task ID: {response.get('task_id')}")
        print("\nNote: Document processing will continue in the background.")
        print("You can check the document status through the API or frontend.")
        
    except requests.exceptions.RequestException as e:
        print(f"Error creating document: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"Error details: {error_detail}")
            except:
                print(f"Response content: {e.response.text}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main() 