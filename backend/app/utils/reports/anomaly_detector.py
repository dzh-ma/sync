"""
This module provides functionality in detecting usage anomalies.
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class EnergyAnomalyDetector:
    """
    Utility for detecting anomalies in energy consumption data in real-time
    """
    
    def __init__(self, history_days: int = 30, contamination: float = 0.05):
        """
        Initialize the anomaly detector
        
        Args:
            history_days (int): Number of days of historical data to use
            contamination (float): Expected proportion of anomalies (0.01 to 0.1)
        """
        self.history_days = history_days
        self.contamination = contamination
        self.model = None
        self.scaler = None
        self.training_complete = False
    
    def train(self, historical_data: List[Dict]) -> bool:
        """
        Train the anomaly detection model using historical data
        
        Args:
            historical_data (List[Dict]): Historical energy consumption records
            
        Returns:
            bool: True if training was successful, False otherwise
        """
        if not historical_data:
            return False
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(historical_data)
            
            # Ensure timestamp is a datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            else:
                return False
            
            # Group by day and device to reduce noise
            df['date'] = df['timestamp'].dt.date
            daily_data = df.groupby(['date', 'device_id'])['energy_consumed'].sum().reset_index()
            
            # Prepare features for anomaly detection
            # For each device, calculate:
            # 1. Daily consumption
            # 2. 7-day rolling average
            # 3. Day of week (to account for weekly patterns)
            
            devices = daily_data['device_id'].unique()
            processed_data = []
            
            for device in devices:
                device_data = daily_data[daily_data['device_id'] == device]
                if len(device_data) <= 7:  # Need enough data for rolling average
                    continue
                
                # FIX:
                device_data = device_data.sort_values('date')
                device_data['day_of_week'] = pd.to_datetime(device_data['date']).dt.dayofweek
                device_data['rolling_avg_7d'] = device_data['energy_consumed'].rolling(7).mean()
                
                # Skip the first 7 days (they won't have a complete 7-day average)
                device_data = device_data.dropna()
                
                processed_data.append(device_data)
            
            if not processed_data:
                return False
            
            # Combine all devices
            full_data = pd.concat(processed_data)
            
            # Features for anomaly detection
            features = full_data[['energy_consumed', 'rolling_avg_7d', 'day_of_week']]
            
            # Standardize the features
            self.scaler = StandardScaler()
            scaled_features = self.scaler.fit_transform(features)
            
            # Train the Isolation Forest model
            self.model = IsolationForest(
                # FIX:
                contamination=self.contamination,
                random_state=42,
                n_estimators=100
            )
            self.model.fit(scaled_features)
            
            self.training_complete = True
            return True
            
        except Exception as e:
            print(f"Error training anomaly detection model: {e}")
            return False
    
    def detect_anomalies(self, new_data: List[Dict]) -> List[Dict]:
        """
        Detect anomalies in new energy consumption data
        
        Args:
            new_data (List[Dict]): New energy consumption records to analyze
            
        Returns:
            List[Dict]: Records flagged as anomalies with additional metadata
        """
        if not self.training_complete or not new_data:
            return []
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(new_data)
            
            # Ensure timestamp is a datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            else:
                return []
            
            # Group by day and device to match training data format
            df['date'] = df['timestamp'].dt.date
            daily_data = df.groupby(['date', 'device_id'])['energy_consumed'].sum().reset_index()
            
            # Prepare features for each device
            devices = daily_data['device_id'].unique()
            processed_data = []
            
            for device in devices:
                device_data = daily_data[daily_data['device_id'] == device].copy()
                if len(device_data) == 0:
                    continue
                
                # Add day of week
                device_data['day_of_week'] = pd.to_datetime(device_data['date']).dt.dayofweek
                
                # We need historical data to compute rolling average
                # For real-time detection, you would need to retrieve this from the database
                # Here we'll use a placeholder value based on the average energy consumption
                device_data['rolling_avg_7d'] = device_data['energy_consumed'].mean()
                
                processed_data.append(device_data)
            
            if not processed_data:
                return []
            
            # Combine all devices
            full_data = pd.concat(processed_data)
            
            # Original data for reference
            original_data = full_data.copy()
            
            # Features for anomaly detection
            features = full_data[['energy_consumed', 'rolling_avg_7d', 'day_of_week']]
            
            # Standardize the features
            scaled_features = self.scaler.transform(features)
            
            # Predict anomalies
            # FIX:
            predictions = self.model.predict(scaled_features)
            scores = self.model.decision_function(scaled_features)
            
            # Add predictions and scores back to the original data
            original_data['anomaly'] = predictions
            original_data['anomaly_score'] = scores
            
            # Filter to only anomalies (prediction of -1 means anomaly)
            anomalies = original_data[original_data['anomaly'] == -1]
            
            # Convert back to dictionary format
            anomaly_records = []
            for _, row in anomalies.iterrows():
                anomaly_records.append({
                    'device_id': row['device_id'],
                    # FIX:
                    'date': row['date'].strftime('%Y-%m-%d'),
                    'energy_consumed': float(row['energy_consumed']),
                    'anomaly_score': float(row['anomaly_score']),
                    'severity': 'high' if row['anomaly_score'] < -0.5 else 'medium'
                })
            
            return anomaly_records
            
        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return []
    
    def get_anomaly_description(self, anomaly: Dict) -> str:
        """
        Generate a human-readable description of an anomaly
        
        Args:
            anomaly (Dict): An anomaly record
            
        Returns:
            str: Human-readable description
        """
        device_id = anomaly.get('device_id', 'Unknown device')
        date = anomaly.get('date', 'Unknown date')
        energy = anomaly.get('energy_consumed', 0)
        severity = anomaly.get('severity', 'medium')
        
        if severity == 'high':
            return f"Unusually high energy consumption detected for {device_id} on {date}. " \
                   f"Consumption of {energy:.2f} kWh is significantly above normal levels."
        else:
            return f"Abnormal energy consumption detected for {device_id} on {date}. " \
                   f"Consumption of {energy:.2f} kWh deviates from expected patterns."
