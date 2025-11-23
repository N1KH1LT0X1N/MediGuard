"""
File Parser Service for extracting features from CSV and Excel files.
"""

import pandas as pd
from typing import Dict, Optional
import io

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

# Feature name variations for column matching
FEATURE_COLUMN_VARIATIONS = {
    'Glucose': ['glucose', 'glu', 'blood glucose', 'sugar'],
    'Cholesterol': ['cholesterol', 'chol', 'total cholesterol'],
    'Hemoglobin': ['hemoglobin', 'hgb', 'hb'],
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


class FileParserService:
    """Service for parsing CSV and Excel files to extract medical features."""
    
    def normalize_column_name(self, col_name: str) -> str:
        """
        Normalize column name for matching.
        
        Args:
            col_name: Original column name
            
        Returns:
            Normalized column name (lowercase, stripped, no special chars)
        """
        if pd.isna(col_name):
            return ""
        return str(col_name).lower().strip().replace('_', ' ').replace('-', ' ')
    
    def find_feature_column(self, df: pd.DataFrame, feature_name: str) -> Optional[str]:
        """
        Find column name in dataframe that matches a feature.
        
        Args:
            df: DataFrame to search
            feature_name: Feature name to find
            
        Returns:
            Column name if found, None otherwise
        """
        variations = FEATURE_COLUMN_VARIATIONS.get(feature_name, [feature_name.lower()])
        
        # Normalize all column names
        normalized_cols = {self.normalize_column_name(col): col for col in df.columns}
        
        for variation in variations:
            normalized_variation = self.normalize_column_name(variation)
            
            # Exact match
            if normalized_variation in normalized_cols:
                return normalized_cols[normalized_variation]
            
            # Partial match (contains)
            for norm_col, orig_col in normalized_cols.items():
                if normalized_variation in norm_col or norm_col in normalized_variation:
                    return orig_col
        
        return None
    
    def parse_csv(self, csv_bytes: bytes) -> Dict[str, Optional[float]]:
        """
        Parse CSV file and extract 24 features.
        
        Args:
            csv_bytes: CSV file bytes
            
        Returns:
            Dictionary of extracted features
        """
        try:
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                try:
                    df = pd.read_csv(io.BytesIO(csv_bytes), encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Could not decode CSV file")
            
            return self._extract_features_from_dataframe(df)
        except Exception as e:
            raise ValueError(f"Error parsing CSV: {str(e)}")
    
    def parse_excel(self, excel_bytes: bytes) -> Dict[str, Optional[float]]:
        """
        Parse Excel file and extract 24 features.
        
        Args:
            excel_bytes: Excel file bytes
            
        Returns:
            Dictionary of extracted features
        """
        try:
            # Read first sheet
            df = pd.read_excel(io.BytesIO(excel_bytes), engine='openpyxl', sheet_name=0)
            return self._extract_features_from_dataframe(df)
        except Exception as e:
            raise ValueError(f"Error parsing Excel file: {str(e)}")
    
    def _extract_features_from_dataframe(self, df: pd.DataFrame) -> Dict[str, Optional[float]]:
        """
        Extract features from a DataFrame.
        
        Args:
            df: DataFrame with medical data
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # If only one row, use that row
        if len(df) == 1:
            row = df.iloc[0]
        else:
            # Use first row (assuming single patient per file)
            row = df.iloc[0]
        
        for feature_name in FEATURE_NAMES:
            features[feature_name] = None
            
            # Find matching column
            col_name = self.find_feature_column(df, feature_name)
            
            if col_name and col_name in df.columns:
                try:
                    value = row[col_name]
                    # Handle NaN and None
                    if pd.notna(value):
                        features[feature_name] = float(value)
                except (ValueError, TypeError):
                    pass
        
        return features


# Global instance
file_parser_service = FileParserService()

