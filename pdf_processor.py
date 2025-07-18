import os
import base64
import logging
import tempfile
from typing import List, Dict, Any, Callable, Optional
from PIL import Image, ImageEnhance
from pdf2image import convert_from_path
import openai
from unstructured.partition.pdf import partition_pdf

# Increase PIL's decompression bomb limit
Image.MAX_IMAGE_PIXELS = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, openai_api_key: str):
        """Initialize the PDF Processor with OpenAI API key."""
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.pdf_images = None
        
        # Prompts for different content types
        self.prompt_image = """
You are an expert in visual-to-text conversion with a focus on technical diagrams and flowcharts.

I will give you an image that may contain a diagram, flowchart, cycle, chart, infographic, or visual structure.

Your task is to:
1. Carefully examine the image for any text, symbols, arrows, or structural elements
2. If the image is blurry or unclear, describe what you can see and ask for clarification
3. Extract the visual structure and convert it into a clean, readable format
4. Preserve the direction, flow, and relationships between elements
5. Use arrows (↓, →, ↺) and indentation to reflect hierarchy and flow
6. If you cannot read the text clearly, describe the structure you can see

Format your response as:
Figure: [Title or Description]
[Visual structure with arrows and indentation]
Description:
[Explanation of what the diagram shows and its purpose]

Even if the image is unclear, provide your best interpretation of the structure.
"""
        
        self.prompt_formula = """
You are an expert in converting mathematical and structural equations from images into readable, properly formatted LaTeX or plain-text math expressions.

I will give you an image that may contain formulas, equations, or math-based visual structures.

Your task is to:
1. Accurately extract and interpret the equation(s) from the image.
2. Convert it into valid LaTeX inline math expressions (e.g., $...$) that can be used in markdown or LaTeX.
3. Ensure subscript, superscript, brackets, and operators are all correctly converted.
4. Preserve multi-line structures, indentations, and alignments when applicable.
5. Also provide a one-line explanation if the math expression represents a known concept (e.g., attention mechanism, layer norm, etc.)

Format your output like this:

```latex
Equation: [Title or concept]
$<LaTeX inline math expression>$
Description:
[A short explanation of what the equation represents.]
```
"""

    def convert_pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """Convert PDF pages to images with high DPI."""
        try:
            logger.info(f"Converting PDF to images: {pdf_path}")
            self.pdf_images = convert_from_path(pdf_path, dpi=200)
            logger.info(f"Successfully converted {len(self.pdf_images)} pages to images")
            return self.pdf_images
        except Exception as e:
            logger.error(f"Failed to convert PDF to images: {str(e)}")
            raise e

    def extract_and_enhance_image(self, element, element_idx: int) -> Optional[str]:
        """Extract image from PDF based on coordinates and enhance it."""
        try:
            if not hasattr(element.metadata, 'coordinates'):
                logger.warning(f"No coordinates found for image element {element_idx}")
                return None
                
            coords = element.metadata.coordinates
            page_num = (element.metadata.page_number or 1) - 1
            
            if page_num >= len(self.pdf_images):
                logger.warning(f"Page {page_num + 1} not found in PDF images")
                return None
                
            pdf_image = self.pdf_images[page_num]
            
            logger.info(f"Processing Image #{element_idx} on page {page_num + 1}")

            # Get bounding box from coordinates
            points = coords.points
            x_coords = [pt[0] for pt in points]
            y_coords = [pt[1] for pt in points]
            min_x, max_x = min(x_coords), max(x_coords)
            min_y, max_y = min(y_coords), max(y_coords)

            # Use coordinates directly with padding
            img_width, img_height = pdf_image.size
            padding = 10
            left = max(0, int(min_x) - padding)
            right = min(img_width, int(max_x) + padding)
            top = max(0, int(min_y) - padding)
            bottom = min(img_height, int(max_y) + padding)
            
            # Validate crop dimensions
            min_width, min_height = 50, 50
            if right > left and bottom > top and (right - left) > min_width and (bottom - top) > min_height:
                # Crop the image
                cropped_image = pdf_image.crop((left, top, right, bottom))
                
                # Enhance image quality
                enhancer = ImageEnhance.Sharpness(cropped_image)
                cropped_image = enhancer.enhance(2.0)
                
                enhancer = ImageEnhance.Contrast(cropped_image)
                cropped_image = enhancer.enhance(1.5)
                
                # Resize if too small
                if cropped_image.size[0] < 200 or cropped_image.size[1] < 200:
                    scale_factor = max(200 / cropped_image.size[0], 200 / cropped_image.size[1])
                    new_size = (int(cropped_image.size[0] * scale_factor), 
                               int(cropped_image.size[1] * scale_factor))
                    cropped_image = cropped_image.resize(new_size, Image.LANCZOS)
                
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                cropped_image.save(temp_file.name, dpi=(300, 300))
                temp_file.close()
                
                logger.info(f"✅ Successfully processed image {element_idx}")
                return temp_file.name
            else:
                logger.warning(f"❌ Invalid crop dimensions for image {element_idx}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error processing image {element_idx}: {e}")
            return None

    def encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """Encode image to base64 string."""
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {str(e)}")
            return None

    def generate_image_description(self, image_path: str) -> str:
        """Generate structured description from image using GPT-4o."""
        try:
            base64_image = self.encode_image_to_base64(image_path)
            if not base64_image:
                return "Image description: [Encoding failed]"
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at interpreting technical diagrams and flowcharts. Even if an image is unclear, provide your best interpretation of the structure and content."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.prompt_image},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=3000,
                temperature=0.3,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate description for image {image_path}: {str(e)}")
            return "Image description: [Processing failed]"

    def generate_formula_description(self, image_path: str) -> str:
        """Generate structured description from formula image using GPT-4o."""
        try:
            base64_image = self.encode_image_to_base64(image_path)
            if not base64_image:
                return "Formula description: [Encoding failed]"
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You must interpret math and formula images and preserve exact LaTeX formatting, ensuring clarity and correctness."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.prompt_formula},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=3000,
                temperature=0.3,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate description for formula {image_path}: {str(e)}")
            return "Formula description: [Processing failed]"

    def cleanup_temp_file(self, file_path: str):
        """Delete temporary file."""
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup file {file_path}: {str(e)}")

    def process_pdf(self, pdf_path: str, process_images: bool = True, 
                   process_formulas: bool = True, process_tables: bool = True,
                   progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """Process PDF and extract all content with overall progress tracking."""
        
        if progress_callback:
            progress_callback("Converting PDF to images...", 10)
        
        # Convert PDF to images
        self.convert_pdf_to_images(pdf_path)
        
        if progress_callback:
            progress_callback("Extracting PDF elements...", 20)
        
        # Extract elements from PDF
        elements = partition_pdf(
            filename=pdf_path,
            strategy="hi_res",
            infer_table_structure=True,
            model_name="yolox"
        )
        
        if progress_callback:
            progress_callback("Processing elements...", 30)
        
        # Process elements sequentially
        extracted_content = []
        image_counter = 0
        total_elements = len(elements)
        
        for idx, element in enumerate(elements):
            element_type = type(element).__name__
            page_num = getattr(element.metadata, 'page_number', 1)
            
            # Update overall progress (30% to 90%)
            if progress_callback:
                progress = 30 + (idx / total_elements) * 60
                progress_callback(f"Processing elements...", progress)
            
            content_item = {
                "type": element_type,
                "page": page_num,
                "content": "",
                "metadata": {}
            }
            
            if element_type == "Title":
                content_item["content"] = element.text.strip()
                content_item["metadata"]["level"] = "title"
                
            elif element_type == "Table" and process_tables:
                content_item["content"] = element.metadata.text_as_html
                content_item["metadata"]["format"] = "html"
                
            elif element_type == "Image" and process_images:
                # Extract and process image
                temp_image_path = self.extract_and_enhance_image(element, image_counter)
                
                if temp_image_path:
                    description = self.generate_image_description(temp_image_path)
                    content_item["content"] = description
                    content_item["metadata"]["image_id"] = image_counter
                    
                    # Cleanup temporary file
                    self.cleanup_temp_file(temp_image_path)
                else:
                    content_item["content"] = "Image description: [Extraction failed]"
                    
                image_counter += 1
                
            elif element_type == "Formula" and process_formulas:
                # Extract and process formula
                temp_image_path = self.extract_and_enhance_image(element, image_counter)
                
                if temp_image_path:
                    description = self.generate_formula_description(temp_image_path)
                    content_item["content"] = description
                    content_item["metadata"]["formula_id"] = image_counter
                    
                    # Cleanup temporary file
                    self.cleanup_temp_file(temp_image_path)
                else:
                    content_item["content"] = "Formula description: [Extraction failed]"
                    
                image_counter += 1
                
            else:
                # Regular text content
                content_item["content"] = element.text.strip() if hasattr(element, 'text') else ""
            
            # Only add non-empty content
            if content_item["content"].strip():
                extracted_content.append(content_item)
        
        if progress_callback:
            progress_callback("Finalizing results...", 100)
        
        logger.info(f"Successfully processed {len(extracted_content)} content items")
        return extracted_content