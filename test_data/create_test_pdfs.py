#!/usr/bin/env python3
"""
Script to create test PDF files with medical data for testing the prediction system.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def create_medical_pdf(filename, title, patient_name, date, report_id, lab_data, highlight_rows=None):
    """Create a medical laboratory report PDF."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Title
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Patient Info
    patient_data = [
        ['Patient Name:', patient_name],
        ['Date:', date],
        ['Report ID:', report_id]
    ]
    patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Lab Results Table
    lab_table = Table(lab_data, colWidths=[2.5*inch, 1*inch, 1*inch, 2*inch])
    
    # Table style
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
    ]
    
    # Highlight abnormal values
    if highlight_rows:
        for row in highlight_rows:
            table_style.append(('BACKGROUND', (0, row), (-1, row), colors.HexColor('#fed7d7')))
    
    lab_table.setStyle(TableStyle(table_style))
    elements.append(lab_table)
    
    doc.build(elements)
    print(f'✓ Created {filename}')

# Anemia test case - Low Hemoglobin, Hematocrit, RBC
anemia_data = [
    ['Test Parameter', 'Value', 'Unit', 'Normal Range'],
    ['Glucose', '95', 'mg/dL', '70-100'],
    ['Cholesterol', '180', 'mg/dL', '<200'],
    ['Hemoglobin', '8.5', 'g/dL', '12-16'],
    ['Platelets', '150000', 'cells/μL', '150000-450000'],
    ['White Blood Cells', '4500', 'cells/μL', '4000-11000'],
    ['Red Blood Cells', '3.2', 'million/μL', '4.5-5.5'],
    ['Hematocrit', '28', '%', '36-48'],
    ['Mean Corpuscular Volume', '82', 'fL', '80-100'],
    ['Mean Corpuscular Hemoglobin', '24', 'pg', '27-31'],
    ['Mean Corpuscular Hemoglobin Concentration', '30', 'g/dL', '32-36'],
    ['Insulin', '8', 'μIU/mL', '2-25'],
    ['BMI', '22', 'kg/m²', '18.5-24.9'],
    ['Systolic Blood Pressure', '120', 'mmHg', '<120'],
    ['Diastolic Blood Pressure', '80', 'mmHg', '<80'],
    ['Triglycerides', '120', 'mg/dL', '<150'],
    ['HbA1c', '5.2', '%', '<5.7'],
    ['LDL Cholesterol', '100', 'mg/dL', '<100'],
    ['HDL Cholesterol', '45', 'mg/dL', '>40'],
    ['ALT', '25', 'U/L', '<40'],
    ['AST', '28', 'U/L', '<40'],
    ['Heart Rate', '72', 'bpm', '60-100'],
    ['Creatinine', '0.8', 'mg/dL', '0.6-1.2'],
    ['Troponin', '0.01', 'ng/mL', '<0.04'],
    ['C-reactive Protein', '2.5', 'mg/L', '<3.0']
]

# Diabetes test case - High Glucose, HbA1c, Insulin
diabetes_data = [
    ['Test Parameter', 'Value', 'Unit', 'Normal Range'],
    ['Glucose', '220', 'mg/dL', '70-100'],
    ['Cholesterol', '250', 'mg/dL', '<200'],
    ['Hemoglobin', '14', 'g/dL', '12-16'],
    ['Platelets', '250000', 'cells/μL', '150000-450000'],
    ['White Blood Cells', '7500', 'cells/μL', '4000-11000'],
    ['Red Blood Cells', '4.8', 'million/μL', '4.5-5.5'],
    ['Hematocrit', '42', '%', '36-48'],
    ['Mean Corpuscular Volume', '90', 'fL', '80-100'],
    ['Mean Corpuscular Hemoglobin', '30', 'pg', '27-31'],
    ['Mean Corpuscular Hemoglobin Concentration', '33', 'g/dL', '32-36'],
    ['Insulin', '25', 'μIU/mL', '2-25'],
    ['BMI', '32', 'kg/m²', '18.5-24.9'],
    ['Systolic Blood Pressure', '145', 'mmHg', '<120'],
    ['Diastolic Blood Pressure', '95', 'mmHg', '<80'],
    ['Triglycerides', '280', 'mg/dL', '<150'],
    ['HbA1c', '9.5', '%', '<5.7'],
    ['LDL Cholesterol', '160', 'mg/dL', '<100'],
    ['HDL Cholesterol', '35', 'mg/dL', '>40'],
    ['ALT', '45', 'U/L', '<40'],
    ['AST', '40', 'U/L', '<40'],
    ['Heart Rate', '85', 'bpm', '60-100'],
    ['Creatinine', '1.1', 'mg/dL', '0.6-1.2'],
    ['Troponin', '0.02', 'ng/mL', '<0.04'],
    ['C-reactive Protein', '5.8', 'mg/L', '<3.0']
]

# Heart Disease test case - High BP, Cholesterol, Troponin
heart_disease_data = [
    ['Test Parameter', 'Value', 'Unit', 'Normal Range'],
    ['Glucose', '110', 'mg/dL', '70-100'],
    ['Cholesterol', '280', 'mg/dL', '<200'],
    ['Hemoglobin', '15', 'g/dL', '12-16'],
    ['Platelets', '300000', 'cells/μL', '150000-450000'],
    ['White Blood Cells', '8000', 'cells/μL', '4000-11000'],
    ['Red Blood Cells', '5.0', 'million/μL', '4.5-5.5'],
    ['Hematocrit', '45', '%', '36-48'],
    ['Mean Corpuscular Volume', '88', 'fL', '80-100'],
    ['Mean Corpuscular Hemoglobin', '29', 'pg', '27-31'],
    ['Mean Corpuscular Hemoglobin Concentration', '32', 'g/dL', '32-36'],
    ['Insulin', '12', 'μIU/mL', '2-25'],
    ['BMI', '28', 'kg/m²', '18.5-24.9'],
    ['Systolic Blood Pressure', '170', 'mmHg', '<120'],
    ['Diastolic Blood Pressure', '105', 'mmHg', '<80'],
    ['Triglycerides', '220', 'mg/dL', '<150'],
    ['HbA1c', '6.5', '%', '<5.7'],
    ['LDL Cholesterol', '180', 'mg/dL', '<100'],
    ['HDL Cholesterol', '38', 'mg/dL', '>40'],
    ['ALT', '30', 'U/L', '<40'],
    ['AST', '35', 'U/L', '<40'],
    ['Heart Rate', '95', 'bpm', '60-100'],
    ['Creatinine', '1.2', 'mg/dL', '0.6-1.2'],
    ['Troponin', '0.04', 'ng/mL', '<0.04'],
    ['C-reactive Protein', '8.5', 'mg/L', '<3.0']
]

if __name__ == '__main__':
    print('Creating test PDF files...\n')
    
    # Create Anemia PDF
    create_medical_pdf(
        'test_data_anemia.pdf',
        'MEDICAL LABORATORY REPORT',
        'Test Patient - Anemia Case',
        '2024-01-15',
        'LAB-2024-001',
        anemia_data,
        highlight_rows=[3, 6, 7]  # Hemoglobin, Red Blood Cells, Hematocrit
    )
    
    # Create Diabetes PDF
    create_medical_pdf(
        'test_data_diabetes.pdf',
        'MEDICAL LABORATORY REPORT',
        'Test Patient - Diabetes Case',
        '2024-01-15',
        'LAB-2024-002',
        diabetes_data,
        highlight_rows=[1, 11, 16]  # Glucose, Insulin, HbA1c
    )
    
    # Create Heart Disease PDF
    create_medical_pdf(
        'test_data_heart_disease.pdf',
        'MEDICAL LABORATORY REPORT',
        'Test Patient - Heart Disease Case',
        '2024-01-15',
        'LAB-2024-003',
        heart_disease_data,
        highlight_rows=[1, 13, 14, 22, 24]  # Cholesterol, BP, Troponin, CRP
    )
    
    print('\n✓ All test files created successfully!')
    print('\nTest files:')
    print('  - test_data_anemia.csv')
    print('  - test_data_diabetes.csv')
    print('  - test_data_heart_disease.csv')
    print('  - test_data_anemia.pdf')
    print('  - test_data_diabetes.pdf')
    print('  - test_data_heart_disease.pdf')

