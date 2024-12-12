import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import random

class PatientDataLoader:
    def __init__(self, mimic_path: Optional[str] = None):
        self.mimic_path = mimic_path
        self.patients_df = None
        self.admissions_df = None
        self.diagnoses_df = None
        self.procedures_df = None
        
        try:
            if mimic_path and os.path.exists(mimic_path):
                self.load_mimic_data()
            else:
                self.generate_synthetic_data()
        except Exception as e:
            print(f"Error loading MIMIC data: {str(e)}, using synthetic data instead")
            self.generate_synthetic_data()
    
    def generate_synthetic_data(self):
        """Generate synthetic patient data for simulation."""
        # Generate synthetic patients
        patient_count = 100
        current_time = datetime.now()
        
        patients = []
        admissions = []
        diagnoses = []
        procedures = []
        
        # Common diagnoses and procedures
        diagnoses_list = [
            "Acute Myocardial Infarction",
            "Pneumonia",
            "Stroke",
            "Appendicitis",
            "Diabetic Ketoacidosis",
            "Trauma",
            "Sepsis",
            "Congestive Heart Failure",
            "Acute Respiratory Failure",
            "Gastrointestinal Bleeding"
        ]
        
        procedures_list = [
            "Coronary Angiography",
            "Appendectomy",
            "CT Scan",
            "MRI",
            "Endoscopy",
            "Mechanical Ventilation",
            "Central Line Placement",
            "Blood Transfusion",
            "Dialysis",
            "Surgery"
        ]
        
        locations = [
            "EMERGENCY ROOM",
            "MEDICAL INTENSIVE CARE UNIT",
            "SURGICAL INTENSIVE CARE UNIT",
            "OPERATING ROOM",
            "GENERAL WARD",
            "SURGICAL WARD"
        ]
        
        for i in range(patient_count):
            # Generate patient
            patient_id = f"P{i+1:03d}"
            gender = random.choice(['M', 'F'])
            age = random.randint(18, 90)
            dob = current_time - timedelta(days=age*365)
            
            patients.append({
                'subject_id': patient_id,
                'gender': gender,
                'dob': dob
            })
            
            # Generate admission
            admission_time = current_time - timedelta(days=random.randint(0, 30))
            discharge_time = (
                admission_time + timedelta(days=random.randint(1, 14))
                if random.random() > 0.3 else None  # 30% still admitted
            )
            
            admission_type = "EMERGENCY" if random.random() < 0.3 else "ELECTIVE"
            diagnosis = random.choice(diagnoses_list)
            location = random.choice(locations)
            
            admissions.append({
                'subject_id': patient_id,
                'hadm_id': f"H{i+1:03d}",
                'admittime': admission_time,
                'dischtime': discharge_time,
                'admission_type': admission_type,
                'admission_location': location,
                'diagnosis': diagnosis
            })
            
            # Generate diagnoses and procedures
            num_diagnoses = random.randint(1, 5)
            num_procedures = random.randint(0, 3)
            
            for j in range(num_diagnoses):
                diagnoses.append({
                    'subject_id': patient_id,
                    'hadm_id': f"H{i+1:03d}",
                    'icd_code': random.choice(diagnoses_list)
                })
            
            for j in range(num_procedures):
                procedures.append({
                    'subject_id': patient_id,
                    'hadm_id': f"H{i+1:03d}",
                    'icd_code': random.choice(procedures_list)
                })
        
        # Convert to DataFrames
        self.patients_df = pd.DataFrame(patients)
        self.admissions_df = pd.DataFrame(admissions)
        self.diagnoses_df = pd.DataFrame(diagnoses)
        self.procedures_df = pd.DataFrame(procedures)
    
    def load_mimic_data(self):
        """Load data from MIMIC-IV database."""
        def load_csv(filename):
            # Try uncompressed file first
            filepath = os.path.join(self.mimic_path, filename)
            if os.path.exists(filepath):
                return pd.read_csv(filepath)
            # Try compressed file
            gz_filepath = filepath + '.gz'
            if os.path.exists(gz_filepath):
                return pd.read_csv(gz_filepath, compression='gzip')
            raise FileNotFoundError(f"Neither {filepath} nor {gz_filepath} found")

        try:
            self.patients_df = load_csv('patients.csv')
            self.admissions_df = load_csv('admissions.csv')
            self.diagnoses_df = load_csv('diagnoses_icd.csv')
            self.procedures_df = load_csv('procedures_icd.csv')
            
            # Convert date columns
            if 'dob' in self.patients_df.columns:
                self.patients_df['dob'] = pd.to_datetime(self.patients_df['dob'])
            if 'admittime' in self.admissions_df.columns:
                self.admissions_df['admittime'] = pd.to_datetime(self.admissions_df['admittime'])
            if 'dischtime' in self.admissions_df.columns:
                self.admissions_df['dischtime'] = pd.to_datetime(self.admissions_df['dischtime'])
            if 'deathtime' in self.admissions_df.columns:
                self.admissions_df['deathtime'] = pd.to_datetime(self.admissions_df['deathtime'])
        except Exception as e:
            print(f"Error loading MIMIC data: {str(e)}")
            raise
    
    def get_patient_info(self, patient_id: str) -> Dict:
        """Get comprehensive patient information."""
        patient = self.patients_df[self.patients_df['subject_id'] == patient_id].iloc[0]
        admissions = self.admissions_df[self.admissions_df['subject_id'] == patient_id]
        diagnoses = self.diagnoses_df[self.diagnoses_df['subject_id'] == patient_id]
        procedures = self.procedures_df[self.procedures_df['subject_id'] == patient_id]
        
        latest_admission = admissions.iloc[-1] if not admissions.empty else None
        
        return {
            'patient_id': patient_id,
            'gender': patient['gender'],
            'age': (datetime.now().year - patient['dob'].year),
            'latest_admission': {
                'admission_type': latest_admission['admission_type'] if latest_admission is not None else None,
                'admission_location': latest_admission['admission_location'] if latest_admission is not None else None,
                'diagnosis': latest_admission['diagnosis'] if latest_admission is not None else None,
            },
            'diagnoses': diagnoses['icd_code'].tolist(),
            'procedures': procedures['icd_code'].tolist()
        }
    
    def get_active_patients(self) -> List[Dict]:
        """Get list of patients from the last 30 days."""
        current_time = datetime.now()
        thirty_days_ago = current_time - timedelta(days=30)
        
        # Get all admissions from the last 30 days
        recent_admissions = self.admissions_df[
            ((self.admissions_df['admittime'] >= thirty_days_ago) & 
             (self.admissions_df['admittime'] <= current_time)) |
            ((self.admissions_df['dischtime'].isna()) | 
             (self.admissions_df['dischtime'] >= thirty_days_ago))
        ]
        
        active_patients = []
        for _, admission in recent_admissions.iterrows():
            try:
                patient_info = self.get_patient_info(admission['subject_id'])
                patient_info['current_location'] = admission['admission_location']
                active_patients.append(patient_info)
            except Exception as e:
                print(f"Error processing patient {admission['subject_id']}: {str(e)}")
                continue
        
        return active_patients
    
    def get_patient_history(self, patient_id: str) -> List[Dict]:
        """Get patient's medical history."""
        admissions = self.admissions_df[self.admissions_df['subject_id'] == patient_id]
        history = []
        
        for _, admission in admissions.iterrows():
            admission_diagnoses = self.diagnoses_df[
                (self.diagnoses_df['subject_id'] == patient_id) &
                (self.diagnoses_df['hadm_id'] == admission['hadm_id'])
            ]
            
            admission_procedures = self.procedures_df[
                (self.procedures_df['subject_id'] == patient_id) &
                (self.procedures_df['hadm_id'] == admission['hadm_id'])
            ]
            
            history.append({
                'admission_time': admission['admittime'],
                'discharge_time': admission['dischtime'],
                'admission_type': admission['admission_type'],
                'diagnosis': admission['diagnosis'],
                'diagnoses_codes': admission_diagnoses['icd_code'].tolist(),
                'procedures': admission_procedures['icd_code'].tolist()
            })
        
        return history
    
    def get_department_distribution(self) -> Dict[str, int]:
        """Get current patient distribution across departments."""
        current_time = datetime.now()
        active_admissions = self.admissions_df[
            (self.admissions_df['admittime'] <= current_time) &
            ((self.admissions_df['dischtime'].isna()) | 
             (self.admissions_df['dischtime'] >= current_time))
        ]
        
        return active_admissions['admission_location'].value_counts().to_dict()
    
    def get_emergency_cases(self) -> List[Dict]:
        """Get list of emergency admissions."""
        current_time = datetime.now()
        emergency_admissions = self.admissions_df[
            (self.admissions_df['admission_type'] == 'EMERGENCY') &
            (self.admissions_df['admittime'] <= current_time) &
            ((self.admissions_df['dischtime'].isna()) | 
             (self.admissions_df['dischtime'] >= current_time))
        ]
        
        emergency_cases = []
        for _, admission in emergency_admissions.iterrows():
            patient_info = self.get_patient_info(admission['subject_id'])
            patient_info['admission_time'] = admission['admittime']
            patient_info['primary_diagnosis'] = admission['diagnosis']
            patient_info['current_location'] = admission['admission_location']
            emergency_cases.append(patient_info)
        
        return emergency_cases

class MIMICDataLoader:
    def __init__(self, mimic_path: str):
        """Initialize MIMIC data loader with path to MIMIC-IV database"""
        self.mimic_path = mimic_path
        self.patients_df = None
        self.admissions_df = None
        self.diagnoses_df = None
        self.load_data()
    
    def load_data(self):
        """Load required MIMIC-IV tables"""
        try:
            print("Loading MIMIC tables...")
            
            # Load core patient data from core module
            patients_path = os.path.join(self.mimic_path, "core", "patients.csv")
            print(f"Loading patients from: {patients_path}")
            self.patients_df = pd.read_csv(patients_path)
            print(f"Loaded {len(self.patients_df)} patients")
            
            # Load hospital admissions from hosp module
            admissions_path = os.path.join(self.mimic_path, "hosp", "admissions.csv")
            print(f"Loading admissions from: {admissions_path}")
            self.admissions_df = pd.read_csv(admissions_path)
            print(f"Loaded {len(self.admissions_df)} admissions")
            
            # Load diagnoses from hosp module
            diagnoses_path = os.path.join(self.mimic_path, "hosp", "diagnoses_icd.csv")
            print(f"Loading diagnoses from: {diagnoses_path}")
            self.diagnoses_df = pd.read_csv(diagnoses_path)
            print(f"Loaded {len(self.diagnoses_df)} diagnoses")
            
            print("Successfully loaded all MIMIC tables")
            
        except Exception as e:
            print(f"Error loading MIMIC data: {str(e)}")
            raise RuntimeError(f"Error loading MIMIC data: {str(e)}")
    
    def get_random_patients(self, n: int = 10) -> List[Dict]:
        """Get n random patients with their admission and diagnosis data"""
        if self.patients_df is None or self.admissions_df is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        
        # Get random sample of patients
        random_patients = self.patients_df.sample(n=n)
        patient_data = []
        
        for _, patient in random_patients.iterrows():
            # Get patient's admissions
            patient_admissions = self.admissions_df[
                self.admissions_df['subject_id'] == patient['subject_id']
            ]
            
            if len(patient_admissions) > 0:
                # Get latest admission
                latest_admission = patient_admissions.iloc[0]
                
                # Get diagnoses for this admission
                diagnoses = self.diagnoses_df[
                    (self.diagnoses_df['subject_id'] == patient['subject_id']) &
                    (self.diagnoses_df['hadm_id'] == latest_admission['hadm_id'])
                ]
                
                patient_data.append({
                    'patient_id': str(patient['subject_id']),
                    'gender': patient['gender'],
                    'age': patient.get('anchor_age', 0),
                    'admission_type': latest_admission['admission_type'],
                    'admission_location': latest_admission['admission_location'],
                    'discharge_location': latest_admission['discharge_location'],
                    'length_of_stay': latest_admission.get('los', 0),
                    'diagnoses': diagnoses['icd_code'].tolist() if len(diagnoses) > 0 else []
                })
        
        return patient_data
    
    def get_admission_location_stats(self) -> Dict[str, int]:
        """Get statistics about admission locations"""
        if self.admissions_df is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        
        return self.admissions_df['admission_location'].value_counts().to_dict()
    
    def get_admission_type_stats(self) -> Dict[str, int]:
        """Get statistics about admission types"""
        if self.admissions_df is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        
        return self.admissions_df['admission_type'].value_counts().to_dict()
    
    def get_length_of_stay_stats(self) -> Dict[str, float]:
        """Get statistics about length of stay"""
        if self.admissions_df is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        
        los_stats = self.admissions_df['los'].describe()
        return {
            'mean': los_stats['mean'],
            'median': los_stats['50%'],
            'min': los_stats['min'],
            'max': los_stats['max']
        }
    
    def get_diagnoses_frequency(self, top_n: int = 10) -> Dict[str, int]:
        """Get the most common diagnoses"""
        if self.diagnoses_df is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        
        return self.diagnoses_df['icd_code'].value_counts().head(top_n).to_dict()
    
    def get_patient_details(self, patient_id: str) -> Optional[Dict]:
        """Get detailed information for a specific patient"""
        if self.patients_df is None or self.admissions_df is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        
        # Get patient data
        patient = self.patients_df[self.patients_df['subject_id'] == int(patient_id)]
        if len(patient) == 0:
            return None
        
        # Get patient's admissions
        admissions = self.admissions_df[
            self.admissions_df['subject_id'] == int(patient_id)
        ]
        
        # Get patient's diagnoses
        diagnoses = self.diagnoses_df[
            self.diagnoses_df['subject_id'] == int(patient_id)
        ]
        
        return {
            'patient_id': str(patient_id),
            'gender': patient.iloc[0]['gender'],
            'age': patient.iloc[0].get('anchor_age', 0),
            'admissions': [
                {
                    'admission_id': str(row['hadm_id']),
                    'admission_type': row['admission_type'],
                    'admission_location': row['admission_location'],
                    'discharge_location': row['discharge_location'],
                    'length_of_stay': row.get('los', 0)
                }
                for _, row in admissions.iterrows()
            ],
            'diagnoses': diagnoses['icd_code'].tolist()
        }