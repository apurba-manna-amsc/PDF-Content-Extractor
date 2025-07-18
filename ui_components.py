import streamlit as st
import base64
from typing import List, Dict, Any
from streamlit_pdf_viewer import pdf_viewer

class UIComponents:
    def __init__(self):
        self.setup_custom_css()
    
    def setup_custom_css(self):
        """Add custom CSS for better styling."""
        st.markdown("""
        <style>
        .main-header {
            text-align: center;
            color: #1f77b4;
            font-size: 2.5rem;
            margin-bottom: 1rem;
            font-weight: bold;
        }
        
        .stats-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        
        .markdown-content {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 0.5rem;
            border: 1px solid #e0e0e0;
            margin: 1rem 0;
            max-height: 600px;
            overflow-y: auto;
        }
        
        .download-section {
            background-color: #e8f4f8;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        
        .footer {
            text-align: center;
            color: #666;
            margin-top: 3rem;
            padding: 1rem;
            border-top: 1px solid #ddd;
        }
        
        .pdf-preview-container {
            margin: 1rem 0;
        }
        
        .processing-time {
            color: #28a745;
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .progress-container {
            margin: 1rem 0;
            padding: 1rem;
            background-color: #f0f8ff;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self):
        """Render the main application header."""
        st.markdown("""
        <div class="main-header">
            📄 PDF Content Extractor
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <p style="font-size: 1.1rem; color: #666;">
                Extract text, tables, images, and formulas from PDF documents with AI-powered analysis
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_pdf_preview(self, pdf_path: str):
        """Render PDF preview in sidebar with narrow, scrollable view."""
        try:
            # Read PDF file
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
            
            st.markdown('<div class="pdf-preview-container">', unsafe_allow_html=True)
            
            # Display PDF using streamlit-pdf-viewer with narrow width
            pdf_viewer(
                input=pdf_data,
                width=280,  # Narrow width for sidebar
                height=400,  # Fixed height with scrolling
                annotation_outline_size=1,
                render_text=True,
                key="pdf_preview"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error displaying PDF preview: {str(e)}")
            st.info("PDF preview not available, but processing will continue normally.")
    
    def create_progress_container(self):
        """Create a container for progress updates."""
        return st.empty()
    
    def update_progress(self, placeholder, progress: float, step: str = ""):
        """Update progress bar with proper cleanup."""
        if placeholder is None:
            return
            
        with placeholder.container():
            st.markdown('<div class="progress-container">', unsafe_allow_html=True)
            
            if progress >= 1.0:
                st.success(f"✅ {step} - Complete!")
            else:
                # Convert to percentage if needed
                if progress > 1:
                    progress = progress / 100
                    
                st.progress(progress, text=f"Processing: {step}")
                st.info(f"Current step: {step} ({progress:.1%} complete)")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def clear_progress(self, placeholder):
        """Clear progress indicators."""
        if placeholder is not None:
            placeholder.empty()
    
    def render_content_stats(self, content: List[Dict[str, Any]]):
        """Render content statistics."""
        if not content:
            st.warning("No content extracted from the PDF.")
            return
        
        # Calculate statistics
        stats = self._calculate_content_stats(content)
        
        # Display statistics in columns
        st.markdown('<div class="stats-container">', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Items", stats["total"])
        with col2:
            st.metric("Text Elements", stats["text"])
        with col3:
            st.metric("Images", stats["images"])
        with col4:
            st.metric("Tables", stats["tables"])
        with col5:
            st.metric("Formulas", stats["formulas"])
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_markdown_content(self, content: List[Dict[str, Any]]):
        """Render the extracted content as formatted markdown."""
        if not content:
            st.warning("No content to display.")
            return
        
        # Generate markdown content
        markdown_content = self._generate_markdown_display(content)
        
        # Display in a scrollable container
        st.markdown('<div class="markdown-content">', unsafe_allow_html=True)
        st.markdown(markdown_content, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_download_buttons(self, download_files: Dict[str, str]):
        """Render download buttons for different formats."""
        st.markdown('<div class="download-section">', unsafe_allow_html=True)
        
        cols = st.columns(len(download_files))
        
        for idx, (format_name, file_content) in enumerate(download_files.items()):
            with cols[idx]:
                file_extension = self._get_file_extension(format_name)
                filename = f"extracted_content.{file_extension}"
                
                st.download_button(
                    label=f"📥 Download {format_name}",
                    data=file_content,
                    file_name=filename,
                    mime=self._get_mime_type(format_name),
                    use_container_width=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_footer(self):
        """Render application footer."""
        st.markdown("""
        <div class="footer">
            <p>Built with ❤️ using Streamlit | Powered by OpenAI GPT-4o</p>
            <p>Upload your PDF and extract structured content with AI assistance</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _calculate_content_stats(self, content: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate statistics for the extracted content."""
        stats = {
            "total": len(content),
            "text": 0,
            "images": 0,
            "tables": 0,
            "formulas": 0
        }
        
        for item in content:
            item_type = item['type'].lower()
            if item_type == 'table':
                stats["tables"] += 1
            elif item_type == 'image':
                stats["images"] += 1
            elif item_type == 'formula':
                stats["formulas"] += 1
            else:
                stats["text"] += 1
        
        return stats
    
    def _generate_markdown_display(self, content: List[Dict[str, Any]]) -> str:
        """Generate markdown content for display."""
        markdown_lines = []
        current_page = 1
        
        for item in content:
            # Add page separator if page changes
            if item['page'] != current_page:
                markdown_lines.append(f"\n---\n\n## Page {item['page']}\n")
                current_page = item['page']
            
            # Format content based on type
            if item['type'] == 'Title':
                markdown_lines.append(f"### {item['content']}\n")
            elif item['type'] == 'Table':
                markdown_lines.append("**Table:**\n")
                markdown_lines.append(item['content'])
                markdown_lines.append("\n")
            elif item['type'] == 'Image':
                markdown_lines.append("**Image:**\n")
                markdown_lines.append(item['content'])
                markdown_lines.append("\n")
            elif item['type'] == 'Formula':
                markdown_lines.append("**Formula:**\n")
                markdown_lines.append(item['content'])
                markdown_lines.append("\n")
            else:
                markdown_lines.append(f"{item['content']}\n")
        
        return "\n".join(markdown_lines)
    
    def _get_file_extension(self, format_name: str) -> str:
        """Get file extension for download format."""
        extensions = {
            'Text': 'txt',
            'Markdown': 'md',
            'JSON': 'json'
        }
        return extensions.get(format_name, 'txt')
    
    def _get_mime_type(self, format_name: str) -> str:
        """Get MIME type for download format."""
        mime_types = {
            'Text': 'text/plain',
            'Markdown': 'text/markdown',
            'JSON': 'application/json'
        }
        return mime_types.get(format_name, 'text/plain')