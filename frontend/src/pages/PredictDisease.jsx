import { useState, useRef, useEffect } from 'react';
import { predictDisease, uploadImage, uploadPDF, uploadCSV } from '../lib/api';
import ExplanationChart from '../components/ExplanationChart';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from 'recharts';

const PredictDisease = () => {
  const [uploadedFiles, setUploadedFiles] = useState({ png: null, pdf: null, csv: null });
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisText, setAnalysisText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentUploadType, setCurrentUploadType] = useState(null);
  const [isManualEntryOpen, setIsManualEntryOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('image'); // 'image', 'pdf', 'csv', 'manual'
  const [manualData, setManualData] = useState({
    glucose: '',
    cholesterol: '',
    hemoglobin: '',
    platelets: '',
    whiteBloodCells: '',
    redBloodCells: '',
    hematocrit: '',
    meanCorpuscularVolume: '',
    meanCorpuscularHemoglobin: '',
    meanCorpuscularHemoglobinConcentration: '',
    insulin: '',
    bmi: '',
    systolicBloodPressure: '',
    diastolicBloodPressure: '',
    triglycerides: '',
    hba1c: '',
    ldlCholesterol: '',
    hdlCholesterol: '',
    alt: '',
    ast: '',
    heartRate: '',
    creatinine: '',
    troponin: '',
    cReactiveProtein: ''
  });

  const [validationErrors, setValidationErrors] = useState({});
  const [predictionResult, setPredictionResult] = useState(null);
  const [error, setError] = useState(null);
  const resultsRef = useRef(null);
  const [missingFeaturesModal, setMissingFeaturesModal] = useState({
    isOpen: false,
    extractedFeatures: {},
    missingFeatureNames: [],
    missingFeatureData: {}
  });

  const medicalFields = [
    { key: 'glucose', label: 'Glucose', unit: 'mg/dL', min: 39.09, max: 231.86 },
    { key: 'cholesterol', label: 'Cholesterol', unit: 'mg/dL', min: 52.73, max: 344.59 },
    { key: 'hemoglobin', label: 'Hemoglobin', unit: 'g/dL', min: 10.58, max: 19.45 },
    { key: 'platelets', label: 'Platelets', unit: 'cells/μL', min: 84000, max: 516000 },
    { key: 'whiteBloodCells', label: 'White Blood Cells', unit: 'cells/μL', min: 2350, max: 12651 },
    { key: 'redBloodCells', label: 'Red Blood Cells', unit: 'million cells/μL', min: 3.56, max: 6.44 },
    { key: 'hematocrit', label: 'Hematocrit', unit: '%', min: 32.23, max: 55.57 },
    { key: 'meanCorpuscularVolume', label: 'Mean Corpuscular Volume', unit: 'fL', min: 75.12, max: 104.49 },
    { key: 'meanCorpuscularHemoglobin', label: 'Mean Corpuscular Hemoglobin', unit: 'pg', min: 25.57, max: 34.42 },
    { key: 'meanCorpuscularHemoglobinConcentration', label: 'Mean Corpuscular Hemoglobin Concentration', unit: 'g/dL', min: 31.12, max: 36.88 },
    { key: 'insulin', label: 'Insulin', unit: 'μIU/mL', min: -3.47, max: 30.49 },
    { key: 'bmi', label: 'BMI', unit: 'kg/m²', min: 9.40, max: 46.04 },
    { key: 'systolicBloodPressure', label: 'Systolic Blood Pressure', unit: 'mmHg', min: 69.85, max: 201.77 },
    { key: 'diastolicBloodPressure', label: 'Diastolic Blood Pressure', unit: 'mmHg', min: 51.09, max: 109.41 },
    { key: 'triglycerides', label: 'Triglycerides', unit: 'mg/dL', min: -55.76, max: 605.71 },
    { key: 'hba1c', label: 'HbA1c', unit: '%', min: 2.10, max: 13.79 },
    { key: 'ldlCholesterol', label: 'LDL Cholesterol', unit: 'mg/dL', min: 14.43, max: 236.67 },
    { key: 'hdlCholesterol', label: 'HDL Cholesterol', unit: 'mg/dL', min: 18.13, max: 91.16 },
    { key: 'alt', label: 'ALT', unit: 'U/L', min: -4.94, max: 68.35 },
    { key: 'ast', label: 'AST', unit: 'U/L', min: 2.73, max: 47.17 },
    { key: 'heartRate', label: 'Heart Rate', unit: 'bpm', min: 38.12, max: 111.89 },
    { key: 'creatinine', label: 'Creatinine', unit: 'mg/dL', min: 0.43, max: 1.47 },
    { key: 'troponin', label: 'Troponin', unit: 'ng/mL', min: 0.00, max: 0.05 },
    { key: 'cReactiveProtein', label: 'C-reactive Protein', unit: 'mg/L', min: -1.12, max: 12.33 }
  ];

  const isAllFieldsFilled = () => {
    return Object.values(manualData).every(value => value.trim() !== '');
  };

  const isAllFieldsValid = () => {
    return isAllFieldsFilled() && Object.keys(validationErrors).length === 0;
  };

  const validateField = (key, value, field) => {
    if (value === '') {
      return null; // Don't validate empty fields
    }

    const numValue = parseFloat(value);
    if (isNaN(numValue)) {
      return 'Please enter a valid number';
    }

    if (numValue < field.min || numValue > field.max) {
      return `Value must be between ${field.min} and ${field.max}`;
    }

    return null;
  };

  const handleManualDataChange = (key, value) => {
    setManualData({ ...manualData, [key]: value });

    // Find the field configuration
    const field = medicalFields.find(f => f.key === key);
    if (!field) return;

    // Validate the field
    const error = validateField(key, value, field);
    
    // Update validation errors
    setValidationErrors(prevErrors => {
      const newErrors = { ...prevErrors };
      if (error) {
        newErrors[key] = error;
      } else {
        delete newErrors[key];
      }
      return newErrors;
    });
  };

  const handleMissingFeatureChange = (featureName, value) => {
    setMissingFeaturesModal(prev => ({
      ...prev,
      missingFeatureData: {
        ...prev.missingFeatureData,
        [featureName]: value
      }
    }));

    // No validation for missing features - allow any value
    // Clear any existing errors for this field
    setValidationErrors(prevErrors => {
      const newErrors = { ...prevErrors };
      const errorKey = `missing_${featureName}`;
      delete newErrors[errorKey];
      return newErrors;
    });
  };

  const handleCompleteMissingFeatures = async () => {
    // Only check if fields are filled (no range validation)
    const missingErrors = {};
    missingFeaturesModal.missingFeatureNames.forEach(featureName => {
      const value = missingFeaturesModal.missingFeatureData[featureName];
      
      if (!value || value.trim() === '') {
        missingErrors[`missing_${featureName}`] = 'This field is required';
        return;
      }
      
      // Check if it's a valid number
      const numValue = parseFloat(value);
      if (isNaN(numValue)) {
        missingErrors[`missing_${featureName}`] = 'Please enter a valid number';
        return;
      }
    });

    if (Object.keys(missingErrors).length > 0) {
      setValidationErrors(prev => ({ ...prev, ...missingErrors }));
      return;
    }

    // Combine extracted features with manually entered missing features
    const allFeatures = { ...missingFeaturesModal.extractedFeatures };
    missingFeaturesModal.missingFeatureNames.forEach(featureName => {
      const value = missingFeaturesModal.missingFeatureData[featureName];
      if (value && value.trim() !== '') {
        allFeatures[featureName] = parseFloat(value);
      }
    });

    // Close modal and proceed with prediction
    setMissingFeaturesModal({ isOpen: false, extractedFeatures: {}, missingFeatureNames: [], missingFeatureData: {} });
    setIsAnalyzing(true);
    setCurrentIndex(0);
    setAnalysisText(analysisSteps[0]);
    setError(null);
    setPredictionResult(null);

    // Animate through analysis steps
    let index = 0;
    const interval = setInterval(() => {
      if (index < analysisSteps.length - 1) {
        index++;
        setAnalysisText(analysisSteps[index]);
        setCurrentIndex(index);
      } else {
        clearInterval(interval);
      }
    }, 1500);

    try {
      const result = await predictDisease(allFeatures);
      clearInterval(interval);
      setPredictionResult(result);
      setIsAnalyzing(false);
      setAnalysisText('Analysis complete! Results ready.');
      
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 300);
    } catch (err) {
      clearInterval(interval);
      setError(err.message || 'An error occurred during prediction');
      setIsAnalyzing(false);
      setAnalysisText('');
    }
  };

  // Map manual data keys to API feature names
  const mapManualDataToFeatures = () => {
    const featureMap = {
      'glucose': 'Glucose',
      'cholesterol': 'Cholesterol',
      'hemoglobin': 'Hemoglobin',
      'platelets': 'Platelets',
      'whiteBloodCells': 'White Blood Cells',
      'redBloodCells': 'Red Blood Cells',
      'hematocrit': 'Hematocrit',
      'meanCorpuscularVolume': 'Mean Corpuscular Volume',
      'meanCorpuscularHemoglobin': 'Mean Corpuscular Hemoglobin',
      'meanCorpuscularHemoglobinConcentration': 'Mean Corpuscular Hemoglobin Concentration',
      'insulin': 'Insulin',
      'bmi': 'BMI',
      'systolicBloodPressure': 'Systolic Blood Pressure',
      'diastolicBloodPressure': 'Diastolic Blood Pressure',
      'triglycerides': 'Triglycerides',
      'hba1c': 'HbA1c',
      'ldlCholesterol': 'LDL Cholesterol',
      'hdlCholesterol': 'HDL Cholesterol',
      'alt': 'ALT',
      'ast': 'AST',
      'heartRate': 'Heart Rate',
      'creatinine': 'Creatinine',
      'troponin': 'Troponin',
      'cReactiveProtein': 'C-reactive Protein'
    };

    const features = {};
    Object.entries(manualData).forEach(([key, value]) => {
      const featureName = featureMap[key];
      if (featureName) {
        features[featureName] = parseFloat(value);
      }
    });
    return features;
  };

  const handleManualAnalyze = async (e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    
    if (!isAllFieldsValid()) {
      alert('Please fill in all fields with valid values before analyzing');
      return;
    }

    setIsAnalyzing(true);
    setCurrentIndex(0);
    setAnalysisText(analysisSteps[0]);
    setError(null);
    setPredictionResult(null);
    
    // Animate through analysis steps
    let index = 0;
    const interval = setInterval(() => {
      if (index < analysisSteps.length - 1) {
        index++;
        setAnalysisText(analysisSteps[index]);
        setCurrentIndex(index);
      } else {
        clearInterval(interval);
      }
    }, 1500);

    try {
      // Map manual data to API format
      const features = mapManualDataToFeatures();
      
      // Call API
      const result = await predictDisease(features);
      
      // Clear interval and set results
      clearInterval(interval);
      setPredictionResult(result);
      setIsAnalyzing(false);
      setAnalysisText('Analysis complete! Results ready.');
      
      // Scroll to results after a brief delay
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 300);
    } catch (err) {
      clearInterval(interval);
      setError(err.message || 'An error occurred during prediction');
      setIsAnalyzing(false);
      setAnalysisText('');
    }
  };

  const analysisSteps = [
    "Predicting disease...",
    "Processing medical data...",
    "Extracting key health indicators...",
    "Cross-referencing with disease database...",
    "Evaluating symptoms and patterns...",
    "Calculating probability scores...",
    "Generating diagnostic insights...",
    "Finalizing disease prediction..."
  ];

  const handleFileInput = (e, type) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0], type);
    }
  };

  const simulateUpload = async (file, type) => {
    setIsUploading(true);
    setCurrentUploadType(type);
    setUploadProgress(0);
    setError(null);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Upload file
      let uploadResult;
      if (type === 'png') {
        uploadResult = await uploadImage(file);
      } else if (type === 'pdf') {
        uploadResult = await uploadPDF(file);
      } else if (type === 'csv') {
        uploadResult = await uploadCSV(file);
      }

      clearInterval(progressInterval);
      setUploadProgress(100);

      setTimeout(() => {
        setIsUploading(false);
        setUploadedFiles({ ...uploadedFiles, [type]: file });
        setCurrentUploadType(null);
        
        // Show extraction result
        if (uploadResult.extraction_success) {
          const extractedCount = Object.values(uploadResult.features || {}).filter(v => v !== null).length;
          alert(`Successfully extracted ${extractedCount} out of 24 features. Click "Analyze Document" to make a prediction.`);
        } else {
          alert(uploadResult.message || 'Feature extraction completed with warnings. Some features may be missing.');
        }
      }, 500);
    } catch (err) {
      setIsUploading(false);
      setError(err.message || 'File upload failed');
      setCurrentUploadType(null);
    }
  };

  const handleFile = (file, type) => {
    const validExtensions = {
      png: ['png', 'jpg', 'jpeg'],
      pdf: ['pdf'],
      csv: ['csv', 'xlsx', 'xls']
    };

    const fileExtension = file.name.split('.').pop().toLowerCase();
    
    if (validExtensions[type].includes(fileExtension)) {
      simulateUpload(file, type);
    } else {
      alert(`Please upload a valid ${type.toUpperCase()} file`);
    }
  };

  const handleAnalyze = async (type, e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    
    if (!uploadedFiles[type]) {
      alert('Please upload a file first');
      return;
    }

    setIsAnalyzing(true);
    setCurrentIndex(0);
    setAnalysisText(analysisSteps[0]);
    setError(null);
    setPredictionResult(null);
    
    // Animate through analysis steps
    let index = 0;
    const interval = setInterval(() => {
      if (index < analysisSteps.length - 1) {
        index++;
        setAnalysisText(analysisSteps[index]);
        setCurrentIndex(index);
      } else {
        clearInterval(interval);
      }
    }, 1500);

    try {
      let uploadResult;
      
      // Upload file and extract features
      if (type === 'png') {
        uploadResult = await uploadImage(uploadedFiles[type]);
      } else if (type === 'pdf') {
        uploadResult = await uploadPDF(uploadedFiles[type]);
      } else if (type === 'csv') {
        uploadResult = await uploadCSV(uploadedFiles[type]);
      }

      // Check if extraction was successful
      if (!uploadResult.extraction_success || !uploadResult.features) {
        throw new Error(uploadResult.message || 'Failed to extract features from file');
      }

      // Filter out null values and convert to proper format
      const features = {};
      Object.entries(uploadResult.features).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          features[key] = parseFloat(value);
        }
      });

      // Check for missing features
      const allFeatureNames = medicalFields.map(f => f.label);
      const missingFeatures = allFeatureNames.filter(name => !features[name] || features[name] === null);
      
      // If we have missing features, show modal for manual input
      if (missingFeatures.length > 0 && missingFeatures.length <= 24) {
        clearInterval(interval);
        setIsAnalyzing(false);
        setAnalysisText('');
        
        // Initialize missing feature data
        const missingData = {};
        missingFeatures.forEach(name => {
          missingData[name] = '';
        });
        
        setMissingFeaturesModal({
          isOpen: true,
          extractedFeatures: features,
          missingFeatureNames: missingFeatures,
          missingFeatureData: missingData
        });
        return; // Exit early, wait for user to fill missing features
      }

      // Check if we have enough features
      const featureCount = Object.keys(features).length;
      if (featureCount < 20) {
        throw new Error(`Only extracted ${featureCount} features. Please ensure the file contains all 24 required features or use manual entry.`);
      }

      // Make prediction
      const result = await predictDisease(features);
      
      // Clear interval and set results
      clearInterval(interval);
      setPredictionResult(result);
      setIsAnalyzing(false);
      setAnalysisText('Analysis complete! Results ready.');
      
      // Scroll to results after a brief delay
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 300);
    } catch (err) {
      clearInterval(interval);
      setError(err.message || 'An error occurred during analysis');
      setIsAnalyzing(false);
      setAnalysisText('');
    }
  };

  const FileUploadCard = ({ type, title, acceptedFormats }) => (
    <div className="w-full">
      <div className="bg-white rounded-xl shadow-lg border-2 border-black overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-gray-50 to-white px-6 py-4 border-b-2 border-black">
          <h3 className="text-lg font-semibold text-gray-900 tracking-tight">{title}</h3>
        </div>

        {/* Upload Area */}
        <div className="p-8">
          <div className="border-2 border-dashed rounded-lg p-16 text-center transition-all duration-200 border-gray-300 hover:border-black hover:bg-gray-50">
            {uploadedFiles[type] ? (
              <div className="space-y-3">
                <div className="text-black text-5xl">✓</div>
                <p className="text-sm font-medium text-gray-700 break-all px-2">
                  {uploadedFiles[type].name}
                </p>
                <p className="text-xs text-gray-500">
                  {(uploadedFiles[type].size / 1024).toFixed(2)} KB
                </p>
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setUploadedFiles({ ...uploadedFiles, [type]: null });
                  }}
                  className="text-xs text-red-600 hover:text-red-800 underline"
                >
                  Remove file
                </button>
              </div>
            ) : (
              <div>
                <svg 
                  className="mx-auto h-16 w-16 text-black mb-4" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" 
                  />
                </svg>
                <p className="text-sm font-medium text-gray-700 mb-3">
                  <label htmlFor={`file-upload-${type}`} className="cursor-pointer text-black hover:text-gray-800 font-semibold">
                    Click to upload
                  </label>
                </p>
                <input
                  id={`file-upload-${type}`}
                  type="file"
                  className="hidden"
                  accept={acceptedFormats}
                  onChange={(e) => handleFileInput(e, type)}
                />
                <p className="text-xs text-gray-500 mt-2">
                  {acceptedFormats.replace(/\./g, '').toUpperCase()} (max. 25MB)
                </p>
              </div>
            )}
          </div>

          {/* Analyze Button - Shows only when file is uploaded */}
          {uploadedFiles[type] && !isAnalyzing && (
            <button
              type="button"
              onClick={(e) => handleAnalyze(type, e)}
              className="w-full mt-4 px-6 py-3 rounded-lg font-bold text-base transition-all duration-200 bg-[#7FFF00] hover:bg-[#6ee000] text-black"
            >
              Analyze Document
            </button>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div 
      className="space-y-6 w-full font-sans"
      onKeyDown={(e) => {
        // Prevent any accidental form submissions
        if (e.key === 'Enter' && e.target.tagName !== 'BUTTON') {
          e.preventDefault();
        }
      }}
    >
      <div className="bg-white rounded-lg shadow p-6 w-full">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-gray-900 mb-4 tracking-tight">
            <span className="text-gray-900">Predict </span>
            <span style={{ color: '#7FFF00' }}>Intelligent</span>
            <span className="text-gray-900"> Diagnosis</span>
          </h1>
          <p className="text-gray-600 font-normal text-lg">Choose your preferred method to analyze and predict potential diseases</p>
        </div>
        
        {/* Category Selection Buttons */}
        <div className="flex gap-4 mb-8 flex-wrap justify-center">
          <button
            onClick={() => setSelectedCategory('image')}
            className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 ${
              selectedCategory === 'image'
                ? 'bg-gray-900 text-white shadow-lg'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Analyze using JPG/PNG
          </button>
          <button
            onClick={() => setSelectedCategory('pdf')}
            className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 ${
              selectedCategory === 'pdf'
                ? 'bg-gray-900 text-white shadow-lg'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Analyze using PDF
          </button>
          <button
            onClick={() => setSelectedCategory('csv')}
            className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 ${
              selectedCategory === 'csv'
                ? 'bg-gray-900 text-white shadow-lg'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Analyze using CSV/Excel
          </button>
          <button
            onClick={() => setSelectedCategory('manual')}
            className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 ${
              selectedCategory === 'manual'
                ? 'bg-gray-900 text-white shadow-lg'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Manually Enter Data
          </button>
        </div>

        {/* Conditional Rendering Based on Selected Category */}
        {selectedCategory === 'image' && (
          <div className="animate-fadeIn">
            <FileUploadCard
              type="png"
              title="Medical Images"
              acceptedFormats=".png,.jpg,.jpeg"
            />
          </div>
        )}

        {selectedCategory === 'pdf' && (
          <div className="animate-fadeIn">
            <FileUploadCard
              type="pdf"
              title="PDF Reports"
              acceptedFormats=".pdf"
            />
          </div>
        )}

        {selectedCategory === 'csv' && (
          <div className="animate-fadeIn">
            <FileUploadCard
              type="csv"
              title="Data Sheets"
              acceptedFormats=".csv,.xlsx,.xls"
            />
          </div>
        )}

        {selectedCategory === 'manual' && (
          <div className="animate-fadeIn">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                e.stopPropagation();
                if (isAllFieldsValid() && !isAnalyzing) {
                  handleManualAnalyze(e);
                }
              }}
              onKeyDown={(e) => {
                // Prevent Enter key from submitting form
                if (e.key === 'Enter') {
                  e.preventDefault();
                  e.stopPropagation();
                  if (isAllFieldsValid() && !isAnalyzing) {
                    handleManualAnalyze(e);
                  }
                }
              }}
            >
              <div className="bg-white rounded-lg border-2 border-black p-6">
                <div className="mb-6">
                  <h2 className="text-2xl font-semibold text-gray-900 tracking-tight mb-2">Enter Medical Parameters</h2>
                  <p className="text-sm text-gray-600 font-normal">Fill in all the required medical parameters to get disease prediction</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {medicalFields.map((field) => (
                    <div key={field.key} className="flex flex-col">
                      <label className="text-sm font-medium text-gray-900 mb-2">
                        {field.label}
                        <span className="text-red-600 ml-1">*</span>
                        {field.unit && <span className="text-gray-500 font-normal ml-1">({field.unit})</span>}
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={manualData[field.key]}
                        onChange={(e) => handleManualDataChange(field.key, e.target.value)}
                        onKeyDown={(e) => {
                          // Prevent Enter key from submitting
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            e.stopPropagation();
                          }
                        }}
                        placeholder={`Enter a value between ${field.min} to ${field.max}`}
                        className={`px-4 py-2 border-2 rounded-lg focus:outline-none transition-colors duration-200 ${
                          validationErrors[field.key]
                            ? 'border-red-500 focus:border-red-600'
                            : 'border-gray-300 focus:border-[#7FFF00]'
                        }`}
                        required
                      />
                      {validationErrors[field.key] && (
                        <span className="text-red-600 text-xs mt-1 font-medium">
                          {validationErrors[field.key]}
                        </span>
                      )}
                    </div>
                  ))}
                </div>

                {/* Analyze Button */}
                <div className="mt-8 flex justify-center">
                  <button
                    type="button"
                    onClick={handleManualAnalyze}
                    disabled={!isAllFieldsValid() || isAnalyzing}
                    className={`px-12 py-4 rounded-lg font-bold text-lg transition-all duration-200 ${
                      isAllFieldsValid() && !isAnalyzing
                        ? 'bg-[#7FFF00] hover:bg-[#6ee000] text-black cursor-pointer'
                        : 'bg-gray-400 text-gray-600 cursor-not-allowed'
                    }`}
                  >
                    {isAnalyzing ? 'Analyzing...' : 'Analyze Data'}
                  </button>
                </div>
              </div>
            </form>
          </div>
        )}
      </div>

      {/* Upload Progress Modal */}
      {isUploading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Uploading File...</h3>
            <div className="space-y-4">
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className="bg-[#7FFF00] h-4 rounded-full transition-all duration-300 flex items-center justify-center"
                  style={{ width: `${uploadProgress}%` }}
                >
                  <span className="text-xs font-bold text-black">{uploadProgress}%</span>
                </div>
              </div>
              <p className="text-sm text-gray-600 text-center">
                {uploadProgress < 100 ? 'Please wait...' : 'Upload complete!'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Output */}
      {isAnalyzing && (
        <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg shadow-lg p-6 border-l-4 border-[#7FFF00]">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="animate-spin rounded-full h-8 w-8 border-4 border-[#7FFF00] border-t-transparent"></div>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-bold text-gray-800 mb-2">Analyzing...</h3>
              <p className="text-[#2d8000] font-medium text-base">
                {analysisText}
              </p>
              <div className="mt-4 w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-[#7FFF00] h-2 rounded-full transition-all duration-500"
                  style={{ width: `${((currentIndex + 1) / analysisSteps.length) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 rounded-lg shadow-lg p-6">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="text-red-600 text-3xl">✗</div>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-bold text-red-800 mb-2">Error</h3>
              <p className="text-red-700 font-medium text-base">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results Display */}
      {predictionResult && !isAnalyzing && (
        <div ref={resultsRef} className="space-y-6 mt-8 animate-fadeIn">
          {/* Prediction Card */}
          <div className="bg-white rounded-xl shadow-2xl border-2 border-black p-8 transform transition-all duration-500 hover:shadow-3xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-4xl font-bold text-gray-900 tracking-tight">Prediction Results</h2>
              <div className="w-16 h-1 bg-gradient-to-r from-[#7FFF00] to-[#6ee000] rounded-full"></div>
            </div>
            
            {/* Main Prediction Display */}
            <div className="bg-gradient-to-br from-[#7FFF00] via-[#6ee000] to-[#5dd000] rounded-xl p-8 mb-8 shadow-lg transform transition-all duration-300 hover:scale-[1.02]">
              <p className="text-sm font-semibold text-gray-800 mb-3 uppercase tracking-wide">Predicted Disease</p>
              <p className="text-5xl font-extrabold text-gray-900 drop-shadow-lg">{predictionResult.predicted_disease}</p>
              <div className="mt-4 flex items-center space-x-2">
                <div className="w-3 h-3 bg-gray-900 rounded-full animate-pulse"></div>
                <p className="text-sm font-medium text-gray-800">AI-Powered Diagnosis</p>
              </div>
            </div>

            {/* Textual LIME Explanation - Minimal Design */}
            {predictionResult.explainability_json && Object.keys(predictionResult.explainability_json).length > 0 && (
              <div className="mb-8 bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
                <div className="mb-6">
                  <h3 className="text-2xl font-bold text-[#222123] tracking-tight mb-1">Why {predictionResult.predicted_disease}?</h3>
                  <p className="text-sm text-gray-500">Key factors from your test results</p>
                </div>

                <div className="space-y-4">
                  {(() => {
                    // Get actual raw input values (not scaled)
                    const rawInputFeatures = predictionResult.input_features || {};
                    
                    // Sort features by absolute importance
                    const sortedFeatures = Object.entries(predictionResult.explainability_json || {})
                      .map(([name, importance]) => {
                        const field = medicalFields.find(f => f.label === name);
                        const rawValue = rawInputFeatures[name];
                        let actualValue = null;
                        
                        // Try to get the actual raw value
                        if (rawValue !== undefined && rawValue !== null) {
                          actualValue = parseFloat(rawValue);
                        }
                        
                        return {
                          name,
                          importance: parseFloat(importance),
                          absImportance: Math.abs(parseFloat(importance)),
                          rawValue: actualValue,
                          field: field
                        };
                      })
                      .filter(f => f.rawValue !== null && !isNaN(f.rawValue)) // Only include features with valid values
                      .sort((a, b) => b.absImportance - a.absImportance)
                      .slice(0, 10); // Top 10 features

                    // Determine if predicted disease is one where low values indicate the disease
                    const lowValueDiseases = ['Anemia', 'Thalassemia', 'Thrombocytopenia'];
                    const isLowValueDisease = lowValueDiseases.includes(predictionResult.predicted_disease);
                    
                    // Analyze each feature to determine if it supports the prediction
                    const analyzedFeatures = sortedFeatures.map(feature => {
                      const { name, importance, rawValue, field } = feature;
                      
                      if (!field) {
                        return { ...feature, isRiskFactor: false, explanation: 'Unknown feature' };
                      }
                      
                      const isBelowNormal = rawValue < field.min;
                      const isAboveNormal = rawValue > field.max;
                      const isInNormalRange = !isBelowNormal && !isAboveNormal;
                      const rangeMidpoint = (field.min + field.max) / 2;
                      const isLowInRange = isInNormalRange && rawValue < rangeMidpoint;
                      const isHighInRange = isInNormalRange && rawValue > rangeMidpoint;
                      
                      let explanation = '';
                      let isRiskFactor = false;
                      let interpretationColor = 'blue';
                      
                      // Determine if this feature is a risk factor based on LIME contribution
                      // For diseases like Anemia: negative LIME contribution with low/normal-low values = risk
                      // For other diseases: positive LIME contribution with high/abnormal values = risk
                      
                      if (isLowValueDisease) {
                        // For Anemia/Thalassemia/Thrombocytopenia: low values are key indicators
                        // Only show as risk factor if:
                        // 1. Value is actually below normal (abnormal), OR
                        // 2. Value is low in range AND has strong negative LIME contribution (indicating low value matters)
                        
                        // Key features for Anemia: Hemoglobin, Hematocrit, Red Blood Cells
                        const isKeyAnemiaFeature = ['Hemoglobin', 'Hematocrit', 'Red Blood Cells'].includes(name);
                        
                        if (importance < 0 && isBelowNormal) {
                          // Negative contribution + below normal = clear risk factor
                          explanation = `Low ${name} (${rawValue.toFixed(2)} ${field.unit}) is below normal range (${field.min.toFixed(2)}-${field.max.toFixed(2)} ${field.unit}). This abnormally low value is a key indicator of ${predictionResult.predicted_disease}.`;
                          isRiskFactor = true;
                          interpretationColor = 'red';
                        } else if (importance < 0 && isLowInRange && isKeyAnemiaFeature && Math.abs(importance) > 0.05) {
                          // For key anemia features, even low-normal values with strong negative contribution matter
                          explanation = `${name} (${rawValue.toFixed(2)} ${field.unit}) is in the lower end of normal range (${field.min.toFixed(2)}-${field.max.toFixed(2)} ${field.unit}). This lower value, combined with other factors, contributes to the ${predictionResult.predicted_disease} diagnosis.`;
                          isRiskFactor = true;
                          interpretationColor = 'red';
                        } else if (importance > 0 && (isAboveNormal || isHighInRange)) {
                          // Positive contribution + high value = elevated value contributes
                          if (isAboveNormal) {
                            explanation = `Elevated ${name} (${rawValue.toFixed(2)} ${field.unit}) exceeds normal range (${field.min.toFixed(2)}-${field.max.toFixed(2)} ${field.unit}) and contributes to ${predictionResult.predicted_disease} prediction.`;
                          } else {
                            explanation = `${name} (${rawValue.toFixed(2)} ${field.unit}) is in the higher end of normal range and contributes to the prediction.`;
                          }
                          isRiskFactor = true;
                          interpretationColor = 'red';
                        } else if (Math.abs(importance) < 0.01) {
                          // Very small contribution = not significant
                          explanation = `${name} value is within normal range and has minimal impact on this prediction.`;
                          interpretationColor = 'gray';
                        } else {
                          // Normal values that reduce likelihood of other conditions (not shown as risk factors)
                          explanation = `Normal ${name} value helps rule out other conditions.`;
                          interpretationColor = 'gray';
                        }
                      } else {
                        // For other diseases (Diabetes, Heart Disease, etc.)
                        if (importance > 0) {
                          // Positive contribution = increases risk
                          if (isAboveNormal) {
                            explanation = `High ${name} (${rawValue.toFixed(2)} ${field.unit}) exceeds normal range (${field.min.toFixed(2)}-${field.max.toFixed(2)} ${field.unit}). This elevated value significantly increases the risk of ${predictionResult.predicted_disease}.`;
                          } else if (isHighInRange) {
                            explanation = `${name} (${rawValue.toFixed(2)} ${field.unit}) is in the higher end of normal range (${field.min.toFixed(2)}-${field.max.toFixed(2)} ${field.unit}). This elevated value contributes to ${predictionResult.predicted_disease} risk.`;
                          } else {
                            explanation = `${name} (${rawValue.toFixed(2)} ${field.unit}) contributes to ${predictionResult.predicted_disease} prediction based on the model's analysis.`;
                          }
                          isRiskFactor = true;
                          interpretationColor = 'red';
                        } else if (importance < 0 && isInNormalRange) {
                          // Negative contribution + normal = protective
                          explanation = `Normal ${name} value helps reduce risk of ${predictionResult.predicted_disease}.`;
                          interpretationColor = 'green';
                        } else {
                          // Small or neutral contribution
                          explanation = `${name} value is within normal range.`;
                          interpretationColor = 'gray';
                        }
                      }
                      
                      return {
                        ...feature,
                        isRiskFactor,
                        explanation,
                        interpretationColor,
                        isBelowNormal,
                        isAboveNormal,
                        isInNormalRange
                      };
                    });
                    
                    // Filter to only show actual risk factors (abnormal values or significant contributions)
                    const actualRiskFactors = analyzedFeatures.filter(f => {
                      if (!f.isRiskFactor) return false;
                      // Only show if value is actually abnormal OR has very strong LIME contribution
                      return f.isBelowNormal || f.isAboveNormal || Math.abs(f.importance) > 0.1;
                    }).slice(0, 5); // Limit to top 5
                    
                    return (
                      <>
                        {/* Key Factors - Simple Human-Readable Explanations with Colored Terms */}
                        {actualRiskFactors.length > 0 && (
                          <div className="space-y-3">
                            {actualRiskFactors.map((feature) => {
                              // Determine color scheme based on status
                              let valueColor = 'text-[#222123]'; // Default black
                              let statusColor = 'text-gray-600';
                              let diseaseColor = 'text-red-600';
                              
                              if (feature.isBelowNormal) {
                                valueColor = 'text-red-600';
                                statusColor = 'text-red-600';
                              } else if (feature.isAboveNormal) {
                                valueColor = 'text-orange-600';
                                statusColor = 'text-orange-600';
                              } else {
                                valueColor = 'text-blue-600';
                                statusColor = 'text-blue-600';
                              }
                              
                              return (
                                <div key={feature.name} className="p-4 rounded-lg border-2 border-[#222123] bg-white transition-all hover:shadow-sm">
                                  <p className="text-gray-800 leading-relaxed">
                                    Your <span className="font-bold text-[#222123]">{feature.name}</span> is{' '}
                                    <span className={`font-bold ${valueColor}`}>
                                      {feature.rawValue.toFixed(1)} {feature.field.unit}
                                    </span>
                                    {feature.isBelowNormal ? (
                                      <>
                                        , which is <span className={`font-semibold ${statusColor}`}>below the normal range</span> of{' '}
                                        <span className="text-gray-600">
                                          {feature.field.min.toFixed(1)}-{feature.field.max.toFixed(1)} {feature.field.unit}
                                        </span>
                                        . This <span className={`font-semibold ${statusColor}`}>low value</span> indicates{' '}
                                        <span className={`font-bold ${diseaseColor}`}>{predictionResult.predicted_disease}</span>.
                                      </>
                                    ) : feature.isAboveNormal ? (
                                      <>
                                        , which is <span className={`font-semibold ${statusColor}`}>above the normal range</span> of{' '}
                                        <span className="text-gray-600">
                                          {feature.field.min.toFixed(1)}-{feature.field.max.toFixed(1)} {feature.field.unit}
                                        </span>
                                        . This <span className={`font-semibold ${statusColor}`}>high value</span> increases your risk of{' '}
                                        <span className={`font-bold ${diseaseColor}`}>{predictionResult.predicted_disease}</span>.
                                      </>
                                    ) : (
                                      <>
                                        {(() => {
                                          const isHighInRange = feature.rawValue > (feature.field.min + feature.field.max) / 2;
                                          return (
                                            <>
                                              , which is in the <span className={`font-semibold ${statusColor}`}>
                                                {isHighInRange ? 'higher' : 'lower'} end of the normal range
                                              </span>
                                              . This contributes to{' '}
                                              <span className={`font-bold ${diseaseColor}`}>{predictionResult.predicted_disease}</span> risk.
                                            </>
                                          );
                                        })()}
                                      </>
                                    )}
                                  </p>
                                </div>
                              );
                            })}
                          </div>
                        )}
                      </>
                    );
                  })()}
                </div>
              </div>
            )}

            {/* Probability Chart */}
            <div className="mb-8 bg-gray-50 rounded-xl p-6 border-2 border-gray-200">
              <div className="mb-6">
                <h3 className="text-3xl font-bold text-gray-900 mb-2 tracking-tight">Disease Probabilities</h3>
                <p className="text-sm text-gray-600">Confidence scores for all possible diagnoses</p>
              </div>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={Object.entries(predictionResult.probabilities || {}).map(([name, value]) => ({
                  name: name.length > 15 ? name.substring(0, 15) + '...' : name,
                  probability: (value * 100).toFixed(2),
                  fullName: name
                })).sort((a, b) => parseFloat(b.probability) - parseFloat(a.probability))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="name" 
                    angle={-45}
                    textAnchor="end"
                    height={100}
                    tick={{ fill: '#523122', fontSize: 12 }}
                  />
                  <YAxis 
                    label={{ value: 'Probability (%)', angle: -90, position: 'insideLeft' }}
                    tick={{ fill: '#523122' }}
                  />
                  <Tooltip
                    formatter={(value) => [`${value}%`, 'Probability']}
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '2px solid #523122',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="probability" fill="#7FFF00" radius={[8, 8, 0, 0]}>
                    {Object.entries(predictionResult.probabilities || {}).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill="#7FFF00" />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Feature Importance Chart - Recharts */}
            {predictionResult.explainability_json && Object.keys(predictionResult.explainability_json).length > 0 && (
              <div className="mb-8 bg-gray-50 rounded-xl p-6 border-2 border-gray-200 animate-fadeIn">
                <div className="mb-4">
                  <h3 className="text-3xl font-bold text-gray-900 mb-2 tracking-tight">Feature Importance Chart</h3>
                  <p className="text-sm text-gray-600">Visual breakdown of feature contributions to the prediction</p>
                </div>
                <ExplanationChart featureImportance={predictionResult.explainability_json} />
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-4 mt-8 pt-6 border-t-2 border-gray-200">
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setPredictionResult(null);
                  setError(null);
                  setAnalysisText('');
                  // Scroll back to top
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
                className="flex-1 px-6 py-3 rounded-lg font-bold text-base transition-all duration-200 bg-gray-900 hover:bg-gray-800 text-white shadow-lg hover:shadow-xl"
              >
                New Analysis
              </button>
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  // Print or download results
                  window.print();
                }}
                className="flex-1 px-6 py-3 rounded-lg font-bold text-base transition-all duration-200 bg-[#7FFF00] hover:bg-[#6ee000] text-black shadow-lg hover:shadow-xl"
              >
                Download Report
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Complete Message */}
      {!isAnalyzing && analysisText === 'Analysis complete! Results ready.' && !predictionResult && !error && (
        <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg shadow-lg p-6 border-l-4 border-[#7FFF00]">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="text-green-600 text-3xl">✓</div>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-bold text-gray-800 mb-2">Analysis Complete</h3>
              <p className="text-[#2d8000] font-medium text-base">
                {analysisText}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Missing Features Modal */}
      {missingFeaturesModal.isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-fadeIn">
          <div className="bg-white rounded-xl shadow-2xl border-2 border-black max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-gray-900 to-gray-800 text-white p-6 rounded-t-xl border-b-2 border-black">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-[#7FFF00] rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold tracking-tight">Complete Missing Features</h2>
                    <p className="text-sm text-gray-300 mt-1">
                      {missingFeaturesModal.missingFeatureNames.length} feature{missingFeaturesModal.missingFeatureNames.length > 1 ? 's' : ''} could not be extracted. Please enter manually.
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setMissingFeaturesModal({ isOpen: false, extractedFeatures: {}, missingFeatureNames: [], missingFeatureData: {} });
                    setValidationErrors({});
                  }}
                  className="text-gray-300 hover:text-white transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              {/* Extracted Features Summary */}
              {Object.keys(missingFeaturesModal.extractedFeatures).length > 0 && (
                <div className="mb-6 p-4 bg-green-50 rounded-lg border-2 border-green-200">
                  <p className="text-sm font-semibold text-green-800 mb-2">
                    ✓ Successfully extracted {Object.keys(missingFeaturesModal.extractedFeatures).length} out of 24 features
                  </p>
                </div>
              )}

              {/* Missing Features Form */}
              <div className="mb-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Enter Missing Values</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {missingFeaturesModal.missingFeatureNames.map((featureName) => {
                    const field = medicalFields.find(f => f.label === featureName);
                    if (!field) return null;
                    
                    const errorKey = `missing_${featureName}`;
                    const hasError = validationErrors[errorKey];
                    
                    return (
                      <div key={featureName} className="flex flex-col">
                        <label className="text-sm font-medium text-gray-900 mb-2">
                          {featureName}
                          <span className="text-red-600 ml-1">*</span>
                          {field.unit && <span className="text-gray-500 font-normal ml-1">({field.unit})</span>}
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          value={missingFeaturesModal.missingFeatureData[featureName] || ''}
                          onChange={(e) => handleMissingFeatureChange(featureName, e.target.value)}
                          placeholder={`Enter value (suggested range: ${field.min.toFixed(2)} - ${field.max.toFixed(2)})`}
                          className={`px-4 py-2 border-2 rounded-lg focus:outline-none transition-colors duration-200 ${
                            hasError
                              ? 'border-red-500 focus:border-red-600'
                              : 'border-gray-300 focus:border-[#7FFF00]'
                          }`}
                          required
                          min={undefined}
                          max={undefined}
                        />
                        {hasError && (
                          <span className="text-red-600 text-xs mt-1 font-medium">
                            {validationErrors[errorKey]}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 pt-4 border-t-2 border-gray-200">
                <button
                  type="button"
                  onClick={() => {
                    setMissingFeaturesModal({ isOpen: false, extractedFeatures: {}, missingFeatureNames: [], missingFeatureData: {} });
                    setValidationErrors({});
                  }}
                  className="flex-1 px-6 py-3 rounded-lg font-bold text-base transition-all duration-200 bg-gray-200 hover:bg-gray-300 text-gray-800 shadow-lg"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleCompleteMissingFeatures}
                  className="flex-1 px-6 py-3 rounded-lg font-bold text-base transition-all duration-200 bg-[#7FFF00] hover:bg-[#6ee000] text-black shadow-lg hover:shadow-xl"
                >
                  Complete & Analyze
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictDisease;
