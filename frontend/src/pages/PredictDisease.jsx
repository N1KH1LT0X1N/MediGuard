import { useState } from 'react';

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

  const handleManualAnalyze = () => {
    if (!isAllFieldsValid()) {
      alert('Please fill in all fields with valid values before analyzing');
      return;
    }

    setIsAnalyzing(true);
    setCurrentIndex(0);
    setAnalysisText(analysisSteps[0]);
    
    let index = 0;
    const interval = setInterval(() => {
      if (index < analysisSteps.length - 1) {
        index++;
        setAnalysisText(analysisSteps[index]);
        setCurrentIndex(index);
      } else {
        clearInterval(interval);
        setTimeout(() => {
          setIsAnalyzing(false);
          setAnalysisText('Analysis complete! Results ready.');
        }, 1000);
      }
    }, 1500);
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

  const simulateUpload = (file, type) => {
    setIsUploading(true);
    setCurrentUploadType(type);
    setUploadProgress(0);

    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            setIsUploading(false);
            setUploadedFiles({ ...uploadedFiles, [type]: file });
            setCurrentUploadType(null);
          }, 500);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
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

  const handleAnalyze = (type) => {
    if (!uploadedFiles[type]) {
      alert('Please upload a file first');
      return;
    }

    setIsAnalyzing(true);
    setCurrentIndex(0);
    setAnalysisText(analysisSteps[0]);
    
    // Simulate dynamic text animation
    let index = 0;
    const interval = setInterval(() => {
      if (index < analysisSteps.length - 1) {
        index++;
        setAnalysisText(analysisSteps[index]);
        setCurrentIndex(index);
      } else {
        clearInterval(interval);
        setTimeout(() => {
          setIsAnalyzing(false);
          setAnalysisText('Analysis complete! Results ready.');
        }, 1000);
      }
    }, 1500);
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
              onClick={() => handleAnalyze(type)}
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
    <div className="space-y-6 w-full font-sans">
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

      {/* Analysis Complete */}
      {!isAnalyzing && analysisText === 'Analysis complete! Results ready.' && (
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
    </div>
  );
};

export default PredictDisease;
