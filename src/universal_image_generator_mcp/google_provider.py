import os
import logging
import sys
from typing import Optional, List, Any, Tuple
import PIL.Image

from google import genai
from google.genai import types

from .base_provider import ImageProvider
from .utils import save_image

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class GoogleProvider(ImageProvider):
    """Google image generation provider supporting both Imagen and Gemini 2.0 Flash models."""
    
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        self.client = genai.Client(api_key=self.api_key)
        
        # Default model selection via environment variable
        self.default_model = os.environ.get("GOOGLE_MODEL", "gemini")  # "gemini" or "imagen"
    
    def get_name(self) -> str:
        return "google"
    
    def supports_generation(self) -> bool:
        return True
    
    def supports_transformation(self) -> bool:
        return True
    
    def _get_model_name(self, model_type: Optional[str] = None, for_generation: bool = True) -> str:
        """Get the appropriate model name based on model type and operation."""
        # For non-generation tasks (translation, filename generation), always use gemini-2.0-flash
        if not for_generation:
            return 'gemini-2.0-flash'
        
        # For generation tasks, use the specified or default model
        effective_model_type = model_type or self.default_model
        
        if effective_model_type.lower() == "imagen":
            return 'imagen-4.0-generate-preview-06-06'
        else:  # Default to gemini for generation
            return 'gemini-2.0-flash-preview-image-generation'
    
    async def _call_gemini(
        self, 
        contents: List[Any], 
        model: str = "gemini-2.0-flash",
        config: Optional[types.GenerateContentConfig] = None, 
        text_only: bool = False
    ) -> bytes | str:
        """Internal method to call Gemini API."""
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
            
            logger.info(f"Response received from Google API using model {model}")
            
            # Check if response has candidates
            if not response.candidates or not response.candidates[0] or not response.candidates[0].content:
                raise ValueError("No valid response received from Google API")
            
            # For text-only calls, extract just the text
            if text_only:
                if not response.candidates[0].content.parts or not response.candidates[0].content.parts[0]:
                    raise ValueError("No text content found in Google response")
                text_content = response.candidates[0].content.parts[0].text
                if text_content is None:
                    raise ValueError("Text content is None in Google response")
                return text_content.strip()
            
            # Return the image data
            if not response.candidates[0].content.parts:
                raise ValueError("No content parts found in Google response")
                
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None and part.inline_data.data is not None:
                    return part.inline_data.data
                
            raise ValueError("No image data found in Google response")

        except Exception as e:
            logger.error(f"Error calling Google API: {str(e)}")
            raise
    
    async def _call_imagen(self, prompt: str) -> bytes:
        """Internal method to call Imagen API."""
        try:
            logger.info(f"Generating image with Imagen for prompt: '{prompt}'...")
            
            response = self.client.models.generate_images(
                model='imagen-4.0-generate-preview-06-06',
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                )
            )
            
            if response.generated_images:
                # Convert PIL Image to bytes - follow the imagen4.md reference approach
                generated_image = response.generated_images[0]
                
                # Ensure the image attribute exists and is not None
                if hasattr(generated_image, 'image') and generated_image.image is not None:
                    # generated_image.image is a PIL Image object - convert to bytes
                    from io import BytesIO
                    import tempfile
                    import os
                    
                    # Save to temporary file first (following imagen4.md approach)
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                        temp_path = tmp_file.name
                    
                    try:
                        # Save using the same method as imagen4.md
                        generated_image.image.save(temp_path)
                        
                        # Read the file back as bytes
                        with open(temp_path, 'rb') as f:
                            image_bytes = f.read()
                        
                        logger.info(f"Image successfully generated with Imagen")
                        return image_bytes
                    finally:
                        # Clean up temporary file
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                else:
                    raise ValueError("Generated image does not have a valid image attribute")
            else:
                raise ValueError("Image generation failed. No images were returned from Imagen.")

        except Exception as e:
            logger.error(f"Error calling Imagen API: {str(e)}")
            raise
    
    async def generate_image(self, prompt: str, **kwargs) -> Tuple[bytes, str, Optional[str]]:
        """Generate image using Google models (Imagen or Gemini)."""
        model_type = kwargs.get('model_type', self.default_model)
        
        logger.info(f"Generating image with Google {model_type} model")
        
        if model_type.lower() == "imagen":
            # Use Imagen API
            response = await self._call_imagen(prompt)
        else:
            # Use Gemini API
            model = self._get_model_name(model_type, for_generation=True)
            response = await self._call_gemini(
                [prompt],
                model=model,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
        
        if not isinstance(response, bytes):
            raise ValueError("Expected bytes response from Google for image generation")
        
        # Generate filename and save image (include model type info)
        filename = await self.convert_prompt_to_filename(prompt, model_type)
        saved_path = await save_image(response, filename)
        
        # Google doesn't provide a remote URL, so return None
        return response, saved_path, None
    
    async def transform_image(self, image: PIL.Image.Image, prompt: str, **kwargs) -> Tuple[bytes, str, Optional[str]]:
        """Transform image using Google models."""
        model_type = kwargs.get('model_type', self.default_model)
        
        logger.info(f"Transforming image with Google {model_type} model")
        
        if model_type.lower() == "imagen":
            # Imagen doesn't support image transformation, fall back to Gemini
            logger.warning("Imagen doesn't support image transformation, using Gemini instead")
            model_type = "gemini"
        
        # Use Gemini API for transformation
        model = self._get_model_name(model_type, for_generation=True)
        response = await self._call_gemini(
            [prompt, image],
            model=model,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )
        
        if not isinstance(response, bytes):
            raise ValueError("Expected bytes response from Google for image transformation")
        
        # Generate filename and save image (include model type info)
        filename = await self.convert_prompt_to_filename(prompt, model_type)
        saved_path = await save_image(response, filename)
        
        # Google doesn't provide a remote URL, so return None
        return response, saved_path, None
    
    async def convert_prompt_to_filename(self, prompt: str, model_type: str) -> str:
        """Generate filename using Gemini, include model type for identification."""
        try:
            filename_prompt = f"""
            Based on this image description: "{prompt}"
            
            Generate a short, descriptive file name suitable for the requested image.
            The filename should:
            - Be concise (maximum 4 words)
            - Use underscores between words
            - Not include any file extension
            - Only return the filename, nothing else
            """
            
            # Always use Gemini for filename generation (good at text tasks)
            model = self._get_model_name("gemini", for_generation=False)
            response = await self._call_gemini([filename_prompt], model=model, text_only=True)
            
            if isinstance(response, str):
                # Include model type in filename for identification
                clean_filename = response.strip().replace(' ', '_')
                return f"{clean_filename}_{model_type}"
            else:
                raise ValueError("Expected string response from Google for filename generation")
                
        except Exception as e:
            logger.error(f"Error generating filename with Gemini: {str(e)}")
            # Fallback to simple filename with model type
            import uuid
            truncated_text = prompt[:12].strip().replace(' ', '_')
            return f"image_{truncated_text}_{model_type}_{str(uuid.uuid4())[:8]}" 