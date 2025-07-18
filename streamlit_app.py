import os
import json
import time
import tempfile
import streamlit as st
from typing import List, Dict, Any
from pdf_processor import PDFProcessor
from ui_components import UIComponents
from file_manager import FileManager

# Configure Streamlit page
st.set_page_config(
    page_title="PDF Content Extractor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Initialize components
    ui = UIComponents()
    file_manager = FileManager()
    
    # App header
    ui.render_header()
    
    # Sidebar for PDF preview and configuration
    with st.sidebar:
        st.header("📄 PDF Preview")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF file to extract its contents"
        )
        
        # PDF Preview
        if uploaded_file is not None:
            # Save uploaded file temporarily
            temp_pdf_path = file_manager.save_uploaded_file(uploaded_file)
            
            # Render PDF preview in sidebar
            ui.render_pdf_preview(temp_pdf_path)
        
        st.divider()
        
        # Configuration section
        st.header("⚙️ Configuration")
        
        # OpenAI API Key input
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-proj-...",
            help="Enter your OpenAI API key to process images and formulas"
        )
        
        # Processing options
        st.subheader("Processing Options")
        process_images = st.checkbox("Process Images", value=True)
        process_formulas = st.checkbox("Process Formulas", value=True)
        process_tables = st.checkbox("Process Tables", value=True)
        
        # Download format options
        st.subheader("Download Options")
        download_formats = st.multiselect(
            "Select download formats",
            ["Text", "Markdown", "JSON"],
            default=["Text", "Markdown", "JSON"]
        )
    
    # Main content area
    if uploaded_file is not None:
        # Process button
        if st.button("🚀 Process PDF", type="primary", use_container_width=True):
            if not openai_api_key:
                st.error("Please enter your OpenAI API key to proceed")
                return
            
            # Clear any previous results
            if 'extracted_content' in st.session_state:
                del st.session_state['extracted_content']
            
            # Initialize processor
            processor = PDFProcessor(openai_api_key)
            
            # Start timing
            start_time = time.time()
            
            # Create progress container using UI components
            progress_placeholder = ui.create_progress_container()
            
            # Define progress callback function
            def update_progress(step: str, progress: float):
                """Update progress bar and status message"""
                ui.update_progress(progress_placeholder, progress, step)
            
            # Process PDF with progress tracking
            try:
                extracted_content = processor.process_pdf(
                    temp_pdf_path,
                    process_images=process_images,
                    process_formulas=process_formulas,
                    process_tables=process_tables,
                    progress_callback=update_progress
                )
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                # Clear progress indicators
                ui.clear_progress(progress_placeholder)
                
                # Store results in session state
                st.session_state.extracted_content = extracted_content
                st.session_state.processed_file_name = uploaded_file.name
                st.session_state.processing_time = processing_time
                
                # Show success message
                st.success(f"✅ Processing completed in {processing_time:.1f} seconds")
                
                # Force a rerun to display results immediately
                st.rerun()
                
            except Exception as e:
                # Clear progress indicators on error
                ui.clear_progress(progress_placeholder)
                
                # Show error message
                st.error(f"❌ Error processing PDF: {str(e)}")
                st.exception(e)
            
            finally:
                # Always cleanup temporary file
                if 'temp_pdf_path' in locals():
                    file_manager.cleanup_temp_file(temp_pdf_path)
    
    # Display results
    if 'extracted_content' in st.session_state:
        st.header("📊 Extracted Content")
        
        content = st.session_state.extracted_content
        
        # Display processing time
        if 'processing_time' in st.session_state:
            st.markdown(f"""
            <div class="processing-time">
                ⏱️ Processing completed in {st.session_state.processing_time:.1f} seconds
            </div>
            """, unsafe_allow_html=True)
        
        # Display content statistics
        ui.render_content_stats(content)
        
        # Display extracted content as markdown
        ui.render_markdown_content(content)
        
        # Download section
        st.header("⬇️ Download Results")
        
        # Generate download files
        download_files = file_manager.generate_download_files(
            content, 
            st.session_state.processed_file_name,
            download_formats
        )
        
        # Download buttons
        ui.render_download_buttons(download_files)
        
    else:
        st.info("👆 Upload a PDF file from the sidebar and click 'Process PDF' to extract its contents")
    
    # Footer
    ui.render_footer()

if __name__ == "__main__":
    main()