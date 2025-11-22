"""
OCR Service for extracting medical features from images and PDFs using EasyOCR.
"""

import re
import easyocr
from typing import Dict, Optional, List
from pathlib import Path
import tempfile
from pdf2image import convert_from_path
from PIL import Image
import io
import numpy as np

# Fix for Pillow 10.0.0+ compatibility - ANTIALIAS was removed
try:
    from PIL.Image import LANCZOS
except ImportError:
    from PIL.Image import ANTIALIAS as LANCZOS

# Patch Image.ANTIALIAS for pdf2image compatibility
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

# Feature names in order (24 features)
FEATURE_NAMES = [
    'Glucose',
    'Cholesterol',
    'Hemoglobin',
    'Platelets',
    'White Blood Cells',
    'Red Blood Cells',
    'Hematocrit',
    'Mean Corpuscular Volume',
    'Mean Corpuscular Hemoglobin',
    'Mean Corpuscular Hemoglobin Concentration',
    'Insulin',
    'BMI',
    'Systolic Blood Pressure',
    'Diastolic Blood Pressure',
    'Triglycerides',
    'HbA1c',
    'LDL Cholesterol',
    'HDL Cholesterol',
    'ALT',
    'AST',
    'Heart Rate',
    'Creatinine',
    'Troponin',
    'C-reactive Protein',
]

# Feature name variations for matching
FEATURE_VARIATIONS = {
    'Glucose': ['glucose', 'glu', 'blood glucose', 'sugar'],
    'Cholesterol': ['cholesterol', 'chol', 'total cholesterol'],
    'Hemoglobin': ['hemoglobin', 'hgb', 'hb', 'hgb a1c'],
    'Platelets': ['platelets', 'plt', 'platelet count'],
    'White Blood Cells': ['white blood cells', 'wbc', 'leukocytes', 'white cell count'],
    'Red Blood Cells': ['red blood cells', 'rbc', 'erythrocytes', 'red cell count'],
    'Hematocrit': ['hematocrit', 'hct', 'pcv', 'packed cell volume'],
    'Mean Corpuscular Volume': ['mean corpuscular volume', 'mcv', 'mean cell volume'],
    'Mean Corpuscular Hemoglobin': ['mean corpuscular hemoglobin', 'mch', 'mean cell hemoglobin'],
    'Mean Corpuscular Hemoglobin Concentration': ['mean corpuscular hemoglobin concentration', 'mchc', 'mean cell hb concentration'],
    'Insulin': ['insulin', 'ins'],
    'BMI': ['bmi', 'body mass index'],
    'Systolic Blood Pressure': ['systolic blood pressure', 'systolic', 'sbp', 'systolic bp'],
    'Diastolic Blood Pressure': ['diastolic blood pressure', 'diastolic', 'dbp', 'diastolic bp'],
    'Triglycerides': ['triglycerides', 'trig', 'tg'],
    'HbA1c': ['hba1c', 'hba1c', 'hemoglobin a1c', 'glycated hemoglobin'],
    'LDL Cholesterol': ['ldl cholesterol', 'ldl', 'low density lipoprotein'],
    'HDL Cholesterol': ['hdl cholesterol', 'hdl', 'high density lipoprotein'],
    'ALT': ['alt', 'alanine aminotransferase', 'sgpt'],
    'AST': ['ast', 'aspartate aminotransferase', 'sgot'],
    'Heart Rate': ['heart rate', 'hr', 'pulse', 'pulse rate'],
    'Creatinine': ['creatinine', 'creat', 'cre'],
    'Troponin': ['troponin', 'trop'],
    'C-reactive Protein': ['c-reactive protein', 'crp', 'c reactive protein', 'hs-crp'],
}


class OCRService:
    """Service for OCR extraction and feature parsing from medical documents."""
    
    def __init__(self):
        """Initialize EasyOCR reader."""
        # Initialize EasyOCR (English only for now)
        self.reader = easyocr.Reader(['en'], gpu=False)
    
    def extract_text_from_image(self, image_bytes: bytes) -> str:
        """
        Extract text from image bytes.
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            Extracted text as string
        """
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert PIL Image to numpy array for EasyOCR
        image_array = np.array(image)
        
        # Perform OCR
        results = self.reader.readtext(image_array)
        
        # Combine all text
        text = ' '.join([result[1] for result in results])
        
        return text
    
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF bytes.
        
        Args:
            pdf_bytes: PDF file bytes
            
        Returns:
            Extracted text as string
        """
        # Save PDF to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_path = tmp_file.name
        
        try:
            # Convert PDF pages to images
            images = convert_from_path(tmp_path, dpi=200)
            
            # Extract text from each page
            all_text = []
            for image in images:
                # Convert PIL Image to numpy array for EasyOCR
                image_array = np.array(image)
                
                # Perform OCR
                results = self.reader.readtext(image_array)
                page_text = ' '.join([result[1] for result in results])
                all_text.append(page_text)
            
            return ' '.join(all_text)
        finally:
            # Clean up temporary file
            Path(tmp_path).unlink(missing_ok=True)
    
    def parse_features_from_text(self, text: str) -> Dict[str, Optional[float]]:
        """
        Parse 24 feature values from extracted text.
        
        Args:
            text: Extracted text from OCR
            
        Returns:
            Dictionary mapping feature names to values (None if not found)
        """
        text_lower = text.lower()
        features = {}
        
        for feature_name in FEATURE_NAMES:
            features[feature_name] = None
            
            # Try all variations of the feature name
            variations = FEATURE_VARIATIONS.get(feature_name, [feature_name.lower()])
            
            for variation in variations:
                # Pattern 1: "Feature: value unit" or "Feature value unit"
                pattern1 = rf'{re.escape(variation)}\s*[:=]?\s*(\d+\.?\d*)\s*(?:mg/dl|mg/dL|g/dl|g/dL|%|bpm|/μl|/ul|million|cells)?'
                match1 = re.search(pattern1, text_lower, re.IGNORECASE)
                
                if match1:
                    try:
                        value = float(match1.group(1))
                        features[feature_name] = value
                        break
                    except (ValueError, IndexError):
                        continue
                
                # Pattern 2: "Feature value" (standalone number)
                pattern2 = rf'{re.escape(variation)}\s+(\d+\.?\d*)'
                match2 = re.search(pattern2, text_lower, re.IGNORECASE)
                
                if match2:
                    try:
                        value = float(match2.group(1))
                        features[feature_name] = value
                        break
                    except (ValueError, IndexError):
                        continue
        
        return features
    
    def extract_features_from_image(self, image_bytes: bytes) -> Dict[str, Optional[float]]:
        """
        Extract features from image.
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            Dictionary of extracted features
        """
        text = self.extract_text_from_image(image_bytes)
        return self.parse_features_from_text(text)
    
    def extract_features_from_pdf(self, pdf_bytes: bytes) -> Dict[str, Optional[float]]:
        """
        Extract features from PDF.
        
        Args:
            pdf_bytes: PDF file bytes
            
        Returns:
            Dictionary of extracted features
        """
        text = self.extract_text_from_pdf(pdf_bytes)
        return self.parse_features_from_text(text)


# Global instance
ocr_service = OCRService()

