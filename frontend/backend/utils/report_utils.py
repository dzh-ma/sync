"""
Utilities for generating enhanced energy reports with visualizations and analytics
"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environments
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from io import BytesIO

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Default energy cost per kWh (using UAE rates)
# NOTE: Tiered rates: 0.23 AED/kWh till 2'000 AED; 0.28 AED/kWh till 4'000 AED; 
# 0.32 AED/kWh till 6'000 AED; 0.36 AED/kWh from 6'000 AED
DEFAULT_ENERGY_COST = 0.23  # AED per kWh

# Ensure the reports directory exists
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def calculate_tiered_cost(energy_consumption: float) -> float:
    """
    Calculate energy cost using UAE's tiered pricing structure
    
    Args:
        energy_consumption (float): Total energy consumption in kWh
        
    Returns:
        float: Estimated cost in AED
    """
    # Convert kWh tiers to actual kWh values
    # These are rough estimates and should be adjusted based on actual utility rates
    tier1_limit = 2000 / 0.23  # ~8696 kWh
    tier2_limit = 4000 / 0.28  # ~14286 kWh
    tier3_limit = 6000 / 0.32  # ~18750 kWh
    
    if energy_consumption <= tier1_limit:
        return energy_consumption * 0.23
    elif energy_consumption <= tier2_limit:
        return (tier1_limit * 0.23) + ((energy_consumption - tier1_limit) * 0.28)
    elif energy_consumption <= tier3_limit:
        return (tier1_limit * 0.23) + ((tier2_limit - tier1_limit) * 0.28) + ((energy_consumption - tier2_limit) * 0.32)
    else:
        return (tier1_limit * 0.23) + ((tier2_limit - tier1_limit) * 0.28) + ((tier3_limit - tier2_limit) * 0.32) + ((energy_consumption - tier3_limit) * 0.36)

def get_device_names(device_ids: List[str]) -> Dict[str, str]:
    """
    Generate readable device names from device IDs
    This is a placeholder - in a real implementation, you would query the devices collection
    
    Args:
        device_ids (List[str]): List of device IDs
        
    Returns:
        Dict[str, str]: Mapping of device_id to readable name
    """
    # In production, this would query your devices collection
    # For now, generate readable names based on ID
    device_names = {}
    for i, device_id in enumerate(device_ids):
        if "light" in device_id.lower():
            device_names[device_id] = f"Light {i+1}"
        elif "therm" in device_id.lower():
            device_names[device_id] = f"Thermostat {i+1}"
        elif "fridge" in device_id.lower() or "refrig" in device_id.lower():
            device_names[device_id] = f"Refrigerator {i+1}"
        elif "tv" in device_id.lower() or "television" in device_id.lower():
            device_names[device_id] = f"Television {i+1}"
        elif "ac" in device_id.lower() or "air" in device_id.lower():
            device_names[device_id] = f"Air Conditioner {i+1}"
        elif "wash" in device_id.lower():
            device_names[device_id] = f"Washing Machine {i+1}"
        elif "dryer" in device_id.lower():
            device_names[device_id] = f"Dryer {i+1}"
        elif "oven" in device_id.lower() or "stove" in device_id.lower():
            device_names[device_id] = f"Oven/Stove {i+1}"
        elif "dishwash" in device_id.lower():
            device_names[device_id] = f"Dishwasher {i+1}"
        elif "water" in device_id.lower():
            device_names[device_id] = f"Water Heater {i+1}"
        else:
            device_names[device_id] = f"Device {i+1}"
            
    return device_names

def generate_enhanced_pdf_report(
    energy_data: List[Dict], 
    user_data: Optional[Dict] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """
    Generate a comprehensive PDF report with visualizations
    
    Args:
        energy_data (List[Dict]): Energy consumption records
        user_data (Optional[Dict]): User information for personalization
        start_date (Optional[str]): Start date for filtering data
        end_date (Optional[str]): End date for filtering data
        
    Returns:
        str: Path to the generated PDF report
    """
    # Generate report filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{REPORTS_DIR}/energy_report_{timestamp}.pdf"
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(energy_data)
    
    # Ensure timestamp is datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.sort_values('timestamp', inplace=True)
    
    # Create the PDF document
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Create a title style
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,  # Center alignment
        spaceAfter=12
    )
    
    # Create a subtitle style
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    )
    
    # Create normal text style
    normal_style = styles['Normal']
    
    # Start building the document
    elements = []
    
    # Title and introduction
    elements.append(Paragraph("Smart Home Energy Consumption Report", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    report_date = datetime.now().strftime("%B %d, %Y")
    
    # Add user info if available
    if user_data and user_data.get('email'):
        elements.append(Paragraph(f"Report for: {user_data.get('email')}", normal_style))
        
    elements.append(Paragraph(f"Generated on: {report_date}", normal_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Summary section
    elements.append(Paragraph("Summary", subtitle_style))
    
    # Calculate total energy and cost
    total_energy = df['energy_consumed'].sum() if 'energy_consumed' in df.columns else 0
    total_cost = calculate_tiered_cost(total_energy)
    
    summary_data = [
        ["Total Energy Consumption", f"{total_energy:.2f} kWh"],
        ["Estimated Cost", f"{total_cost:.2f} AED"],
    ]
    
    # Add date range if available
    if 'timestamp' in df.columns and not df.empty:
        start_date_str = df['timestamp'].min().strftime("%Y-%m-%d")
        end_date_str = df['timestamp'].max().strftime("%Y-%m-%d")
        summary_data.append(["Date Range", f"{start_date_str} to {end_date_str}"])
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Add trend analysis
    elements.append(Paragraph("Energy Consumption Trends", subtitle_style))
    
    if 'timestamp' in df.columns and len(df) > 1 and 'energy_consumed' in df.columns:
        # Group by day
        daily_data = df.groupby(pd.Grouper(key='timestamp', freq='D'))['energy_consumed'].sum().reset_index()
        
        if len(daily_data) > 1:
            # Create trend visualization
            plt.figure(figsize=(8, 4))
            plt.plot(daily_data['timestamp'], daily_data['energy_consumed'], marker='o', linestyle='-')
            plt.xlabel('Date')
            plt.ylabel('Energy (kWh)')
            plt.title('Daily Energy Consumption')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save the plot to a BytesIO object
            img_data = BytesIO()
            plt.savefig(img_data, format='png')
            img_data.seek(0)
            plt.close()
            
            # Add the image to the PDF
            img = Image(img_data, width=6*inch, height=3*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.2 * inch))
            
            # Add trend insights
            if len(daily_data) > 1:
                daily_data['change'] = daily_data['energy_consumed'].pct_change() * 100
                avg_change = daily_data['change'].mean()
                if not np.isnan(avg_change):
                    trend_text = f"Your average daily change in energy consumption is {avg_change:.1f}%."
                    elements.append(Paragraph(trend_text, normal_style))
                
                # Identify highest and lowest consumption days
                max_day = daily_data.loc[daily_data['energy_consumed'].idxmax()]
                min_day = daily_data.loc[daily_data['energy_consumed'].idxmin()]
                elements.append(Paragraph(f"Highest usage: {max_day['energy_consumed']:.2f} kWh on {max_day['timestamp'].strftime('%Y-%m-%d')}", normal_style))
                elements.append(Paragraph(f"Lowest usage: {min_day['energy_consumed']:.2f} kWh on {min_day['timestamp'].strftime('%Y-%m-%d')}", normal_style))
        else:
            elements.append(Paragraph("Insufficient data to analyze trends. At least two days of data are required.", normal_style))
    else:
        elements.append(Paragraph("Insufficient data to analyze trends.", normal_style))
    
    elements.append(Spacer(1, 0.3 * inch))
    
    # Device breakdown
    elements.append(Paragraph("Energy Consumption by Device", subtitle_style))
    
    if 'device_id' in df.columns and 'energy_consumed' in df.columns:
        device_usage = df.groupby('device_id')['energy_consumed'].sum().reset_index()
        
        if not device_usage.empty:
            # Get device names
            device_names = get_device_names(device_usage['device_id'].unique())
            device_usage['device_name'] = device_usage['device_id'].map(device_names)
            
            # Sort by energy consumed (descending)
            device_usage = device_usage.sort_values('energy_consumed', ascending=False)
            
            # Calculate percentage of total
            total = device_usage['energy_consumed'].sum()
            if total > 0:
                device_usage['percentage'] = (device_usage['energy_consumed'] / total) * 100
                device_usage['cost'] = device_usage['energy_consumed'] * DEFAULT_ENERGY_COST
            
                # Create pie chart for top devices
                if len(device_usage) > 6:
                    # Show top 5 + "Others"
                    top_devices = device_usage.head(5)
                    others_energy = device_usage.iloc[5:]['energy_consumed'].sum()
                    
                    # Create a new DataFrame with Others row
                    pie_data = pd.concat([
                        top_devices,
                        pd.DataFrame({
                            'device_id': ['others'],
                            'energy_consumed': [others_energy],
                            'device_name': ['Others'],
                            'percentage': [(others_energy / total) * 100],
                            'cost': [others_energy * DEFAULT_ENERGY_COST]
                        })
                    ])
                else:
                    pie_data = device_usage
                
                # Create pie chart
                plt.figure(figsize=(8, 5))
                
                # Use device names for better readability
                labels = pie_data['device_name'].tolist()
                sizes = pie_data['energy_consumed'].tolist()
                explode = [0.1 if i == 0 else 0 for i in range(len(labels))]  # Explode the largest slice
                
                plt.pie(sizes, labels=labels, explode=explode, autopct='%1.1f%%', 
                        shadow=True, startangle=90)
                plt.axis('equal')
                plt.title('Energy Consumption by Device')
                plt.tight_layout()
                
                # Save the plot to a BytesIO object
                img_data = BytesIO()
                plt.savefig(img_data, format='png')
                img_data.seek(0)
                plt.close()
                
                # Add the image to the PDF
                img = Image(img_data, width=6*inch, height=4*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.2 * inch))
                
                # Add table with detailed breakdown
                device_table_data = [["Device", "Energy (kWh)", "Percentage", "Cost (AED)"]]
                for _, row in device_usage.iterrows():
                    device_table_data.append([
                        row['device_name'],
                        f"{row['energy_consumed']:.2f}",
                        f"{row['percentage']:.1f}%",
                        f"{row['cost']:.2f}"
                    ])
                
                device_table = Table(device_table_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                device_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(device_table)
                
                # Add insights
                elements.append(Spacer(1, 0.2 * inch))
                top_device = device_usage.iloc[0]
                elements.append(Paragraph(
                    f"Your {top_device['device_name']} is using {top_device['percentage']:.1f}% of your total energy. "
                    f"This costs approximately {top_device['cost']:.2f} AED during this period.", 
                    normal_style
                ))
            else:
                elements.append(Paragraph("No energy consumption recorded for any device.", normal_style))
        else:
            elements.append(Paragraph("No device data available.", normal_style))
    else:
        elements.append(Paragraph("Device information not available in the data.", normal_style))
    
    elements.append(Spacer(1, 0.3 * inch))
    
    # Usage patterns by time of day
    elements.append(Paragraph("Usage Patterns by Hour of Day", subtitle_style))
    
    if 'timestamp' in df.columns and 'energy_consumed' in df.columns:
        # Extract hour from timestamp
        df['hour'] = df['timestamp'].dt.hour
        
        # Group by hour
        hourly_usage = df.groupby('hour')['energy_consumed'].sum().reset_index()
        
        if not hourly_usage.empty:
            # Sort by hour for visualization
            hourly_usage = hourly_usage.sort_values('hour')
            
            # Create bar chart
            plt.figure(figsize=(8, 4))
            plt.bar(hourly_usage['hour'], hourly_usage['energy_consumed'], color='skyblue')
            plt.xlabel('Hour of Day')
            plt.ylabel('Energy Consumption (kWh)')
            plt.title('Energy Consumption by Hour of Day')
            plt.xticks(range(0, 24, 2))
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            
            # Save the plot to a BytesIO object
            img_data = BytesIO()
            plt.savefig(img_data, format='png')
            img_data.seek(0)
            plt.close()
            
            # Add the image to the PDF
            img = Image(img_data, width=6*inch, height=3*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.2 * inch))
            
            # Identify peak usage hours
            sorted_hours = hourly_usage.sort_values('energy_consumed', ascending=False)
            peak_hours = sorted_hours.head(3)
            
            # Format peak hours for display (e.g., "18:00" instead of just "18")
            peak_hours_str = ", ".join([f"{int(hour)}:00" for hour in peak_hours['hour']])
            elements.append(Paragraph(f"Your peak energy usage occurs at: {peak_hours_str}", normal_style))
            
            # Add recommendations based on peak hours
            if any(h in peak_hours['hour'].values for h in [17, 18, 19, 20]):  # Evening peak hours
                elements.append(Paragraph(
                    "You have high energy usage during evening peak hours. Consider shifting some activities to off-peak times to reduce energy costs.",
                    normal_style
                ))
        else:
            elements.append(Paragraph("Insufficient data to analyze hourly usage patterns.", normal_style))
    else:
        elements.append(Paragraph("Timestamp information not available for hourly analysis.", normal_style))
    
    elements.append(PageBreak())
    
    # Location-based analysis (if available)
    if 'location' in df.columns and 'energy_consumed' in df.columns:
        elements.append(Paragraph("Energy Consumption by Location", subtitle_style))
        
        # Fill missing locations
        df_loc = df.copy()
        df_loc['location'] = df_loc['location'].fillna('Unknown')
        
        # Group by location
        location_usage = df_loc.groupby('location')['energy_consumed'].sum().reset_index()
        
        if not location_usage.empty and len(location_usage) > 1:  # Only show if multiple locations
            # Sort by energy consumed (descending)
            location_usage = location_usage.sort_values('energy_consumed', ascending=False)
            
            # Calculate percentage
            total = location_usage['energy_consumed'].sum()
            if total > 0:
                location_usage['percentage'] = (location_usage['energy_consumed'] / total) * 100
                
                # Create bar chart
                plt.figure(figsize=(8, 4))
                bars = plt.bar(location_usage['location'], location_usage['energy_consumed'], color='lightgreen')
                plt.xlabel('Location')
                plt.ylabel('Energy Consumption (kWh)')
                plt.title('Energy Consumption by Location')
                plt.xticks(rotation=45, ha='right')
                plt.grid(True, alpha=0.3, axis='y')
                plt.tight_layout()
                
                # Add percentage labels on bars
                for bar, percentage in zip(bars, location_usage['percentage']):
                    plt.text(
                        bar.get_x() + bar.get_width()/2,
                        bar.get_height() + 0.1,
                        f"{percentage:.1f}%",
                        ha='center'
                    )
                
                # Save the plot to a BytesIO object
                img_data = BytesIO()
                plt.savefig(img_data, format='png')
                img_data.seek(0)
                plt.close()
                
                # Add the image to the PDF
                img = Image(img_data, width=6*inch, height=3*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.2 * inch))
                
                # Add insights
                top_location = location_usage.iloc[0]
                elements.append(Paragraph(
                    f"Your highest energy consumption is in the {top_location['location']} area, "
                    f"accounting for {top_location['percentage']:.1f}% of your total energy use.",
                    normal_style
                ))
            else:
                elements.append(Paragraph("No energy consumption recorded for any location.", normal_style))
        else:
            elements.append(Paragraph("Insufficient location data for analysis.", normal_style))
        
        elements.append(Spacer(1, 0.3 * inch))
    
    # Energy-saving recommendations
    elements.append(Paragraph("Energy Saving Recommendations", subtitle_style))
    
    # Generate general recommendations
    recommendations = [
        "Install LED bulbs which use up to 80% less energy than traditional incandescent bulbs.",
        "Use smart power strips to eliminate phantom energy use from devices on standby.",
        "Set your air conditioner to 24°C or higher during summer to optimize energy efficiency.",
        "Clean or replace AC filters regularly to maintain efficiency and reduce energy consumption.",
        "Use natural light when possible and turn off lights when leaving a room."
    ]
    
    # Add personalized recommendations based on data analysis
    if 'device_id' in df.columns and 'energy_consumed' in df.columns:
        device_usage = df.groupby('device_id')['energy_consumed'].sum().reset_index()
        
        if not device_usage.empty:
            device_names = get_device_names(device_usage['device_id'].unique())
            device_usage['device_name'] = device_usage['device_id'].map(device_names)
            top_device = device_usage.sort_values('energy_consumed', ascending=False).iloc[0]
            
            # Add device-specific recommendation
            if "ac" in top_device['device_id'].lower() or "air" in top_device['device_id'].lower():
                recommendations.append(
                    f"Your {top_device['device_name']} is your highest energy consumer. Consider setting the temperature "
                    f"1-2 degrees higher to save up to 10% on cooling costs."
                )
            elif "refrigerator" in top_device['device_name'].lower() or "fridge" in top_device['device_name'].lower():
                recommendations.append(
                    f"Your {top_device['device_name']} is using a significant amount of energy. Ensure the door seals are tight, "
                    f"and the temperature is set to the manufacturer's recommended level (usually 3-4°C for the fridge and -18°C for the freezer)."
                )
            elif "water" in top_device['device_name'].lower():
                recommendations.append(
                    f"Your {top_device['device_name']} is a major energy consumer. Consider lowering the temperature setting "
                    f"or installing a timer to heat water only when needed."
                )
            else:
                recommendations.append(
                    f"Your {top_device['device_name']} is your highest energy consumer. Consider upgrading to a more "
                    f"energy-efficient model or adjusting usage patterns."
                )
    
    # Add time-based recommendation based on hourly analysis
    if 'timestamp' in df.columns and 'energy_consumed' in df.columns:
        df['hour'] = df['timestamp'].dt.hour
        hourly_usage = df.groupby('hour')['energy_consumed'].sum().reset_index()
        
        if not hourly_usage.empty:
            peak_hour = hourly_usage.loc[hourly_usage['energy_consumed'].idxmax(), 'hour']
            recommendations.append(
                f"Your peak energy usage occurs around {int(peak_hour)}:00. Try to shift energy-intensive "
                f"activities to off-peak hours to reduce demand charges and overall energy costs."
            )
    
    # Add weekly pattern recommendation
    if 'timestamp' in df.columns and 'energy_consumed' in df.columns:
        df['day_of_week'] = df['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
        daily_usage = df.groupby('day_of_week')['energy_consumed'].sum().reset_index()
        
        if not daily_usage.empty:
            peak_day_num = daily_usage.loc[daily_usage['energy_consumed'].idxmax(), 'day_of_week']
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            peak_day = days[peak_day_num]
            
            recommendations.append(
                f"Your highest energy consumption is on {peak_day}. Consider rescheduling energy-intensive "
                f"activities to distribute energy usage more evenly throughout the week."
            )
    
    # Add the recommendations to the PDF
    for i, recommendation in enumerate(recommendations, 1):
        elements.append(Paragraph(f"{i}. {recommendation}", normal_style))
        elements.append(Spacer(1, 0.1 * inch))
    
    # Build the PDF
    doc.build(elements)
    
    return filename

def generate_enhanced_csv_report(
    energy_data: List[Dict], 
    user_data: Optional[Dict] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """
    Generate a comprehensive CSV report with multiple tables
    
    Args:
        energy_data (List[Dict]): Energy consumption records
        user_data (Optional[Dict]): User information for personalization
        start_date (Optional[str]): Start date for filtering data
        end_date (Optional[str]): End date for filtering data
        
    Returns:
        str: Path to the generated CSV report
    """
    # Generate report filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{REPORTS_DIR}/energy_report_{timestamp}.csv"
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(energy_data)
    
    # Ensure timestamp is datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.sort_values('timestamp', inplace=True)
    
    # Create a CSV with multiple sections
    with open(filename, 'w') as f:
        # Section 1: Summary
        f.write("ENERGY CONSUMPTION SUMMARY\n")
        f.write(f"Generated on,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if user_data and user_data.get('email'):
            f.write(f"User,{user_data.get('email')}\n")
        
        total_energy = df['energy_consumed'].sum() if 'energy_consumed' in df.columns else 0
        total_cost = calculate_tiered_cost(total_energy)
        
        f.write(f"Total Energy Consumption (kWh),{total_energy:.2f}\n")
        f.write(f"Estimated Cost (AED),{total_cost:.2f}\n")
        
        if 'timestamp' in df.columns and not df.empty:
            start_date_str = df['timestamp'].min().strftime("%Y-%m-%d")
            end_date_str = df['timestamp'].max().strftime("%Y-%m-%d")
            f.write(f"Date Range,{start_date_str} to {end_date_str}\n")
        
        f.write("\n\n")
        
        # Section 2: Daily Consumption
        f.write("DAILY ENERGY CONSUMPTION\n")
        if 'timestamp' in df.columns and 'energy_consumed' in df.columns:
            daily_data = df.groupby(pd.Grouper(key='timestamp', freq='D'))['energy_consumed'].sum().reset_index()
            daily_data['date'] = daily_data['timestamp'].dt.strftime('%Y-%m-%d')
            daily_data['change_pct'] = daily_data['energy_consumed'].pct_change() * 100
            daily_data = daily_data.fillna(0)
            
            f.write("Date,Energy (kWh),Day-over-Day Change (%),Estimated Cost (AED)\n")
            for _, row in daily_data.iterrows():
                f.write(f"{row['date']},{row['energy_consumed']:.2f},{row['change_pct']:.1f},{row['energy_consumed'] * DEFAULT_ENERGY_COST:.2f}\n")
        else:
            f.write("No daily consumption data available.\n")
        
        f.write("\n\n")
        
        # Section 3: Device Breakdown
        f.write("DEVICE ENERGY CONSUMPTION\n")
        if 'device_id' in df.columns and 'energy_consumed' in df.columns:
            device_usage = df.groupby('device_id')['energy_consumed'].sum().reset_index()
            device_names = get_device_names(device_usage['device_id'].unique())
            device_usage['device_name'] = device_usage['device_id'].map(device_names)
            
            # Calculate percentage and cost
            total = device_usage['energy_consumed'].sum()
            if total > 0:
                device_usage['percentage'] = (device_usage['energy_consumed'] / total) * 100
                device_usage['cost'] = device_usage['energy_consumed'] * DEFAULT_ENERGY_COST
                
                f.write("Device,Energy (kWh),Percentage (%),Estimated Cost (AED)\n")
                for _, row in device_usage.sort_values('energy_consumed', ascending=False).iterrows():
                    f.write(f"{row['device_name']},{row['energy_consumed']:.2f},{row['percentage']:.1f},{row['cost']:.2f}\n")
            else:
                f.write("No device consumption data available.\n")
        else:
            f.write("No device information available.\n")
        
        f.write("\n\n")
        
        # Section 4: Hourly Patterns
        f.write("HOURLY ENERGY CONSUMPTION PATTERNS\n")
        if 'timestamp' in df.columns and 'energy_consumed' in df.columns:
            df['hour'] = df['timestamp'].dt.hour
            hourly_usage = df.groupby('hour')['energy_consumed'].sum().reset_index()
            
            if not hourly_usage.empty:
                f.write("Hour,Energy (kWh),Percentage of Total (%)\n")
                total = hourly_usage['energy_consumed'].sum()
                for _, row in hourly_usage.sort_values('hour').iterrows():
                    percentage = (row['energy_consumed'] / total) * 100 if total > 0 else 0
                    f.write(f"{int(row['hour'])}:00,{row['energy_consumed']:.2f},{percentage:.1f}\n")
            else:
                f.write("No hourly pattern data available.\n")
        else:
            f.write("No timestamp information available for hourly analysis.\n")
        
        f.write("\n\n")
        
        # Section 5: Location Analysis (if available)
        if 'location' in df.columns and 'energy_consumed' in df.columns:
            f.write("LOCATION ENERGY CONSUMPTION\n")
            df_loc = df.copy()
            df_loc['location'] = df_loc['location'].fillna('Unknown')
            location_usage = df_loc.groupby('location')['energy_consumed'].sum().reset_index()
            
            if not location_usage.empty:
                total = location_usage['energy_consumed'].sum()
                if total > 0:
                    location_usage['percentage'] = (location_usage['energy_consumed'] / total) * 100
                    location_usage['cost'] = location_usage['energy_consumed'] * DEFAULT_ENERGY_COST
                    
                    f.write("Location,Energy (kWh),Percentage (%),Estimated Cost (AED)\n")
                    for _, row in location_usage.sort_values('energy_consumed', ascending=False).iterrows():
                        f.write(f"{row['location']},{row['energy_consumed']:.2f},{row['percentage']:.1f},{row['cost']:.2f}\n")
                else:
                    f.write("No location consumption data available.\n")
            else:
                f.write("No location data available.\n")
            
            f.write("\n\n")
        
        # Section 6: Raw Data
        f.write("RAW ENERGY CONSUMPTION DATA\n")
        if not df.empty:
            # Create a copy of the DataFrame for output
            output_df = df.copy()
            
            # Format timestamp for readability if it exists
            if 'timestamp' in output_df.columns:
                output_df['timestamp'] = output_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Write header
            headers = ','.join(output_df.columns)
            f.write(f"{headers}\n")
            
            # Write data rows
            for _, row in output_df.iterrows():
                f.write(','.join([str(value) for value in row.values]) + '\n')
        else:
            f.write("No raw data available.\n")
    
    return filename

def generate_enhanced_report(
    energy_data: List[Dict], 
    format: str = 'pdf',
    user_data: Optional[Dict] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """
    Generate an enhanced energy report in the specified format
    
    Args:
        energy_data (List[Dict]): Energy consumption records
        format (str): Report format ('pdf' or 'csv')
        user_data (Optional[Dict]): User information for personalization
        start_date (Optional[str]): Start date for filtering data
        end_date (Optional[str]): End date for filtering data
        
    Returns:
        str: Path to the generated report
    """
    if format.lower() == 'csv':
        return generate_enhanced_csv_report(energy_data, user_data, start_date, end_date)
    else:
        return generate_enhanced_pdf_report(energy_data, user_data, start_date, end_date)
