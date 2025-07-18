import os
import json
import tempfile
from typing import List, Dict, Any
import streamlit as st

class FileManager:
    def __init__(self):
        self.temp_files = []
    
    def save_uploaded_file(self, uploaded_file) -> str:
        """Save uploaded file to temporary location."""
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.write(uploaded_file.getbuffer())
            temp_file.close()
            
            # Track temporary file for cleanup
            self.temp_files.append(temp_file.name)
            
            return temp_file.name
            
        except Exception as e:
            st.error(f"Error saving uploaded file: {str(e)}")
            return None
    
    def cleanup_temp_file(self, file_path: str):
        """Delete a specific temporary file."""
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
                if file_path in self.temp_files:
                    self.temp_files.remove(file_path)
        except Exception as e:
            st.error(f"Error cleaning up temporary file: {str(e)}")
    
    def cleanup_all_temp_files(self):
        """Clean up all temporary files."""
        for file_path in self.temp_files.copy():
            self.cleanup_temp_file(file_path)
    
    def generate_download_files(self, content: List[Dict[str, Any]], 
                               original_filename: str, 
                               formats: List[str]) -> Dict[str, str]:
        """Generate download files in different formats."""
        download_files = {}
        
        if "Text" in formats:
            download_files["Text"] = self._generate_text_format(content)
        
        if "Markdown" in formats:
            download_files["Markdown"] = self._generate_markdown_format(content)
        
        if "JSON" in formats:
            download_files["JSON"] = self._generate_json_format(content, original_filename)
        
        return download_files
    
    def _generate_text_format(self, content: List[Dict[str, Any]]) -> str:
        """Generate plain text format."""
        text_content = []
        text_content.append("PDF CONTENT EXTRACTION RESULTS")
        text_content.append("=" * 50)
        text_content.append("")
        
        current_page = 1
        for item in content:
            # Add page separator if page changes
            if item['page'] != current_page:
                text_content.append(f"\n--- PAGE {item['page']} ---\n")
                current_page = item['page']
            
            # Add content type header
            text_content.append(f"[{item['type'].upper()}]")
            
            # Add content
            if item['type'] == 'Table':
                text_content.append("TABLE CONTENT (HTML):")
                text_content.append(item['content'])
            else:
                text_content.append(item['content'])
            
            text_content.append("")  # Empty line separator
        
        return "\n".join(text_content)
    
    def _generate_markdown_format(self, content: List[Dict[str, Any]]) -> str:
        """Generate markdown format."""
        md_content = []
        md_content.append("# PDF Content Extraction Results")
        md_content.append("")
        
        current_page = 1
        for item in content:
            # Add page separator if page changes
            if item['page'] != current_page:
                md_content.append(f"## Page {item['page']}")
                md_content.append("")
                current_page = item['page']
            
            # Format content based on type
            if item['type'] == 'Title':
                md_content.append(f"### {item['content']}")
            elif item['type'] == 'Table':
                md_content.append("**Table:**")
                md_content.append("")
                md_content.append(item['content'])
            elif item['type'] == 'Image':
                md_content.append("**Image Description:**")
                md_content.append("")
                md_content.append(item['content'])
            elif item['type'] == 'Formula':
                md_content.append("**Formula:**")
                md_content.append("")
                md_content.append(item['content'])
            else:
                md_content.append(item['content'])
            
            md_content.append("")  # Empty line separator
        
        return "\n".join(md_content)
    
    def _generate_json_format(self, content: List[Dict[str, Any]], original_filename: str) -> str:
        """Generate JSON format."""
        json_data = {
            "metadata": {
                "original_filename": original_filename,
                "total_items": len(content),
                "extraction_info": {
                    "total_pages": max([item['page'] for item in content]) if content else 0,
                    "content_types": list(set([item['type'] for item in content]))
                }
            },
            "content": content
        }
        
        return json.dumps(json_data, indent=2, ensure_ascii=False)