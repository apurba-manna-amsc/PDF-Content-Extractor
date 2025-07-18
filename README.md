# PDF Content Extractor

A powerful Streamlit application that extracts and processes content from PDF documents, including text, images, formulas, and tables. The application uses advanced AI models to interpret visual elements and convert them into structured, readable formats.

## 🚀 Features

- **📄 PDF Processing**: Upload and process PDF files with high-resolution conversion
- **🖼️ Image Extraction**: Automatically detects and extracts images from PDFs
- **📊 Table Processing**: Extracts tables and converts them to HTML format
- **🔢 Formula Recognition**: Identifies mathematical formulas and converts them to LaTeX
- **📝 Text Extraction**: Extracts all text content with proper formatting
- **🎯 AI-Powered Analysis**: Uses OpenAI GPT-4 Vision for intelligent content interpretation
- **📱 Interactive UI**: Clean, responsive Streamlit interface with real-time progress tracking
- **⬇️ Multiple Export Formats**: Download results in Text, Markdown, or JSON formats
- **🔧 Configurable Processing**: Toggle processing options for different content types

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key (for image and formula processing)
- Poppler (for PDF to image conversion)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/apurba-manna-amsc/PDF-Content-Extractor.git
   cd PDF-Content-Extractor
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Poppler (Required for pdf2image):**
   
   **Windows:**
   ```bash
   # Download and install from: https://poppler.freedesktop.org/
   # Or use conda:
   conda install -c conda-forge poppler
   ```
   
   **macOS:**
   ```bash
   brew install poppler
   ```
   
   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt-get install poppler-utils
   ```

## 📦 Dependencies

Create a `requirements.txt` file with the following dependencies:

```txt
streamlit>=1.28.0
openai>=1.3.0
pdf2image>=1.16.0
Pillow>=9.0.0
unstructured[pdf]>=0.10.0
layoutparser>=0.3.4
detectron2>=0.6
torch>=1.9.0
torchvision>=0.10.0
numpy>=1.21.0
```

## 🚀 Usage

1. **Start the application:**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Open your browser** and navigate to `http://localhost:8501`

3. **Upload a PDF file** using the sidebar file uploader

4. **Configure processing options:**
   - Enter your OpenAI API key
   - Select content types to process (Images, Formulas, Tables)
   - Choose download formats

5. **Process the PDF** by clicking the "🚀 Process PDF" button

6. **View and download results** in your preferred format

## 📁 Project Structure

```
PDF-Content-Extractor/
├── streamlit_app.py          # Main Streamlit application
├── pdf_processor.py          # Core PDF processing logic
├── ui_components.py          # UI components and styling
├── file_manager.py           # File handling utilities
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
└── screenshots/              # Application screenshots
```

## 🔧 Configuration

### OpenAI API Key
The application requires an OpenAI API key to process images and formulas. You can obtain one from [OpenAI's platform](https://platform.openai.com/api-keys).

### Processing Options
- **Process Images**: Extract and analyze images using GPT-4 Vision
- **Process Formulas**: Convert mathematical formulas to LaTeX format
- **Process Tables**: Extract tables and convert to HTML structure

## 📊 Output Formats

The application provides multiple output formats:

1. **Text (.txt)**: Plain text extraction of all content
2. **Markdown (.md)**: Structured markdown with proper formatting
3. **JSON (.json)**: Machine-readable structured data with metadata

## 🎯 Core Components

### PDFProcessor
- Converts PDF pages to high-resolution images
- Extracts content using the `unstructured` library
- Processes images and formulas using OpenAI GPT-4 Vision
- Handles image enhancement and quality optimization

### UIComponents
- Provides a clean, responsive interface
- Real-time progress tracking
- PDF preview functionality
- Download management

### FileManager
- Handles file uploads and temporary file management
- Generates downloadable content in multiple formats
- Manages cleanup of temporary files

## 🤖 AI Features

The application leverages OpenAI's GPT-4 Vision model for:
- **Image Analysis**: Interprets technical diagrams, flowcharts, and visual structures
- **Formula Recognition**: Converts mathematical expressions to LaTeX format
- **Content Understanding**: Provides contextual descriptions of visual elements

## 📸 Screenshots

### Main Application Interface
![Main Interface](screenshots/main-interface.png)
*Clean, intuitive dashboard with PDF upload and configuration options*

### PDF Processing in Action
![Processing Progress](screenshots/processing-progress.png)
*Real-time progress tracking during content extraction*

### Extracted Content Results
![Extracted Content](screenshots/extracted-content.png)
*AI-processed content showing text, images, formulas, and tables*

### Download Options
![Download Options](screenshots/download-options.png)
*Multiple export formats available for download*

## 🔍 Troubleshooting

### Common Issues:

1. **Poppler Installation Error:**
   - Ensure Poppler is properly installed and in your system PATH
   - Try using conda: `conda install -c conda-forge poppler`

2. **OpenAI API Errors:**
   - Verify your API key is valid and has sufficient credits
   - Check your internet connection

3. **Memory Issues with Large PDFs:**
   - The application automatically handles large images
   - Consider processing smaller sections if you encounter memory issues

4. **Dependency Conflicts:**
   - Use a virtual environment to avoid conflicts
   - Ensure all dependencies are up to date

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Apurba Manna**
- Email: [98apurbamanna@gmail.com](mailto:98apurbamanna@gmail.com)
- GitHub: [@apurba-manna-amsc](https://github.com/apurba-manna-amsc)
- Project Link: [PDF-Content-Extractor](https://github.com/apurba-manna-amsc/PDF-Content-Extractor)

## 🙏 Acknowledgments

- OpenAI for providing the GPT-4 Vision API
- Streamlit for the amazing web framework
- The `unstructured` library for PDF processing capabilities
- All contributors and users of this project

## 📈 Future Enhancements

- [ ] Support for password-protected PDFs
- [ ] Batch processing of multiple PDFs
- [ ] Custom AI model integration
- [ ] Advanced table formatting options
- [ ] Cloud deployment options
- [ ] API endpoint for programmatic access

---

⭐ **Star this repository if you find it helpful!**
