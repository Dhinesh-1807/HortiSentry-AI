import React, { useState, useMemo } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  Upload,
  Camera,
  CheckCircle2,
  AlertCircle,
  Leaf,
  Search,
  Check,
  Loader2,
  MapPin
} from 'lucide-react';
import { CropConfig } from '../../types';
import { ProgressBar } from '../../components/ProgressBar';
import { Alert } from '../../components/Alert';
import { createObservation } from '../../services/api';

// Hierarchical Horticultural Location Clusters (State -> District -> Village)
export const HORTICULTURE_LOCATIONS: Record<string, Record<string, string[]>> = {
  'Tamil Nadu': {
    'Salem': ['Attur', 'Omalur', 'Mecheri', 'Yercaud', 'Valapadi', 'Edappadi', 'Salem Rural'],
    'Dindigul': ['Oddanchatram', 'Palani', 'Kodaikanal', 'Natham', 'Batlagundu', 'Vedasandur', 'Dindigul Rural'],
    'Dharmapuri': ['Palacode', 'Pennagaram', 'Harur', 'Karimangalam', 'Nallampalli', 'Pappireddipatti'],
    'Krishnagiri': ['Hosur', 'Denkanikottai', 'Rayakottai', 'Kelamangalam', 'Pochampalli', 'Uthangarai'],
    'Theni': ['Periyakulam', 'Bodinayakanur', 'Cumbum', 'Uthamapalayam', 'Andipatti', 'Chinnamanur'],
    'Nilgiris': ['Ooty', 'Coonoor', 'Kotagiri', 'Gudalur', 'Kundah'],
    'Coimbatore': ['Pollachi', 'Mettupalayam', 'Sulur', 'Thondamuthur', 'Annur', 'Kinathukadavu'],
    'Erode': ['Gobichettipalayam', 'Bhavani', 'Sathyamangalam', 'Perundurai', 'Anthiyur'],
    'Tiruppur': ['Udumalaipettai', 'Dharapuram', 'Kangeyam', 'Madathukulam', 'Palladam'],
    'Madurai': ['Melur', 'Vadipatti', 'Usilampatti', 'Tirumangalam', 'Sholavandan'],
    'Namakkal': ['Rasipuram', 'Paramathi Velur', 'Kolli Hills', 'Tiruchengode', 'Sendamangalam']
  },
  'Karnataka': {
    'Bengaluru Rural': ['Green Valley', 'Doddaballapur', 'Devanahalli', 'Nelamangala', 'Hoskote'],
    'Kolar': ['Malur', 'Bangarapet', 'Srinivaspur', 'Mulbagal', 'Kolar Rural'],
    'Chikkaballapur': ['Chintamani', 'Sidlaghatta', 'Gudibande', 'Bagepalli', 'Gauribidanur'],
    'Belagavi': ['Chikkodi', 'Gokak', 'Hukkeri', 'Athani', 'Bailhongal', 'Khanapur'],
    'Hassan': ['Sakleshpur', 'Belur', 'Alur', 'Arsikere', 'Channarayapatna'],
    'Mysuru': ['Hunsur', 'Nanjangud', 'Periyapatna', 'T. Narasipura', 'HD Kote'],
    'Mandya': ['Pandavapura', 'Srirangapatna', 'Maddur', 'Malavalli', 'Nagamangala'],
    'Chikkamagaluru': ['Mudigere', 'Koppa', 'Sringeri', 'Tarikere', 'Narasimharajapura'],
    'Shimoga': ['Thirthahalli', 'Sagar', 'Shikaripura', 'Sorab', 'Bhadravathi']
  },
  'Maharashtra': {
    'Nashik': ['Niphad', 'Dindori', 'Yeola', 'Sinnar', 'Satana', 'Kalwan'],
    'Pune': ['Junnar', 'Ambegaon', 'Khed', 'Baramati', 'Indapur', 'Shirur'],
    'Satara': ['Panchgani', 'Mahabaleshwar', 'Wai', 'Karad', 'Phaltan'],
    'Ahmednagar': ['Sangamner', 'Rahata', 'Kopargaon', 'Shrirampur', 'Akole'],
    'Solapur': ['Pandharpur', 'Barshi', 'Malshiras', 'Sangola', 'Karmala'],
    'Sangli': ['Miraj', 'Tasgaon', 'Walwa', 'Khanapur', 'Palus'],
    'Nagpur': ['Katol', 'Narkhed', 'Kalmeshwar', 'Saoner', 'Ramtek']
  },
  'Andhra Pradesh': {
    'Chittoor': ['Madanapalle', 'Punganur', 'Palamaner', 'Bangarupalem', 'Kuppam'],
    'Anantapur': ['Tadipatri', 'Dharmavaram', 'Kadiri', 'Hindupur', 'Rayadurg'],
    'Guntur': ['Tenali', 'Narasaraopet', 'Sattenapalle', 'Bapatla', 'Mangalagiri'],
    'Krishna': ['Nuzvid', 'Gudivada', 'Machilipatnam', 'Vuyyuru', 'Jaggayyapeta']
  },
  'Kerala': {
    'Wayanad': ['Mananthavady', 'Sulthan Bathery', 'Vythiri', 'Kalpetta', 'Ambalavayal'],
    'Idukki': ['Devikulam', 'Udumbanchola', 'Peermade', 'Thodupuzha', 'Munnar'],
    'Palakkad': ['Mannarkkad', 'Ottapalam', 'Alathur', 'Chittur', 'Pattambi']
  },
  'Himachal Pradesh': {
    'Shimla': ['Kotkhai', 'Rohru', 'Rampur', 'Theog', 'Jubbal'],
    'Kullu': ['Manali', 'Banjar', 'Anni', 'Nirmand'],
    'Kinnaur': ['Kalpa', 'Nichar', 'Pooh', 'Sangla']
  }
};

interface ObservationWizardProps {
  crops: CropConfig[];
  onNavigate: (route: string) => void;
}

export const ObservationWizard: React.FC<ObservationWizardProps> = ({ crops, onNavigate }) => {
  const [step, setStep] = useState<number>(1);

  // Category & Search state
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Form State
  const [selectedCropKey, setSelectedCropKey] = useState<string>('');
  const [file, setFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageMeta, setImageMeta] = useState<{ width: number; height: number; sizeMB: number } | null>(null);
  const [imageError, setImageError] = useState<string | null>(null);
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [selectedStage, setSelectedStage] = useState<string>('VEGETATIVE');
  
  // Location Hierarchy State with sensible defaults
  const [state, setState] = useState<string>('Tamil Nadu');
  const [district, setDistrict] = useState<string>('Salem');
  const [village, setVillage] = useState<string>('Attur');
  const [notes, setNotes] = useState<string>('');
  const [symptomObservedAt, setSymptomObservedAt] = useState<string>('');

  const [variety, setVariety] = useState<string>('');
  const [farmerConfidence, setFarmerConfidence] = useState<number>(0.8);

  // Submitting State
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Sample leaf generator helper for fast evaluation
  const handleUseSampleImage = () => {
    setImageError(null);
    const canvas = document.createElement('canvas');
    canvas.width = 300;
    canvas.height = 300;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Draw background leaf
    ctx.fillStyle = '#2E7D32';
    ctx.beginPath();
    ctx.ellipse(150, 150, 110, 130, Math.PI / 4, 0, 2 * Math.PI);
    ctx.fill();

    // Leaf main vein
    ctx.strokeStyle = '#81C784';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(50, 250);
    ctx.quadraticCurveTo(150, 150, 250, 50);
    ctx.stroke();

    // Secondary veins
    ctx.lineWidth = 2;
    for (let i = 0; i < 5; i++) {
      ctx.beginPath();
      ctx.moveTo(80 + i * 30, 220 - i * 30);
      ctx.lineTo(60 + i * 30, 190 - i * 30);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(90 + i * 30, 210 - i * 30);
      ctx.lineTo(120 + i * 30, 230 - i * 30);
      ctx.stroke();
    }

    // Leaf spot symptoms (Early Blight concentric target spots)
    ctx.fillStyle = '#5D4037';
    ctx.beginPath();
    ctx.arc(130, 110, 20, 0, 2 * Math.PI);
    ctx.fill();
    ctx.strokeStyle = '#8D6E63';
    ctx.lineWidth = 3;
    ctx.stroke();

    ctx.fillStyle = '#6D4C41';
    ctx.beginPath();
    ctx.arc(180, 160, 15, 0, 2 * Math.PI);
    ctx.fill();

    canvas.toBlob((blob) => {
      if (!blob) return;
      const sampleFile = new File([blob], 'sample_tomato_leaf.png', { type: 'image/png' });
      setFile(sampleFile);
      const url = URL.createObjectURL(blob);
      setImagePreview(url);
      setImageMeta({
        width: 300,
        height: 300,
        sizeMB: parseFloat((blob.size / (1024 * 1024)).toFixed(2))
      });
    }, 'image/png');
  };

  const selectedCropConfig = crops.find((c) => c.key === selectedCropKey) || null;

  // Filter crops based on category and search query
  const filteredCrops = useMemo(() => {
    return crops.filter((c) => {
      const matchCat =
        selectedCategory === 'all' ||
        (c.category && c.category.toLowerCase() === selectedCategory.toLowerCase());
      
      const q = searchQuery.toLowerCase().trim();
      const matchSearch =
        !q ||
        c.key.toLowerCase().includes(q) ||
        (c.common_name && c.common_name.toLowerCase().includes(q)) ||
        (c.display_name && c.display_name.toLowerCase().includes(q));

      return matchCat && matchSearch;
    });
  }, [crops, selectedCategory, searchQuery]);

  // Derived location lists based on state & district selection
  const availableDistricts = useMemo(() => {
    return HORTICULTURE_LOCATIONS[state] ? Object.keys(HORTICULTURE_LOCATIONS[state]) : [];
  }, [state]);

  const availableVillages = useMemo(() => {
    return HORTICULTURE_LOCATIONS[state]?.[district] || [];
  }, [state, district]);

  const handleStateChange = (newState: string) => {
    setState(newState);
    const districts = HORTICULTURE_LOCATIONS[newState] ? Object.keys(HORTICULTURE_LOCATIONS[newState]) : [];
    if (districts.length > 0) {
      const firstDistrict = districts[0];
      setDistrict(firstDistrict);
      const villages = HORTICULTURE_LOCATIONS[newState][firstDistrict] || [];
      setVillage(villages[0] || '');
    } else {
      setDistrict('');
      setVillage('');
    }
  };

  const handleDistrictChange = (newDistrict: string) => {
    setDistrict(newDistrict);
    const villages = HORTICULTURE_LOCATIONS[state]?.[newDistrict] || [];
    setVillage(villages[0] || '');
  };

  const handleVillageChange = (newVillage: string) => {
    setVillage(newVillage);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setImageError(null);
    if (!e.target.files || e.target.files.length === 0) return;

    const selectedFile = e.target.files[0];
    const sizeMB = selectedFile.size / (1024 * 1024);

    const allowedExts = ['jpg', 'jpeg', 'png', 'webp'];
    const ext = selectedFile.name.split('.').pop()?.toLowerCase() || '';
    if (!allowedExts.includes(ext)) {
      setImageError('Please select a JPG, JPEG, PNG, or WEBP image.');
      return;
    }

    if (sizeMB > 10) {
      setImageError('File size exceeds the 10 MB limit. Please select a smaller image.');
      return;
    }

    setFile(selectedFile);

    const reader = new FileReader();
    reader.onload = (event) => {
      const imgUrl = event.target?.result as string;
      setImagePreview(imgUrl);

      const img = new Image();
      img.onload = () => {
        setImageMeta({
          width: img.width,
          height: img.height,
          sizeMB: parseFloat(sizeMB.toFixed(2)),
        });
      };
      img.src = imgUrl;
    };
    reader.readAsDataURL(selectedFile);
  };

  const toggleSymptom = (sym: string) => {
    if (selectedSymptoms.includes(sym)) {
      setSelectedSymptoms(selectedSymptoms.filter((s) => s !== sym));
    } else {
      setSelectedSymptoms([...selectedSymptoms, sym]);
    }
  };

  const canProceed = (): boolean => {
    if (step === 1) return !!selectedCropKey;
    if (step === 2) return !!file && !imageError;
    if (step === 3) return selectedSymptoms.length > 0;
    if (step === 4) return !!selectedStage;
    if (step === 5) return village.trim().length > 0 && district.trim().length > 0 && state.trim().length > 0;
    return true;
  };

  const handleSubmit = async () => {
    if (!file) return;
    setSubmitting(true);
    setSubmitError(null);

    try {
      const formData = new FormData();
      formData.append('crop_id', selectedCropKey);
      formData.append('crop_stage', selectedStage);
      formData.append('symptoms', JSON.stringify(selectedSymptoms));
      formData.append('village', village);
      formData.append('district', district);
      formData.append('state', state);
      if (notes) formData.append('notes', notes);
      if (symptomObservedAt) formData.append('symptom_observed_at', symptomObservedAt);
      if (variety) formData.append('variety', variety);
      if (farmerConfidence !== null && farmerConfidence !== undefined) {
        formData.append('farmer_confidence', String(farmerConfidence));
      }
      formData.append('file', file);

      const result = await createObservation(formData);
      onNavigate(`/ai-review/${result.observation_id}`);
    } catch (err: any) {
      console.error('Submission error:', err);
      setSubmitError(err.message || 'We could not submit the observation. Please check your connection and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const stepNames = [
    'Crop Catalogue',
    'Image Upload',
    'Select Symptoms',
    'Crop Growth Stage',
    'Location & Notes',
    'Review & Submit'
  ];

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-2xl border border-slate-200 shadow-sm p-5 sm:p-7 relative">
      <ProgressBar currentStep={step} totalSteps={6} stepName={stepNames[step - 1]} />

      <div className="space-y-6 min-h-[380px]">
        {/* STEP 1: MULTI-CROP CATALOGUE SELECTION */}
        {step === 1 && (
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-slate-900">Select Target Horticultural Crop</h2>
                <span className="text-xs bg-amber-100 text-amber-800 font-bold px-2.5 py-0.5 rounded-full border border-amber-300">
                  Mandatory Selection
                </span>
              </div>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Choose from 32 supported horticultural crops across Vegetables, Fruits, and Spices.
              </p>
            </div>

            {!selectedCropKey && (
              <div className="bg-amber-50 border border-amber-300 rounded-xl p-3 text-xs text-amber-800 font-semibold flex items-center gap-2 shadow-xs">
                <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                <span>Crop selection is mandatory. Please click on a crop card below to select your target crop before proceeding.</span>
              </div>
            )}

            {/* Category Tabs */}
            <div className="flex flex-wrap gap-2 pt-1 border-b border-slate-200 pb-3">
              {[
                { key: 'all', label: 'All Crops' },
                { key: 'vegetables', label: 'Vegetables 🥦' },
                { key: 'fruits', label: 'Fruits 🥭' },
                { key: 'spices_plantation', label: 'Spices & Plantation 🌿' },
              ].map((cat) => (
                <button
                  key={cat.key}
                  onClick={() => setSelectedCategory(cat.key)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    selectedCategory === cat.key
                      ? 'bg-emerald-700 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            {/* Search Input */}
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="text"
                placeholder="Search crop by name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-300 text-xs sm:text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              />
            </div>

            {/* Crop Catalogue Grid with Real Crop Images */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 max-h-96 overflow-y-auto pr-1">
              {filteredCrops.map((c) => {
                const isSelected = selectedCropKey === c.key;
                const isTomato = c.key === 'tomato';
                const isTrained = c.vision_support_status === 'trained_model' || isTomato;
                const cropImg = `/images/crops/${c.key}.jpg`;

                return (
                  <div
                    key={c.key}
                    onClick={() => setSelectedCropKey(c.key)}
                    className={`p-3 rounded-2xl border-2 cursor-pointer transition-all flex items-center gap-3.5 group ${
                      isSelected
                        ? 'border-emerald-600 bg-emerald-50/80 ring-2 ring-emerald-600/20 shadow-sm'
                        : 'border-slate-200 hover:border-emerald-300 hover:bg-slate-50/80 bg-white shadow-2xs'
                    }`}
                  >
                    {/* Real Crop Image */}
                    <div className="w-18 h-18 sm:w-20 sm:h-20 rounded-xl overflow-hidden bg-slate-100 flex-shrink-0 border border-slate-200/80 shadow-xs relative">
                      <img
                        src={cropImg}
                        alt={c.display_name || c.common_name || c.key}
                        className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                        loading="lazy"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="%232E7D32" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>';
                        }}
                      />
                    </div>

                    {/* Crop Details */}
                    <div className="flex-1 min-w-0 flex flex-col justify-between self-stretch py-0.5">
                      <div className="flex items-start justify-between gap-1">
                        <div>
                          <h3 className="font-bold text-slate-900 text-sm sm:text-base leading-tight truncate">
                            {c.display_name || c.common_name || c.key}
                          </h3>
                          <p className="text-[11px] text-slate-500 font-medium capitalize mt-0.5">
                            {c.category ? c.category.replace('_', ' & ') : 'Horticulture'}
                          </p>
                        </div>
                        {isSelected && (
                          <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
                        )}
                      </div>

                      {/* Vision / Evidence Status Badge */}
                      <div className="pt-1.5">
                        {isTrained ? (
                          <span className="bg-emerald-100 text-emerald-800 text-[10px] px-2 py-0.5 rounded-md font-bold inline-flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
                            AI Vision Ready
                          </span>
                        ) : (
                          <span className="bg-blue-50 text-blue-800 border border-blue-200 text-[10px] px-2 py-0.5 rounded-md font-semibold inline-flex items-center gap-1">
                            Visual Assessment
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}

              {filteredCrops.length === 0 && (
                <div className="col-span-2 text-center py-8 text-slate-500 text-xs">
                  No crops found matching "{searchQuery}". Try searching for another crop.
                </div>
              )}
            </div>
          </div>
        )}

        {/* STEP 2: IMAGE UPLOAD */}
        {step === 2 && (
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Upload Crop Leaf Photo</h2>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Provide a clear, well-lit photo focusing on the affected leaf or symptom.
              </p>
            </div>

            {imageError && (
              <Alert type="danger" title="Image Error">
                {imageError}
              </Alert>
            )}

            {!imagePreview ? (
              <div className="border-2 border-dashed border-slate-300 rounded-2xl p-8 text-center bg-slate-50/50 space-y-4 hover:border-emerald-500 transition-colors">
                <div className="w-14 h-14 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center mx-auto">
                  <Upload className="w-7 h-7" />
                </div>
                <div>
                  <p className="font-semibold text-slate-800 text-sm">Select leaf photo from device</p>
                  <p className="text-xs text-slate-400 mt-1">Supports JPG, PNG, WEBP (Max 10 MB)</p>
                </div>
                <div className="flex flex-col sm:flex-row justify-center gap-3 pt-2">
                  <label className="cursor-pointer inline-flex items-center justify-center gap-2 bg-[#2E7D32] hover:bg-[#1B5E20] text-white text-sm font-semibold px-5 py-2.5 rounded-xl transition-all shadow-sm">
                    <Upload className="w-4 h-4" />
                    Choose Image
                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/webp"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </label>
                  <label className="cursor-pointer inline-flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-900 text-white text-sm font-semibold px-5 py-2.5 rounded-xl transition-all shadow-sm">
                    <Camera className="w-4 h-4" />
                    Take Photo
                    <input
                      type="file"
                      accept="image/*"
                      capture="environment"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </label>
                  <button
                    type="button"
                    onClick={handleUseSampleImage}
                    className="inline-flex items-center justify-center gap-2 bg-[#E8F5E9] hover:bg-[#C8E6C9] text-[#1B5E20] border border-[#C8E6C9] text-sm font-bold px-4 py-2.5 rounded-xl transition-all"
                  >
                    <Leaf className="w-4 h-4 text-[#2E7D32]" />
                    Use Sample Leaf
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="relative rounded-2xl overflow-hidden border border-slate-200 bg-black/5 flex items-center justify-center max-h-64">
                  <img src={imagePreview} alt="Crop preview" className="max-h-64 object-contain rounded-xl" />
                </div>
                {imageMeta && (
                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs text-slate-600 flex justify-between items-center">
                    <div>
                      <span className="font-semibold text-slate-800">{file?.name}</span>
                      <span className="text-slate-400"> ({imageMeta.sizeMB} MB)</span>
                    </div>
                    <span className="bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-mono">
                      {imageMeta.width} x {imageMeta.height} px
                    </span>
                  </div>
                )}
                <div className="flex justify-end">
                  <label className="cursor-pointer text-xs font-semibold text-emerald-700 hover:text-emerald-900 underline">
                    Choose Another Image
                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/webp"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </label>
                </div>
              </div>
            )}
          </div>
        )}

        {/* STEP 3: SYMPTOMS SELECTION */}
        {step === 3 && (
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Select Observed Symptoms</h2>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Select visual symptoms visible on the leaf for {selectedCropConfig?.common_name || selectedCropKey}.
              </p>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-1">
              {(selectedCropConfig?.symptoms || ['Yellow spots', 'Brown spots', 'Leaf curling', 'Wilting', 'Discoloration']).map((symItem) => {
                const symName = typeof symItem === 'string' ? symItem : (symItem as any).display_name || String(symItem);
                const isSelected = selectedSymptoms.includes(symName);
                return (
                  <div
                    key={symName}
                    onClick={() => toggleSymptom(symName)}
                    className={`p-3 rounded-xl border text-xs sm:text-sm font-semibold cursor-pointer transition-all flex items-center justify-between gap-2 ${
                      isSelected
                        ? 'border-emerald-600 bg-emerald-50/80 text-emerald-900 ring-2 ring-emerald-600/20'
                        : 'border-slate-200 bg-slate-50/50 text-slate-700 hover:border-emerald-300'
                    }`}
                  >
                    <span>{symName}</span>
                    {isSelected && <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />}
                  </div>
                );
              })}
            </div>
            {selectedSymptoms.length === 0 && (
              <p className="text-xs text-amber-700 font-medium">Please select at least one symptom to proceed.</p>
            )}
          </div>
        )}

        {/* STEP 4: CROP STAGE SELECTION */}
        {step === 4 && (
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Select Crop Growth Stage</h2>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Indicate the growth stage of your crop.
              </p>
            </div>
            <div className="space-y-2.5 pt-1">
              {[
                { key: 'SEEDLING', title: 'Seedling', desc: 'Young plant with initial true leaves' },
                { key: 'VEGETATIVE', title: 'Vegetative', desc: 'Active stem and leaf growth phase' },
                { key: 'FLOWERING', title: 'Flowering', desc: 'Blossom and floral development' },
                { key: 'FRUITING', title: 'Fruiting', desc: 'Green or ripening fruit formation' },
                { key: 'HARVEST', title: 'Harvest', desc: 'Mature crop harvesting stage' },
              ].map((stage) => {
                const isSelected = selectedStage === stage.key;
                return (
                  <div
                    key={stage.key}
                    onClick={() => setSelectedStage(stage.key)}
                    className={`p-3.5 rounded-xl border cursor-pointer transition-all flex items-center justify-between gap-3 ${
                      isSelected
                        ? 'border-emerald-600 bg-emerald-50/80 ring-2 ring-emerald-600/20'
                        : 'border-slate-200 bg-slate-50/50 hover:border-emerald-300'
                    }`}
                  >
                    <div>
                      <h3 className="font-bold text-slate-900 text-sm">{stage.title}</h3>
                      <p className="text-xs text-slate-500">{stage.desc}</p>
                    </div>
                    {isSelected && <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* STEP 5: LOCATION & NOTES */}
        {step === 5 && (
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                <MapPin className="w-5 h-5 text-emerald-600" />
                Location & Field Notes
              </h2>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Select regional location (State, District, Village) for regional disease surveillance.
              </p>
            </div>

            <Alert type="info" title="Regional Privacy Protection">
              Location helps organize observations by regional agro-climatic clusters. We only collect coarse location data (State, District, Village). No street address or personal identifiers are stored.
            </Alert>

            {/* Cascading Dropdown Selectors for State, District, and Village */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {/* State Dropdown */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">State *</label>
                <select
                  value={state}
                  onChange={(e) => handleStateChange(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-sm font-medium focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 bg-white text-slate-800"
                >
                  {Object.keys(HORTICULTURE_LOCATIONS).map((st) => (
                    <option key={st} value={st}>{st}</option>
                  ))}
                </select>
              </div>

              {/* District Dropdown */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">District *</label>
                <select
                  value={district}
                  onChange={(e) => handleDistrictChange(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-sm font-medium focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 bg-white text-slate-800"
                >
                  {availableDistricts.map((dst) => (
                    <option key={dst} value={dst}>{dst}</option>
                  ))}
                </select>
              </div>

              {/* Village Dropdown */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Village *</label>
                <select
                  value={village}
                  onChange={(e) => handleVillageChange(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-sm font-medium focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 bg-white text-slate-800"
                >
                  {availableVillages.map((vlg) => (
                    <option key={vlg} value={vlg}>{vlg}</option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Symptom Observed Date & Time (Optional)</label>
              <input
                type="datetime-local"
                value={symptomObservedAt}
                onChange={(e) => setSymptomObservedAt(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Crop Variety / Hybrid (Optional)</label>
              <input
                type="text"
                placeholder="e.g. Arka Rakshak, Roma, PKM-1, Local Desi"
                value={variety}
                onChange={(e) => setVariety(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Farmer Confidence in Visual Symptoms</label>
              <div className="grid grid-cols-3 gap-2 pt-1">
                {[
                  { val: 0.4, label: 'Uncertain', desc: 'Low Confidence' },
                  { val: 0.7, label: 'Fairly Certain', desc: 'Medium Confidence' },
                  { val: 0.95, label: 'Very Confident', desc: 'High Confidence' }
                ].map((c) => (
                  <button
                    key={c.val}
                    type="button"
                    onClick={() => setFarmerConfidence(c.val)}
                    className={`p-2 rounded-xl border text-center transition-all ${
                      farmerConfidence === c.val
                        ? 'border-[#2E7D32] bg-[#E8F5E9] text-[#1B5E20] font-bold ring-1 ring-[#2E7D32]'
                        : 'border-slate-200 bg-slate-50 text-slate-700 hover:border-slate-300'
                    }`}
                  >
                    <div className="text-xs">{c.label}</div>
                    <div className="text-[10px] text-slate-500">{c.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Additional Field Notes (Optional)</label>
              <textarea
                rows={3}
                placeholder="Describe anything unusual you noticed (e.g., weather conditions, affected crop percentage)..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              />
            </div>
          </div>
        )}

        {/* STEP 6: REVIEW & SUBMIT */}
        {step === 6 && (
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Review Your Observation</h2>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Verify details before submitting for AI Evidence Review.
              </p>
            </div>

            {submitError && (
              <Alert type="danger" title="Submission Error">
                {submitError}
              </Alert>
            )}

            <div className="bg-slate-50/80 rounded-xl border border-slate-200 p-4 space-y-3.5">
              <div className="flex items-center gap-3">
                {imagePreview && (
                  <img src={imagePreview} alt="Thumbnail" className="w-16 h-16 rounded-lg object-cover border border-slate-300" />
                )}
                <div>
                  <h3 className="font-bold text-slate-900 text-base">{selectedCropConfig?.common_name || selectedCropKey}</h3>
                  <p className="text-xs font-semibold text-emerald-700">Stage: {selectedStage}</p>
                </div>
              </div>

              <div className="border-t border-slate-200 pt-2.5 space-y-2 text-xs sm:text-sm">
                <div>
                  <span className="font-semibold text-slate-500">Selected Symptoms: </span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedSymptoms.map((sym) => (
                      <span key={sym} className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-medium text-xs">
                        {sym}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="font-semibold text-slate-500">Location: </span>
                  <span className="text-slate-800 font-medium">{village}, {district}, {state}</span>
                </div>
                {notes && (
                  <div>
                    <span className="font-semibold text-slate-500">Notes: </span>
                    <span className="text-slate-700 italic">{notes}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Navigation Footer */}
      <div className="flex items-center justify-between pt-6 border-t border-slate-200 mt-6">
        {step > 1 ? (
          <button
            onClick={() => setStep(step - 1)}
            disabled={submitting}
            className="inline-flex items-center gap-1 text-sm font-semibold text-slate-600 hover:text-slate-900 px-3 py-2 rounded-lg"
          >
            <ChevronLeft className="w-4 h-4" />
            Back
          </button>
        ) : (
          <div />
        )}

        {step < 6 ? (
          <button
            onClick={() => setStep(step + 1)}
            disabled={!canProceed()}
            className="inline-flex items-center gap-1.5 bg-emerald-700 hover:bg-emerald-800 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-sm px-6 py-2.5 rounded-xl transition-all shadow-sm"
          >
            Continue
            <ChevronRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="inline-flex items-center gap-2 bg-emerald-700 hover:bg-emerald-800 disabled:opacity-50 text-white font-extrabold text-sm px-7 py-3 rounded-xl transition-all shadow-md active:scale-[0.98]"
          >
            {submitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Retrieving AI Evidence Review...
              </>
            ) : (
              'Submit Observation'
            )}
          </button>
        )}
      </div>
    </div>
  );
};
