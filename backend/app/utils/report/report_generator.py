"""
This module provides report generation feature & functionality
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from statsmodels.tsa.arima.model import ARIMA
from io import BytesIO

# Ensure that the reports directory exists
# REPORTS_DIR = os.path.join(os.path.dirname(__file__), "generated_reports")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "generated_reports")
os.makedirs(REPORTS_DIR, exist_ok = True)

# Average electricity cost per kWh
# NOTE: 0.23 AED/kWh till 2'000 AED; 0.28 AED/kWh till 4'000 AED; 0.32 AED/kWh till 6'000 AED; 0.36 AED/kWh from 6'000 AED
DEFAULT_ENERGY_COST = 0.23  # AED per kWh

class EnergyReportGenerator:
    """
    Enhanced energy report generator with advanced analytics and visualizations
    """
    
    def __init__(self, energy_data: List[Dict], user_data: Optional[Dict] = None):
        """
        Initialize the report generator with energy consumption data
        
        Args:
            energy_data (List[Dict]): Energy consumption records
            user_data (Optional[Dict]): User information for personalization
        """
        # Convert data to pandas DataFrame for easier analysis
        self.df = pd.DataFrame(energy_data)
        
        # Ensure timestamp is datetime
        if 'timestamp' in self.df.columns:
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df.sort_values('timestamp', inplace=True)
        
        self.user_data = user_data or {}
        self.device_names = self._get_device_names()
        
    def _get_device_names(self) -> Dict[str, str]:
        """
        Map device IDs to more readable names
        This would ideally pull from a devices collection
        
        Returns:
            Dict[str, str]: Mapping of device_id to readable name
        """
        # This is a placeholder - in production, you would query the database
        # to get actual device names based on the device_ids in the energy data
        
        device_ids = self.df['device_id'].unique() if 'device_id' in self.df.columns else []
        
        # Create a mapping of device_id to readable names
        # In production, this would come from the devices collection
        return {device_id: f"Device {i+1}" for i, device_id in enumerate(device_ids)}
    
    def calculate_total_energy_usage(self) -> float:
        """
        Calculate the total energy consumption in kWh
        
        Returns:
            float: Total energy consumption
        """
        if 'energy_consumed' in self.df.columns:
            return float(self.df['energy_consumed'].sum())
        return 0.0
    
    def calculate_total_cost(self, cost_per_kwh: float = DEFAULT_ENERGY_COST) -> float:
        """
        Calculate the total cost based on energy consumption
        
        Args:
            cost_per_kwh (float): Cost per kWh in local currency
            
        Returns:
            float: Total estimated cost
        """
        total_energy = self.calculate_total_energy_usage()
        return total_energy * cost_per_kwh
    
    def analyze_trends(self, interval: str = 'day') -> pd.DataFrame:
        """
        Analyze energy consumption trends over time
        
        Args:
            interval (str): Time grouping interval ('hour', 'day', 'week', 'month')
            
        Returns:
            pd.DataFrame: Aggregated energy consumption by time period
        """
        if 'timestamp' not in self.df.columns or 'energy_consumed' not in self.df.columns:
            return pd.DataFrame()
            
        # Group by the specified time interval
        if interval == 'hour':
            grouper = pd.Grouper(key='timestamp', freq='H')
        elif interval == 'day':
            grouper = pd.Grouper(key='timestamp', freq='D')
        elif interval == 'week':
            grouper = pd.Grouper(key='timestamp', freq='W')
        elif interval == 'month':
            grouper = pd.Grouper(key='timestamp', freq='M')
        else:
            grouper = pd.Grouper(key='timestamp', freq='D')  # Default to daily
            
        # Aggregate by the interval
        trends = self.df.groupby(grouper)['energy_consumed'].sum().reset_index()
        trends.columns = ['period', 'energy_consumed']
        
        # Calculate the percentage change between consecutive periods
        trends['change_pct'] = trends['energy_consumed'].pct_change() * 100
        
        return trends
    
    def analyze_by_device(self) -> pd.DataFrame:
        """
        Analyze energy consumption by device
        
        Returns:
            pd.DataFrame: Energy consumption aggregated by device
        """
        if 'device_id' not in self.df.columns or 'energy_consumed' not in self.df.columns:
            return pd.DataFrame()
            
        # Group by device_id
        device_usage = self.df.groupby('device_id')['energy_consumed'].sum().reset_index()
        
        # Add readable device names
        # FIX:
        device_usage['device_name'] = device_usage['device_id'].map(self.device_names)
        
        # Calculate percentage of total
        total = device_usage['energy_consumed'].sum()
        if total > 0:
            device_usage['percentage'] = (device_usage['energy_consumed'] / total) * 100
        else:
            device_usage['percentage'] = 0
            
        return device_usage
    
    def analyze_by_location(self) -> pd.DataFrame:
        """
        Analyze energy consumption by location
        
        Returns:
            pd.DataFrame: Energy consumption aggregated by location
        """
        if 'location' not in self.df.columns or 'energy_consumed' not in self.df.columns:
            return pd.DataFrame()
            
        # Fill missing locations
        location_df = self.df.copy()
        location_df['location'] = location_df['location'].fillna('Unknown')
            
        # Group by location
        location_usage = location_df.groupby('location')['energy_consumed'].sum().reset_index()
        
        # Calculate percentage of total
        total = location_usage['energy_consumed'].sum()
        if total > 0:
            location_usage['percentage'] = (location_usage['energy_consumed'] / total) * 100
        else:
            location_usage['percentage'] = 0
            
        return location_usage
    
    def identify_peak_usage_times(self) -> pd.DataFrame:
        """
        Identify peak energy usage times
        
        Returns:
            pd.DataFrame: Hours of the day ranked by energy consumption
        """
        if 'timestamp' not in self.df.columns or 'energy_consumed' not in self.df.columns:
            return pd.DataFrame()
            
        # Extract hour from timestamp
        hour_df = self.df.copy()
        hour_df['hour'] = hour_df['timestamp'].dt.hour
        
        # Group by hour
        hourly_usage = hour_df.groupby('hour')['energy_consumed'].sum().reset_index()
        
        # Sort by energy consumption (descending)
        hourly_usage.sort_values('energy_consumed', ascending=False, inplace=True)
        
        return hourly_usage
    
    def detect_anomalies(self) -> Tuple[pd.DataFrame, float]:
        """
        Detect anomalies in energy consumption using Isolation Forest
        
        Returns:
            Tuple[pd.DataFrame, float]: DataFrame with anomaly scores and anomaly threshold
        """
        if len(self.df) < 10 or 'energy_consumed' not in self.df.columns:
            return pd.DataFrame(), 0.0
            
        try:
            # Prepare data for anomaly detection
            data = self.df[['energy_consumed']].copy()
            
            # Standardize the data
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(data)
            
            # Use Isolation Forest for anomaly detection
            # FIX:
            model = IsolationForest(contamination=0.05, random_state=42)
            data['anomaly_score'] = model.fit_predict(scaled_data)
            
            # Convert to anomaly score (higher is more anomalous)
            # FIX:
            data['anomaly_score'] = data['anomaly_score'].map({1: 0, -1: 1})
            
            # Add timestamp
            data['timestamp'] = self.df['timestamp']
            
            # Get the anomaly threshold (for plotting)
            anomaly_threshold = data[data['anomaly_score'] > 0]['energy_consumed'].min()
            
            # FIX:
            return data, anomaly_threshold
        except Exception as e:
            print(f"Error in anomaly detection: {e}")
            return pd.DataFrame(), 0.0
    
    def forecast_future_usage(self, days_ahead: int = 7) -> pd.DataFrame:
        """
        Forecast future energy consumption using ARIMA
        
        Args:
            days_ahead (int): Number of days to forecast
            
        Returns:
            pd.DataFrame: Forecasted energy consumption
        """
        if len(self.df) < 14 or 'timestamp' not in self.df.columns or 'energy_consumed' not in self.df.columns:
            return pd.DataFrame()
            
        try:
            # Prepare data for forecasting
            # Group by day to reduce noise
            daily_data = self.df.groupby(pd.Grouper(key='timestamp', freq='D'))['energy_consumed'].sum()
            
            # Ensure we have enough data points
            if len(daily_data) < 7:
                return pd.DataFrame()
                
            # Fit ARIMA model
            # Using a simple model for demonstration; would need tuning in production
            # FIX:
            model = ARIMA(daily_data, order=(1, 1, 1))
            model_fit = model.fit()
            
            # Generate forecast
            forecast = model_fit.forecast(steps=days_ahead)
            
            # Create forecasted dates
            last_date = daily_data.index[-1]
            # FIX:
            forecast_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
            
            # Create result DataFrame
            forecast_df = pd.DataFrame({
                'timestamp': forecast_dates,
                'forecasted_energy': forecast.values,
                'type': 'forecast'
            })
            
            # Add the historical data
            historical_df = pd.DataFrame({
                'timestamp': daily_data.index,
                'forecasted_energy': daily_data.values,
                'type': 'historical'
            })
            
            # Combine historical and forecast
            result = pd.concat([historical_df, forecast_df])
            
            return result
            
        except Exception as e:
            print(f"Error in forecasting: {e}")
            return pd.DataFrame()
    
    def generate_energy_saving_tips(self) -> List[str]:
        """
        Generate personalized energy-saving tips based on usage patterns
        
        Returns:
            List[str]: Energy-saving recommendations
        """
        tips = [
            "Consider using smart power strips to eliminate phantom energy use from devices on standby.",
            "Replace high-energy appliances with energy-efficient models (look for ENERGY STAR ratings).",
            "Install a programmable thermostat to optimize heating and cooling.",
            "Use natural light when possible and replace incandescent bulbs with LEDs.",
            "Ensure proper insulation in your home to reduce heating and cooling costs."
        ]
        
        # Add personalized tips based on patterns in the data
        device_usage = self.analyze_by_device()
        if not device_usage.empty:
            # Identify the device with highest energy consumption
            top_device = device_usage.iloc[0]
            tips.append(f"Your {top_device['device_name']} consumes {top_device['percentage']:.1f}% of your energy. "
                        f"Consider upgrading to a more efficient model or adjusting usage patterns.")
        
        # Add tips based on peak hours
        peak_hours = self.identify_peak_usage_times()
        if not peak_hours.empty and len(peak_hours) > 0:
            top_hour = peak_hours.iloc[0]['hour']
            tips.append(f"Your peak energy usage occurs around {top_hour}:00. "
                        f"Consider shifting energy-intensive activities to off-peak hours.")
        
        return tips
    
    def create_pdf_report(self) -> str:
        """
        Generate a comprehensive PDF report with visualizations
        
        Returns:
            str: Path to the generated PDF report
        """
        # Generate report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{REPORTS_DIR}/energy_report_{timestamp}.pdf"
        
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
        elements.append(Paragraph("Energy Consumption Report", title_style))
        elements.append(Spacer(1, 0.2 * inch))
        
        report_date = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(f"Generated on {report_date}", normal_style))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Summary section
        elements.append(Paragraph("Summary", subtitle_style))
        
        total_energy = self.calculate_total_energy_usage()
        total_cost = self.calculate_total_cost()
        
        summary_data = [
            ["Total Energy Consumption", f"{total_energy:.2f} kWh"],
            ["Estimated Cost", f"{total_cost:.2f} AED"],
        ]
        
        # Add date range if available
        if 'timestamp' in self.df.columns and not self.df.empty:
            start_date = self.df['timestamp'].min().strftime("%Y-%m-%d")
            end_date = self.df['timestamp'].max().strftime("%Y-%m-%d")
            summary_data.append(["Date Range", f"{start_date} to {end_date}"])
        
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
        
        trends = self.analyze_trends(interval='day')
        if not trends.empty and len(trends) > 1:
            # Create trend visualization
            plt.figure(figsize=(8, 4))
            plt.plot(trends['period'], trends['energy_consumed'], marker='o', linestyle='-')
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
            avg_change = trends['change_pct'].mean()
            last_change = trends['change_pct'].iloc[-1] if len(trends) > 1 else 0
            
            if not np.isnan(avg_change) and not np.isnan(last_change):
                trend_text = f"Your average daily change in energy consumption is {avg_change:.1f}%. "
                trend_text += f"Your most recent change was {last_change:.1f}%."
                elements.append(Paragraph(trend_text, normal_style))
        else:
            elements.append(Paragraph("Insufficient data to analyze trends.", normal_style))
        
        elements.append(Spacer(1, 0.3 * inch))
        
        # Device breakdown
        elements.append(Paragraph("Energy Consumption by Device", subtitle_style))
        
        device_usage = self.analyze_by_device()
        if not device_usage.empty:
            # Create device visualization
            plt.figure(figsize=(8, 4))
            
            # Sort by energy consumed
            device_usage = device_usage.sort_values('energy_consumed', ascending=False)
            
            # Use device names for better readability
            labels = device_usage['device_name'].tolist()
            sizes = device_usage['energy_consumed'].tolist()
            
            # Create pie chart
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, shadow=True)
            plt.axis('equal')
            plt.title('Energy Consumption by Device')
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
            
            # Add table with detailed breakdown
            device_table_data = [["Device", "Energy (kWh)", "Percentage", "Cost ($)"]]
            for _, row in device_usage.iterrows():
                device_table_data.append([
                    # FIX:
                    row['device_name'],
                    f"{row['energy_consumed']:.2f}",
                    f"{row['percentage']:.1f}%",
                    f"${row['energy_consumed'] * DEFAULT_ENERGY_COST:.2f}"
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
        else:
            elements.append(Paragraph("Insufficient data to analyze device usage.", normal_style))
        
        elements.append(Spacer(1, 0.3 * inch))
        
        # Add usage patterns
        elements.append(Paragraph("Usage Patterns", subtitle_style))
        
        hourly_usage = self.identify_peak_usage_times()
        if not hourly_usage.empty:
            # Create hourly pattern visualization
            plt.figure(figsize=(8, 4))
            
            # Sort by hour for better visualization
            hourly_usage = hourly_usage.sort_values('hour')
            
            plt.bar(hourly_usage['hour'], hourly_usage['energy_consumed'])
            plt.xlabel('Hour of Day')
            plt.ylabel('Energy (kWh)')
            plt.title('Energy Consumption by Hour of Day')
            plt.xticks(range(0, 24, 2))  # Show every 2 hours
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
            
            # Add peak usage insight
            top_hours = hourly_usage.sort_values('energy_consumed', ascending=False).head(3)
            peak_hours_str = ", ".join([f"{hour}:00" for hour in top_hours['hour']])
            elements.append(Paragraph(f"Your peak energy usage occurs at: {peak_hours_str}", normal_style))
        else:
            elements.append(Paragraph("Insufficient data to analyze usage patterns.", normal_style))
        
        elements.append(PageBreak())
        
        # Anomaly detection
        elements.append(Paragraph("Anomaly Detection", subtitle_style))
        
        anomaly_data, threshold = self.detect_anomalies()
        if not anomaly_data.empty and 'anomaly_score' in anomaly_data.columns:
            # Create anomaly visualization
            plt.figure(figsize=(8, 4))
            
            # Plot normal points
            normal = anomaly_data[anomaly_data['anomaly_score'] == 0]
            plt.scatter(normal['timestamp'], normal['energy_consumed'], 
                       color='blue', label='Normal', alpha=0.5)
            
            # Plot anomalies
            anomalies = anomaly_data[anomaly_data['anomaly_score'] > 0]
            plt.scatter(anomalies['timestamp'], anomalies['energy_consumed'], 
                       color='red', label='Anomaly', alpha=0.8)
            
            plt.xlabel('Date')
            plt.ylabel('Energy (kWh)')
            plt.title('Anomaly Detection in Energy Consumption')
            plt.legend()
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
            
            # Add anomaly insights
            anomaly_count = len(anomalies)
            if anomaly_count > 0:
                # FIX:
                anomaly_dates = anomalies['timestamp'].dt.strftime('%Y-%m-%d').tolist()
                anomaly_text = f"We detected {anomaly_count} anomalies in your energy consumption. "
                if anomaly_count <= 3:
                    anomaly_text += f"Unusual consumption occurred on: {', '.join(anomaly_dates)}."
                elements.append(Paragraph(anomaly_text, normal_style))
            else:
                elements.append(Paragraph("No anomalies detected in your energy consumption pattern.", normal_style))
        else:
            elements.append(Paragraph("Insufficient data to perform anomaly detection.", normal_style))
        
        elements.append(Spacer(1, 0.3 * inch))
        
        # Forecasting
        elements.append(Paragraph("Energy Consumption Forecast", subtitle_style))
        
        forecast_data = self.forecast_future_usage(days_ahead=7)
        if not forecast_data.empty:
            # Create forecast visualization
            plt.figure(figsize=(8, 4))
            
            # Plot historical data
            historical = forecast_data[forecast_data['type'] == 'historical']
            plt.plot(historical['timestamp'], historical['forecasted_energy'], 
                    'b-', label='Historical', alpha=0.7)
            
            # Plot forecasted data
            forecast = forecast_data[forecast_data['type'] == 'forecast']
            plt.plot(forecast['timestamp'], forecast['forecasted_energy'], 
                    'r--', label='Forecast', alpha=0.7)
            
            plt.xlabel('Date')
            plt.ylabel('Energy (kWh)')
            plt.title('7-Day Energy Consumption Forecast')
            plt.legend()
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
            
            # Add forecast insights
            forecasted_total = forecast['forecasted_energy'].sum()
            forecasted_cost = forecasted_total * DEFAULT_ENERGY_COST
            forecast_text = f"Forecasted energy consumption for the next 7 days: {forecasted_total:.2f} kWh. "
            forecast_text += f"Estimated cost: ${forecasted_cost:.2f}."
            elements.append(Paragraph(forecast_text, normal_style))
        else:
            elements.append(Paragraph("Insufficient data to generate forecast.", normal_style))
        
        elements.append(Spacer(1, 0.3 * inch))
        
        # Energy saving recommendations
        elements.append(Paragraph("Energy Saving Recommendations", subtitle_style))
        
        tips = self.generate_energy_saving_tips()
        for tip in tips:
            elements.append(Paragraph(f"• {tip}", normal_style))
            elements.append(Spacer(1, 0.1 * inch))
        
        # Build the PDF
        doc.build(elements)
        
        return filename
    
    def create_csv_report(self) -> str:
        """
        Generate a comprehensive CSV report with multiple sheets
        
        Returns:
            str: Path to the generated CSV (Excel) report
        """
        # Generate report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{REPORTS_DIR}/energy_report_{timestamp}.xlsx"
        
        # Create Excel writer
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            # Summary sheet
            summary_data = {
                'Metric': ['Total Energy Consumption (kWh)', 'Estimated Cost ($)'],
                'Value': [
                    f"{self.calculate_total_energy_usage():.2f}",
                    f"{self.calculate_total_cost():.2f}"
                ]
            }
            
            # Add date range if available
            if 'timestamp' in self.df.columns and not self.df.empty:
                start_date = self.df['timestamp'].min().strftime("%Y-%m-%d")
                end_date = self.df['timestamp'].max().strftime("%Y-%m-%d")
                summary_data['Metric'].append('Date Range')
                summary_data['Value'].append(f"{start_date} to {end_date}")
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Trend analysis
            trends = self.analyze_trends(interval='day')
            if not trends.empty:
                trends.to_excel(writer, sheet_name='Daily Trends', index=False)
            
            # Device breakdown
            device_usage = self.analyze_by_device()
            if not device_usage.empty:
                # Add cost column
                device_usage['estimated_cost'] = device_usage['energy_consumed'] * DEFAULT_ENERGY_COST
                device_usage.to_excel(writer, sheet_name='Device Breakdown', index=False)
            
            # Location breakdown
            location_usage = self.analyze_by_location()
            if not location_usage.empty:
                # Add cost column
                location_usage['estimated_cost'] = location_usage['energy_consumed'] * DEFAULT_ENERGY_COST
                location_usage.to_excel(writer, sheet_name='Location Breakdown', index=False)
            
            # Hourly patterns
            hourly_usage = self.identify_peak_usage_times()
            if not hourly_usage.empty:
                hourly_usage.to_excel(writer, sheet_name='Hourly Patterns', index=False)
            
            # Anomalies
            anomaly_data, _ = self.detect_anomalies()
            if not anomaly_data.empty and 'anomaly_score' in anomaly_data.columns:
                anomaly_data.to_excel(writer, sheet_name='Anomalies', index=False)
            
            # Forecast
            forecast_data = self.forecast_future_usage(days_ahead=7)
            if not forecast_data.empty:
                forecast_data.to_excel(writer, sheet_name='Forecast', index=False)
            
            # Energy saving tips
            tips = self.generate_energy_saving_tips()
            tips_df = pd.DataFrame({'Energy Saving Tips': tips})
            tips_df.to_excel(writer, sheet_name='Recommendations', index=False)
            
            # Raw data
            if not self.df.empty:
                # Format the timestamp for readability
                raw_data = self.df.copy()
                if 'timestamp' in raw_data.columns:
                    raw_data['timestamp'] = raw_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
                raw_data.to_excel(writer, sheet_name='Raw Data', index=False)
        
        return filename


# Function to generate energy report
def generate_energy_report(
    energy_data: List[Dict], 
    user_data: Optional[Dict] = None,
    format: str = 'pdf',
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """
    Generate a comprehensive energy consumption report
    
    Args:
        energy_data (List[Dict]): Energy consumption records
        user_data (Optional[Dict]): User information for personalization
        format (str): Report format ('pdf' or 'csv')
        start_date (Optional[str]): Start date filter in YYYY-MM-DD format
        end_date (Optional[str]): End date filter in YYYY-MM-DD format
        
    Returns:
        str: Path to the generated report file
    """
    # Filter data by date range if provided
    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            filtered_data = [
                record for record in energy_data 
                if start_dt <= datetime.fromisoformat(str(record['timestamp'])) <= end_dt
            ]
        except (ValueError, KeyError):
            # If there's an error in filtering, use all data
            filtered_data = energy_data
    else:
        filtered_data = energy_data
    
    # Create report generator
    report_generator = EnergyReportGenerator(filtered_data, user_data)
    
    # Generate report based on format
    if format.lower() == 'csv':
        return report_generator.create_csv_report()
    else:
        return report_generator.create_pdf_report()
