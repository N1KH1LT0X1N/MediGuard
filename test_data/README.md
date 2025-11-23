# Test Data Directory

This directory contains test files for the MediGuard AI project.

## Contents

### Test PDFs (for OCR testing)
- `test_data_diabetes.pdf` - Sample diabetes test report
- `test_data_heart_disease.pdf` - Sample heart disease test report
- `test_data_anemia.pdf` - Sample anemia test report

### Test CSVs (for file upload testing)
- `test_data_diabetes.csv` - Diabetes test data in CSV format
  - **Expected Prediction:** Diabetes
  - **Key Indicators:** High Glucose (220), High HbA1c (9.5%), High Insulin (25)
- `test_data_heart_disease.csv` - Heart disease test data in CSV format
  - **Expected Prediction:** Heart Disease
  - **Key Indicators:** High Cholesterol (280), High BP (170/105), Elevated Troponin (0.04)
- `test_data_anemia.csv` - Anemia test data in CSV format
  - **Expected Prediction:** Anemia
  - **Key Indicators:** Low Hemoglobin (8.5), Low RBC (3.2), Low Hematocrit (28)

### Training Data
- `cleaned_test.csv` - Cleaned test dataset (488 samples)
- `cleaned.csv` - Cleaned training dataset (63 samples)

### Scripts
- `create_test_pdfs.py` - Script to generate test PDF files from CSV data

## Usage

### Testing CSV Upload
1. Go to Predict Disease page
2. Select "Analyze using CSV/Excel"
3. Upload one of the test CSV files
4. Verify the prediction matches the expected disease

### Testing PDF Upload
1. Go to Predict Disease page
2. Select "Analyze using PDF"
3. Upload one of the test PDF files
4. OCR should extract values and make prediction

### Testing Manual Entry
You can manually enter values from any CSV file to test the manual entry form.

## Feature Order

The CSV files follow this exact order (24 features):
1. Glucose, 2. Cholesterol, 3. Hemoglobin, 4. Platelets, 5. White Blood Cells,
6. Red Blood Cells, 7. Hematocrit, 8. Mean Corpuscular Volume, 9. Mean Corpuscular Hemoglobin,
10. Mean Corpuscular Hemoglobin Concentration, 11. Insulin, 12. BMI,
13. Systolic Blood Pressure, 14. Diastolic Blood Pressure, 15. Triglycerides,
16. HbA1c, 17. LDL Cholesterol, 18. HDL Cholesterol, 19. ALT, 20. AST,
21. Heart Rate, 22. Creatinine, 23. Troponin, 24. C-reactive Protein

## Notes

- All test values are within acceptable ranges defined in frontend validation
- Values are designed to clearly indicate the specific disease
- PDF files are formatted to look like real medical reports
- Abnormal values are highlighted in red in the PDFs
- The PDFs are generated from the CSV files using `create_test_pdfs.py`

