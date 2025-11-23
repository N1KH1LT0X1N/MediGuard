# Test Files for MediGuard AI

This directory contains test CSV and PDF files with dummy medical data for testing the disease prediction system.

## Test Files

### CSV Files

1. **test_data_anemia.csv**
   - **Expected Prediction:** Anemia
   - **Key Indicators:**
     - Low Hemoglobin: 8.5 g/dL (normal: 12-16)
     - Low Red Blood Cells: 3.2 million/μL (normal: 4.5-5.5)
     - Low Hematocrit: 28% (normal: 36-48)
   - All 24 features included in correct order

2. **test_data_diabetes.csv**
   - **Expected Prediction:** Diabetes
   - **Key Indicators:**
     - High Glucose: 220 mg/dL (normal: 70-100)
     - High HbA1c: 9.5% (normal: <5.7)
     - High Insulin: 25 μIU/mL (normal: 2-25, upper limit)
     - High BMI: 32 kg/m² (normal: 18.5-24.9)
   - All 24 features included in correct order

3. **test_data_heart_disease.csv**
   - **Expected Prediction:** Heart Disease
   - **Key Indicators:**
     - High Cholesterol: 280 mg/dL (normal: <200)
     - High Systolic BP: 170 mmHg (normal: <120)
     - High Diastolic BP: 105 mmHg (normal: <80)
     - Elevated Troponin: 0.04 ng/mL (normal: <0.04)
     - High C-reactive Protein: 8.5 mg/L (normal: <3.0)
   - All 24 features included in correct order

### PDF Files

1. **test_data_anemia.pdf**
   - Formatted medical laboratory report
   - Contains same data as CSV
   - Highlighted abnormal values (Hemoglobin, RBC, Hematocrit)
   - Ready for OCR testing

2. **test_data_diabetes.pdf**
   - Formatted medical laboratory report
   - Contains same data as CSV
   - Highlighted abnormal values (Glucose, Insulin, HbA1c)
   - Ready for OCR testing

3. **test_data_heart_disease.pdf**
   - Formatted medical laboratory report
   - Contains same data as CSV
   - Highlighted abnormal values (Cholesterol, BP, Troponin, CRP)
   - Ready for OCR testing

## How to Use

### Testing CSV Upload

1. Go to the Predict Disease page
2. Select "Analyze using CSV/Excel"
3. Upload one of the CSV files
4. Click "Analyze Document"
5. Verify the prediction matches the expected disease
6. Check the LIME explanation shows the correct risk factors

### Testing PDF Upload

1. Go to the Predict Disease page
2. Select "Analyze using PDF"
3. Upload one of the PDF files
4. Click "Analyze Document"
5. The OCR should extract the values
6. Verify the prediction and explanation

### Testing Manual Entry

You can also manually enter the values from any CSV file to test the manual entry form.

## Feature Order

The CSV files follow this exact order (24 features):

1. Glucose
2. Cholesterol
3. Hemoglobin
4. Platelets
5. White Blood Cells
6. Red Blood Cells
7. Hematocrit
8. Mean Corpuscular Volume
9. Mean Corpuscular Hemoglobin
10. Mean Corpuscular Hemoglobin Concentration
11. Insulin
12. BMI
13. Systolic Blood Pressure
14. Diastolic Blood Pressure
15. Triglycerides
16. HbA1c
17. LDL Cholesterol
18. HDL Cholesterol
19. ALT
20. AST
21. Heart Rate
22. Creatinine
23. Troponin
24. C-reactive Protein

## Notes

- All values are within the acceptable ranges defined in the frontend validation
- Values are designed to clearly indicate the specific disease
- PDF files are formatted to look like real medical reports
- Abnormal values are highlighted in red in the PDFs for easy identification

