"""
Test script to generate a sample energy report using the modernized report generator.
"""
import asyncio
from datetime import datetime, timedelta
import numpy as np
import random

# This imports the enhanced report generator
from enhanced_report_generator import generate_energy_report

async def test_report_generation():
    """Generate a sample energy report with realistic data."""
    # Create sample energy data
    energy_data = []
    now = datetime.now()
    
    # Generate 30 days of sample data
    for day in range(30):
        # Create a cyclical pattern with some variation
        day_factor = 1 + 0.3 * np.sin(day * np.pi / 7)  # Weekly cycle
        
        # Generate hourly data for this day with realistic patterns
        # Most usage happens at peak hours (morning and evening)
        for hour in range(24):
            # Morning peak (7-9 AM)
            if 7 <= hour <= 9:
                hour_factor = 0.7
            # Evening peak (18-21 PM)
            elif 18 <= hour <= 21:
                hour_factor = 1.0
            # Midnight to early morning (low usage)
            elif 0 <= hour <= 5:
                hour_factor = 0.2
            # Other times (medium usage)
            else:
                hour_factor = 0.5
                
            # Add some random variation
            random_factor = 0.8 + random.random() * 0.4
            
            # Create timestamp for this data point
            timestamp = now - timedelta(days=day, hours=24-hour)
            
            # Generate data for 5 different devices
            for device_id in range(1, 6):
                # Device 1 uses the most energy, device 5 the least
                device_factor = (6 - device_id) / 5
                
                # Skip some entries to create a sparse dataset (more realistic)
                if random.random() > 0.7 and hour_factor < 0.7:
                    continue
                
                # Create energy value with all factors
                energy_value = hour_factor * day_factor * device_factor * random_factor
                
                # Assign to either Living Room or Bedroom
                location = "Living Room" if device_id <= 3 else "Bedroom"
                
                # Skip recording Device 5 energy (to create an example with no consumption for one device)
                if device_id == 5:
                    energy_value = 0
                
                # Add entry to dataset
                energy_data.append({
                    "timestamp": timestamp,
                    "device_id": f"Device {device_id}",
                    "energy_consumed": energy_value,
                    "location": location
                })
    
    # Add a couple of outliers for anomaly detection
    # Extremely high energy consumption on random days
    for _ in range(3):
        outlier_day = random.randint(1, 28)
        outlier_hour = random.randint(12, 20)  # During active hours
        outlier_timestamp = now - timedelta(days=outlier_day, hours=outlier_hour)
        
        energy_data.append({
            "timestamp": outlier_timestamp,
            "device_id": f"Device {random.randint(1, 3)}",  # One of the higher-consumption devices
            "energy_consumed": random.uniform(10, 15),  # Very high consumption
            "location": "Living Room"
        })
    
    # Generate the report
    user_data = {"username": "Test User"}
    start_date = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = now.strftime("%Y-%m-%d")
    
    print("Generating enhanced energy report...")
    report_path = generate_energy_report(
        energy_data=energy_data,
        user_data=user_data,
        format="pdf",
        start_date=start_date,
        end_date=end_date
    )
    
    if report_path:
        print(f"✅ Report generated successfully: {report_path}")
        print(f"Open the file to see the modern design!")
    else:
        print("❌ Failed to generate report")

if __name__ == "__main__":
    asyncio.run(test_report_generation())
