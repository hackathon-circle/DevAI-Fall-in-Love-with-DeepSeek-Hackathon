import os
import re
from typing import List, Dict, Any

def traverse_files(directory: str) -> List[str]:
    """Traverse through directory and return all file paths."""
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

def read_file_content(file_path: str) -> List[str]:
    """Read file content and return lines with line numbers."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.readlines()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []

def get_relevant_lines(content: List[str], query: str) -> List[Dict[str, Any]]:
    """Find relevant lines based on the search query."""
    relevant_lines = []
    for i, line in enumerate(content, 1):
        if query.lower() in line.lower():
            relevant_lines.append({
                'line_number': i,
                'content': line.strip()
            })
    return relevant_lines

def format_response(query: str, matches: Dict[str, List[Dict[str, Any]]]) -> str:
    """Format the search results according to the specified response format."""
    response = f"<QUERY>\n{query}\n</QUERY>\n\n"
    
    if matches:
        response += "<CODE_TO_CHANGE>\n"
        for file_path, lines in matches.items():
            response += f"    <FILE_PATH>\n        {file_path}\n    </FILE_PATH>\n"
            response += "    <CODE>\n"
            for line in lines:
                response += f"        {line['line_number']}  {line['content']}\n"
            response += "    </CODE>\n\n"
        response += "</CODE_TO_CHANGE>"
    else:
        response += "<NO_MATCHES>No relevant code found.</NO_MATCHES>"
    
    return response

def search_codebase(directory: str, query: str) -> str:
    """Main function to search through codebase."""
    # Step 1: File traversal
    file_paths = traverse_files(directory)
    
    # Step 2: Read and find relevant files/lines
    matches = {}
    for file_path in file_paths:
        content = read_file_content(file_path)
        relevant_lines = get_relevant_lines(content, query)
        if relevant_lines:
            matches[file_path] = relevant_lines
    
    # Step 3: Format response
    return format_response(query, matches)

if __name__ == "__main__":
    # Example usage
    directory = "sameple-codebase"  # Directory to search in
    query = input("Enter search query: ")
    result = search_codebase(directory, query)
    print(result)