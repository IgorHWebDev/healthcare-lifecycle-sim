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