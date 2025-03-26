"""
A module for generating modern, professional energy reports with visualizations and analytics.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib
from matplotlib.colors import LinearSegmentedColormap
matplotlib.use('Agg')  # Use non-interactive backend
from datetime import datetime, timedelta
import uuid
import matplotlib.patches as mpatches
from matplotlib.ticker import MaxNLocator

# Try to import scikit-learn and statsmodels for advanced analytics
try:
    from sklearn.ensemble import IsolationForest
    from statsmodels.tsa.arima.model import ARIMA
    ADVANCED_ANALYTICS_AVAILABLE = True
except ImportError:
    ADVANCED_ANALYTICS_AVAILABLE = False

# Create reports directory if it doesn't exist
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# Set up modern color scheme
PRIMARY_COLOR = '#2C3E50'  # Dark blue-gray
SECONDARY_COLOR = '#3498DB'  # Bright blue
ACCENT_COLOR = '#E74C3C'  # Red
NEUTRAL_COLOR = '#ECF0F1'  # Light gray
MUTED_COLOR = '#95A5A6'  # Medium gray
SUCCESS_COLOR = '#2ECC71'  # Green

# Create a custom colormap for pie charts and other visualizations
COLORS = ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6', '#1abc9c', '#d35400', '#34495e']

# Set global matplotlib parameters for a more modern look
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 10,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 18,
    'figure.figsize': (8.27, 11.69),  # A4 size in inches
    'figure.facecolor': 'white',
    'figure.dpi': 100,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.5
})

def generate_energy_report(energy_data, user_data=None, format="pdf", start_date=None, end_date=None):
    """
    Generate a comprehensive energy usage report with modern design.
    
    Args:
        energy_data (list): List of dictionaries containing energy usage data
        user_data (dict): Dictionary containing user information
        format (str): Report format ('pdf' or 'csv')
        start_date (str): Start date for the report period
        end_date (str): End date for the report period
        
    Returns:
        str: Path to the generated report file
    """
    try:
        # Generate report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_id = str(uuid.uuid4())[:8]
        filename = f"{REPORTS_DIR}/energy_report_{timestamp}_{report_id}.{format}"
        
        # If CSV format is requested, generate a simple CSV
        if format.lower() == "csv":
            return generate_csv_report(energy_data, filename)
        
        # For PDF format, generate a comprehensive report
        print(f"Generating modern PDF report: {filename}")
        return generate_pdf_report(energy_data, user_data, filename, start_date, end_date)
    except Exception as e:
        print(f"Error generating energy report: {str(e)}")
        return None

def generate_csv_report(energy_data, filename):
    """Generate a CSV report with energy usage data."""
    try:
        df = pd.DataFrame(energy_data)
        df.to_csv(filename, index=False)
        return filename
    except Exception as e:
        print(f"Error generating CSV report: {str(e)}")
        return None

def generate_pdf_report(energy_data, user_data, filename, start_date, end_date):
    """Generate a comprehensive PDF report with modern visualizations."""
    try:
        # Convert energy data to DataFrame for easier analysis
        df = prepare_data(energy_data)
        
        # Apply modern style
        with plt.style.context('seaborn-v0_8-whitegrid'):
            # Initialize the PDF with matplotlib
            with PdfPages(filename) as pdf:
                # Title page and summary
                create_title_page(pdf, user_data, df, start_date, end_date)
                
                # Energy consumption trends
                create_trends_page(pdf, df)
                
                # Device breakdown
                create_device_breakdown_page(pdf, df)
                
                # Usage patterns
                create_usage_patterns_page(pdf, df)
                
                # Anomaly detection
                create_anomaly_detection_page(pdf, df)
                
                # Forecast
                create_forecast_page(pdf, df)
                
                # Recommendations
                create_recommendations_page(pdf, df)
        
        return filename
    except Exception as e:
        print(f"Error generating PDF report: {str(e)}")
        return None

def prepare_data(energy_data):
    """Convert raw energy data to DataFrame and perform initial processing."""
    # Convert to DataFrame
    df = pd.DataFrame(energy_data)
    
    # Convert timestamp strings to datetime objects
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Extract date and hour for analysis
        df['date'] = df['timestamp'].dt.date
        df['hour'] = df['timestamp'].dt.hour
    
    return df

def create_title_page(pdf, user_data, df, start_date, end_date):
    """Create the title page with report summary."""
    # Set up the figure with modern styling
    fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
    fig.subplots_adjust(top=0.85, bottom=0.15, left=0.15, right=0.85)
    
    # Create grid for layout
    gs = gridspec.GridSpec(3, 1, height_ratios=[1, 1, 1])
    
    # Add title and date section
    ax_title = fig.add_subplot(gs[0])
    ax_title.axis('off')
    
    # Title with blue styling
    ax_title.text(0.5, 0.7, "SYNC Energy Consumption Report", 
             fontsize=28, ha='center', weight='bold', color=PRIMARY_COLOR,
             bbox=dict(facecolor='white', edgecolor=SECONDARY_COLOR, boxstyle='round,pad=0.5', alpha=0.1))
    
    # Generated date
    ax_title.text(0.5, 0.45, f"Generated on {datetime.now().strftime('%B %d, %Y')}", 
             fontsize=12, ha='center', color=MUTED_COLOR)
    
    # User info if available
    if user_data and user_data.get('username'):
        ax_title.text(0.5, 0.3, f"Report for: {user_data.get('username')}", 
                 fontsize=14, ha='center', weight='bold', color=PRIMARY_COLOR)
    
    # Summary section with modern table
    ax_summary = fig.add_subplot(gs[1])
    ax_summary.axis('off')
    ax_summary.text(0.5, 0.9, "Summary", fontsize=20, ha='center', weight='bold', color=PRIMARY_COLOR)
    
    # Calculate key metrics
    total_energy = df['energy_consumed'].sum() if 'energy_consumed' in df.columns else 0
    rate_per_kwh = 0.23  # Example rate in AED
    total_cost = total_energy * rate_per_kwh
    
    # Create summary table with modern styling
    summary_data = [
        ['Total Energy Consumption', f"{total_energy:.2f} kWh"],
        ['Estimated Cost', f"{total_cost:.2f} AED"],
        ['Date Range', f"{start_date} to {end_date}" if start_date and end_date else "All available data"]
    ]
    
    # Plot summary table with modern styling
    table = ax_summary.table(
        cellText=summary_data,
        loc='center',
        cellLoc='center',
        colWidths=[0.3, 0.3],
        bbox=[0.15, 0.1, 0.7, 0.6]
    )
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.5)
    
    # Apply modern styling to table cells
    for (row, col), cell in table.get_celld().items():
        if row == 0:  # Header row
            cell.set_text_props(weight='bold', color=PRIMARY_COLOR)
        cell.set_edgecolor(SECONDARY_COLOR)
        cell.set_facecolor(NEUTRAL_COLOR if row % 2 == 0 else 'white')
        cell.set_alpha(0.8)
    
    # Add a section at the bottom for branding or additional info
    ax_footer = fig.add_subplot(gs[2])
    ax_footer.axis('off')
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def create_trends_page(pdf, df):
    """Create the energy consumption trends page with modern styling."""
    if 'timestamp' not in df.columns or 'energy_consumed' not in df.columns or len(df) < 2:
        # Skip if required data is not available
        return
    
    # Aggregate by date for the trend analysis
    daily_df = df.groupby(df['timestamp'].dt.date)['energy_consumed'].sum().reset_index()
    daily_df.columns = ['date', 'energy']
    
    # Calculate daily changes
    daily_df['pct_change'] = daily_df['energy'].pct_change() * 100
    avg_change = daily_df['pct_change'].dropna().mean() if len(daily_df) > 1 else float('inf')
    recent_change = daily_df['pct_change'].iloc[-1] if len(daily_df) > 1 else 0
    
    # Create figure with modern styling
    fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
    fig.subplots_adjust(top=0.9, bottom=0.15, left=0.15, right=0.85)
    
    # Title section
    plt.suptitle("Energy Consumption Trends", fontsize=24, y=0.98, color=PRIMARY_COLOR, weight='bold')
    
    # Set up grid for layout
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 3])
    
    # Empty plot for spacing
    ax_space = fig.add_subplot(gs[0])
    ax_space.axis('off')
    
    # Daily consumption plot with enhanced styling
    ax_trend = fig.add_subplot(gs[1])
    line = ax_trend.plot(
        daily_df['date'], 
        daily_df['energy'], 
        marker='o', 
        linestyle='-', 
        color=SECONDARY_COLOR,
        linewidth=2,
        markersize=6,
        markerfacecolor='white',
        markeredgecolor=SECONDARY_COLOR,
        markeredgewidth=2
    )
    
    # Add shaded background for visibility
    ax_trend.fill_between(
        daily_df['date'], 
        0, 
        daily_df['energy'], 
        color=SECONDARY_COLOR, 
        alpha=0.1
    )
    
    # Style the plot
    ax_trend.set_title('Daily Energy Consumption', fontsize=16, color=PRIMARY_COLOR, pad=20)
    ax_trend.set_xlabel('Date', fontsize=12, color=MUTED_COLOR, labelpad=10)
    ax_trend.set_ylabel('Energy (kWh)', fontsize=12, color=MUTED_COLOR, labelpad=10)
    
    # Clean up the axes
    ax_trend.spines['top'].set_visible(False)
    ax_trend.spines['right'].set_visible(False)
    ax_trend.spines['left'].set_color(MUTED_COLOR)
    ax_trend.spines['bottom'].set_color(MUTED_COLOR)
    
    # Add grid for better readability
    ax_trend.grid(True, linestyle='--', alpha=0.7, color=MUTED_COLOR)
    ax_trend.set_axisbelow(True)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Add text about changes with enhanced styling
    plt.figtext(
        0.5, 0.05, 
        f"Your average daily change in energy consumption is {avg_change:.1f}%. Your most recent change was {recent_change:.1f}%.",
        ha='center', fontsize=11, color=PRIMARY_COLOR,
        bbox=dict(facecolor=NEUTRAL_COLOR, edgecolor=SECONDARY_COLOR, boxstyle='round,pad=0.5')
    )
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def create_device_breakdown_page(pdf, df):
    """Create the device energy consumption breakdown page with modern styling."""
    if 'device_id' not in df.columns or 'energy_consumed' not in df.columns:
        # Skip if required data is not available
        return
    
    # Aggregate by device
    device_df = df.groupby('device_id')['energy_consumed'].sum().reset_index()
    device_df.columns = ['device', 'energy']
    device_df = device_df.sort_values('energy', ascending=False)
    
    # Calculate percentages and cost
    total_energy = device_df['energy'].sum()
    device_df['percentage'] = (device_df['energy'] / total_energy * 100)
    rate_per_kwh = 0.23  # Example rate in AED
    device_df['cost'] = device_df['energy'] * rate_per_kwh
    
    # Create figure for pie chart with modern styling
    fig1 = plt.figure(figsize=(8.27, 11.69), facecolor='white')
    fig1.subplots_adjust(top=0.9, bottom=0.15, left=0.15, right=0.85)
    
    # Title section
    plt.suptitle("Energy Consumption by Device", fontsize=24, y=0.98, color=PRIMARY_COLOR, weight='bold')
    
    # Create layout grid
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 3])
    
    # Placeholder for spacing
    ax_space = fig1.add_subplot(gs[0])
    ax_space.axis('off')
    
    # Pie chart with modern colors
    ax_pie = fig1.add_subplot(gs[1])
    
    # Only show top 6 devices in pie chart to avoid clutter
    top_devices = device_df.head(6)
    if len(device_df) > 6:
        # Add an "Other" category for remaining devices
        others = pd.DataFrame([{
            'device': 'Other',
            'energy': device_df.iloc[6:]['energy'].sum(),
            'percentage': device_df.iloc[6:]['percentage'].sum(),
            'cost': device_df.iloc[6:]['cost'].sum()
        }])
        top_devices = pd.concat([top_devices, others])
    
    # Create the pie chart with modern styling
    wedges, texts, autotexts = ax_pie.pie(
        top_devices['energy'], 
        labels=None,  # We'll add a legend instead
        autopct='%1.1f%%',
        startangle=90, 
        shadow=False, 
        explode=[0.05 if i == 0 else 0 for i in range(len(top_devices))],
        colors=COLORS[:len(top_devices)],
        wedgeprops=dict(width=0.5, edgecolor='white'),
        textprops={'color': PRIMARY_COLOR, 'fontweight': 'bold'}
    )
    
    # Style the percentages
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
    
    # Add device labels as a legend
    ax_pie.legend(
        wedges, 
        top_devices['device'], 
        title="Devices",
        loc="center left", 
        bbox_to_anchor=(1, 0.5),
        frameon=False,
        title_fontsize=12,
        fontsize=10
    )
    
    ax_pie.set_title('Distribution of Energy Consumption', fontsize=16, color=PRIMARY_COLOR, pad=20)
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax_pie.set_aspect('equal')
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0, 0.85, 0.95])
    
    pdf.savefig(fig1, bbox_inches='tight')
    plt.close(fig1)
    
    # Create figure for device table with modern styling
    fig2 = plt.figure(figsize=(8.27, 11.69), facecolor='white')
    plt.subplots_adjust(top=0.9, bottom=0.15, left=0.15, right=0.85)
    
    # Set up the table data
    table_data = []
    for _, row in device_df.iterrows():
        table_data.append([
            row['device'], 
            f"{row['energy']:.2f}", 
            f"{row['percentage']:.1f}%", 
            f"${row['cost']:.2f}"
        ])
    
    # Create the table with modern styling
    ax_table = plt.gca()
    ax_table.axis('off')
    
    table = ax_table.table(
        cellText=table_data, 
        colLabels=['Device', 'Energy (kWh)', 'Percentage', 'Cost ($)'],
        loc='center', 
        cellLoc='center',
        bbox=[0.15, 0.15, 0.7, 0.7]
    )
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    
    # Apply modern styling to table cells
    for (row, col), cell in table.get_celld().items():
        if row == 0:  # Header row
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor(PRIMARY_COLOR)
        else:
            cell.set_text_props(color=PRIMARY_COLOR)
            cell.set_facecolor(NEUTRAL_COLOR if row % 2 == 0 else 'white')
        
        cell.set_edgecolor(MUTED_COLOR)
        cell.set_alpha(0.8)
    
    pdf.savefig(fig2, bbox_inches='tight')
    plt.close(fig2)

def create_usage_patterns_page(pdf, df):
    """Create the usage patterns page with hourly breakdown using modern styling."""
    if 'timestamp' not in df.columns or 'energy_consumed' not in df.columns:
        # Skip if required data is not available
        return
    
    # Extract hour if not already present
    if 'hour' not in df.columns:
        df['hour'] = df['timestamp'].dt.hour
    
    # Aggregate by hour
    hourly_df = df.groupby('hour')['energy_consumed'].sum().reset_index()
    
    # Find peak hours (top 3)
    peak_hours = hourly_df.sort_values('energy_consumed', ascending=False)['hour'].head(3).tolist()
    
    # Create figure with modern styling
    fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
    fig.subplots_adjust(top=0.9, bottom=0.15, left=0.15, right=0.85)
    
    # Title section
    plt.suptitle("Usage Patterns", fontsize=24, y=0.98, color=PRIMARY_COLOR, weight='bold')
    
    # Create grid for layout
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 3])
    
    # Empty plot for spacing
    ax_space = fig.add_subplot(gs[0])
    ax_space.axis('off')
    
    # Hourly consumption bar chart with enhanced styling
    ax_hours = fig.add_subplot(gs[1])
    
    # Create bars with gradient color
    bars = ax_hours.bar(
        hourly_df['hour'], 
        hourly_df['energy_consumed'], 
        color=SECONDARY_COLOR,
        alpha=0.8,
        width=0.7,
        edgecolor='white',
        linewidth=1
    )
    
    # Highlight peak hours
    for i, hour in enumerate(hourly_df['hour']):
        if hour in peak_hours:
            bars[i].set_color(ACCENT_COLOR)
    
    # Style the plot
    ax_hours.set_title('Energy Consumption by Hour of Day', fontsize=16, color=PRIMARY_COLOR, pad=20)
    ax_hours.set_xlabel('Hour of Day', fontsize=12, color=MUTED_COLOR, labelpad=10)
    ax_hours.set_ylabel('Energy (kWh)', fontsize=12, color=MUTED_COLOR, labelpad=10)
    
    # Set the x-axis to show all hours
    ax_hours.set_xticks(range(0, 24, 2))
    ax_hours.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 2)])
    
    # Clean up the axes
    ax_hours.spines['top'].set_visible(False)
    ax_hours.spines['right'].set_visible(False)
    ax_hours.spines['left'].set_color(MUTED_COLOR)
    ax_hours.spines['bottom'].set_color(MUTED_COLOR)
    
    # Add grid for better readability
    ax_hours.grid(True, linestyle='--', alpha=0.7, color=MUTED_COLOR, axis='y')
    ax_hours.set_axisbelow(True)
    
    # Add peak hours text with enhanced styling
    peak_hours_str = ', '.join([f"{hour}:00" for hour in peak_hours])
    plt.figtext(
        0.5, 0.05, 
        f"Your peak energy usage occurs at: {peak_hours_str}",
        ha='center', fontsize=11, color=PRIMARY_COLOR,
        bbox=dict(facecolor=NEUTRAL_COLOR, edgecolor=SECONDARY_COLOR, boxstyle='round,pad=0.5')
    )
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def create_anomaly_detection_page(pdf, df):
    """Create the anomaly detection page with modern styling."""
    if 'timestamp' not in df.columns or 'energy_consumed' not in df.columns or len(df) < 10 or not ADVANCED_ANALYTICS_AVAILABLE:
        # Skip if not enough data or required libraries
        return
    
    try:
        # Prepare data for anomaly detection
        df_anomaly = df.copy()
        df_anomaly = df_anomaly[['timestamp', 'energy_consumed']].sort_values('timestamp')
        
        # Resample to regular intervals if needed
        daily_df = df_anomaly.groupby(df_anomaly['timestamp'].dt.date)['energy_consumed'].sum().reset_index()
        daily_df.columns = ['date', 'energy']
        
        # Only proceed if we have sufficient data
        if len(daily_df) >= 5:
            # Prepare data for isolation forest
            X = daily_df['energy'].values.reshape(-1, 1)
            
            # Initialize and fit the model
            isolation_forest = IsolationForest(contamination=0.1, random_state=42)
            daily_df['anomaly'] = isolation_forest.fit_predict(X)
            
            # Convert predictions to binary (0: normal, 1: anomaly)
            daily_df['anomaly'] = daily_df['anomaly'].map({1: 0, -1: 1})
            
            # Count anomalies
            anomaly_count = daily_df['anomaly'].sum()
            
            # Create figure with modern styling
            fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
            fig.subplots_adjust(top=0.9, bottom=0.15, left=0.15, right=0.85)
            
            # Title section
            plt.suptitle("Anomaly Detection", fontsize=24, y=0.98, color=PRIMARY_COLOR, weight='bold')
            
            # Create grid for layout
            gs = gridspec.GridSpec(2, 1, height_ratios=[1, 3])
            
            # Empty plot for spacing
            ax_space = fig.add_subplot(gs[0])
            ax_space.axis('off')
            
            # Anomaly plot with enhanced styling
            ax_anomaly = fig.add_subplot(gs[1])
            
            # Split normal and anomaly points
            normal = daily_df[daily_df['anomaly'] == 0]
            anomaly = daily_df[daily_df['anomaly'] == 1]
            
            # Plot normal points
            ax_anomaly.scatter(
                normal['date'], 
                normal['energy'], 
                label='Normal', 
                color=SECONDARY_COLOR,
                alpha=0.7,
                s=50,
                edgecolor='white',
                linewidth=1
            )
            
            # Plot anomalies with different style
            if not anomaly.empty:
                ax_anomaly.scatter(
                    anomaly['date'], 
                    anomaly['energy'], 
                    label='Anomaly', 
                    color=ACCENT_COLOR,
                    marker='X',
                    s=100,
                    edgecolor='white',
                    linewidth=2
                )
            
            # Style the plot
            ax_anomaly.set_title('Anomaly Detection in Energy Consumption', fontsize=16, color=PRIMARY_COLOR, pad=20)
            ax_anomaly.set_xlabel('Date', fontsize=12, color=MUTED_COLOR, labelpad=10)
            ax_anomaly.set_ylabel('Energy (kWh)', fontsize=12, color=MUTED_COLOR, labelpad=10)
            
            # Add legend with modern styling
            legend = ax_anomaly.legend(
                loc='upper right',
                frameon=True,
                fancybox=True,
                framealpha=0.8,
                fontsize=10,
                facecolor=NEUTRAL_COLOR,
                edgecolor=MUTED_COLOR
            )
            
            # Clean up the axes
            ax_anomaly.spines['top'].set_visible(False)
            ax_anomaly.spines['right'].set_visible(False)
            ax_anomaly.spines['left'].set_color(MUTED_COLOR)
            ax_anomaly.spines['bottom'].set_color(MUTED_COLOR)
            
            # Add grid for better readability
            ax_anomaly.grid(True, linestyle='--', alpha=0.7, color=MUTED_COLOR)
            ax_anomaly.set_axisbelow(True)
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)
            
            # Add text about anomalies with enhanced styling
            plt.figtext(
                0.5, 0.05, 
                f"We detected {anomaly_count} anomalies in your energy consumption.",
                ha='center', fontsize=11, color=PRIMARY_COLOR,
                bbox=dict(facecolor=NEUTRAL_COLOR, edgecolor=SECONDARY_COLOR, boxstyle='round,pad=0.5')
            )
            
            # Adjust layout
            plt.tight_layout(rect=[0, 0.05, 1, 0.95])
            
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
    except Exception as e:
        print(f"Error in anomaly detection: {str(e)}")

def create_forecast_page(pdf, df):
    """Create the energy consumption forecast page with modern styling."""
    if 'timestamp' not in df.columns or 'energy_consumed' not in df.columns or len(df) < 7:
        # Skip if not enough data
        return
    
    try:
        # Prepare data for forecasting
        df_forecast = df.copy()
        df_forecast = df_forecast[['timestamp', 'energy_consumed']].sort_values('timestamp')
        
        # Resample to daily data
        daily_df = df_forecast.groupby(df_forecast['timestamp'].dt.date)['energy_consumed'].sum().reset_index()
        daily_df.columns = ['date', 'energy']
        
        # Only proceed if we have sufficient data
        if len(daily_df) >= 7:
            # Simple forecasting approach: average of last week
            forecast_days = 7
            forecast_value = daily_df['energy'].tail(7).mean()
            forecast_total = forecast_value * forecast_days
            
            # Create date range for forecast
            last_date = daily_df['date'].max()
            forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
            
            # Create figure with modern styling
            fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
            fig.subplots_adjust(top=0.9, bottom=0.15, left=0.15, right=0.85)
            
            # Title section
            plt.suptitle("Energy Consumption Forecast", fontsize=24, y=0.98, color=PRIMARY_COLOR, weight='bold')
            
            # Create grid for layout
            gs = gridspec.GridSpec(2, 1, height_ratios=[1, 3])
            
            # Empty plot for spacing
            ax_space = fig.add_subplot(gs[0])
            ax_space.axis('off')
            
            # Forecast plot with enhanced styling
            ax_forecast = fig.add_subplot(gs[1])
            
            # Plot historical data
            ax_forecast.plot(
                daily_df['date'], 
                daily_df['energy'], 
                '-', 
                color=SECONDARY_COLOR,
                linewidth=2,
                label='Historical',
                marker='o',
                markersize=5,
                markerfacecolor='white',
                markeredgecolor=SECONDARY_COLOR,
                markeredgewidth=1
            )
            
            # Add shaded area for historical data
            ax_forecast.fill_between(
                daily_df['date'],
                0,
                daily_df['energy'],
                color=SECONDARY_COLOR,
                alpha=0.1
            )
            
            # Plot forecast data
            ax_forecast.plot(
                forecast_dates, 
                [forecast_value] * forecast_days, 
                '--', 
                color=ACCENT_COLOR,
                linewidth=2,
                label='Forecast',
                marker='s',
                markersize=5,
                markerfacecolor='white',
                markeredgecolor=ACCENT_COLOR,
                markeredgewidth=1
            )
            
            # Add shaded area for forecast data
            ax_forecast.fill_between(
                forecast_dates,
                0,
                [forecast_value] * forecast_days,
                color=ACCENT_COLOR,
                alpha=0.1
            )
            
            # Style the plot
            ax_forecast.set_title('7-Day Energy Consumption Forecast', fontsize=16, color=PRIMARY_COLOR, pad=20)
            ax_forecast.set_xlabel('Date', fontsize=12, color=MUTED_COLOR, labelpad=10)
            ax_forecast.set_ylabel('Energy (kWh)', fontsize=12, color=MUTED_COLOR, labelpad=10)
            
            # Add legend with modern styling
            legend = ax_forecast.legend(
                loc='upper right',
                frameon=True,
                fancybox=True,
                framealpha=0.8,
                fontsize=10,
                facecolor=NEUTRAL_COLOR,
                edgecolor=MUTED_COLOR
            )
            
            # Clean up the axes
            ax_forecast.spines['top'].set_visible(False)
            ax_forecast.spines['right'].set_visible(False)
            ax_forecast.spines['left'].set_color(MUTED_COLOR)
            ax_forecast.spines['bottom'].set_color(MUTED_COLOR)
            
            # Add grid for better readability
            ax_forecast.grid(True, linestyle='--', alpha=0.7, color=MUTED_COLOR)
            ax_forecast.set_axisbelow(True)
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)
            
            # Calculate cost
            rate_per_kwh = 0.23  # Example rate in AED
            forecast_cost = forecast_total * rate_per_kwh
            
            # Add text about forecast with enhanced styling
            plt.figtext(
                0.5, 0.05, 
                f"Forecasted energy consumption for the next 7 days: {forecast_total:.2f} kWh. Estimated cost: ${forecast_cost:.2f}.",
                ha='center', fontsize=11, color=PRIMARY_COLOR,
                bbox=dict(facecolor=NEUTRAL_COLOR, edgecolor=SECONDARY_COLOR, boxstyle='round,pad=0.5')
            )
            
            # Adjust layout
            plt.tight_layout(rect=[0, 0.05, 1, 0.95])
            
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
    except Exception as e:
        print(f"Error in forecasting: {str(e)}")

def create_recommendations_page(pdf, df):
    """Create the energy saving recommendations page with modern styling."""
    # Default recommendations
    recommendations = [
        "Consider using smart power strips to eliminate phantom energy use from devices on standby.",
        "Replace high-energy appliances with energy-efficient models (look for ENERGY STAR ratings).",
        "Install a programmable thermostat to optimize heating and cooling.",
        "Use natural light when possible and replace incandescent bulbs with LEDs.",
        "Ensure proper insulation in your home to reduce heating and cooling costs."
    ]
    
    # Add personalized recommendations if data is available
    if 'device_id' in df.columns and 'energy_consumed' in df.columns:
        try:
            # Device with highest consumption
            device_df = df.groupby('device_id')['energy_consumed'].sum().reset_index()
            top_device = device_df.sort_values('energy_consumed', ascending=False).iloc[0]
            total_energy = device_df['energy_consumed'].sum()
            top_percentage = (top_device['energy_consumed'] / total_energy * 100) if total_energy > 0 else 0
            
            if top_percentage > 5:
                recommendations.append(
                    f"Your {top_device['device_id']} consumes {top_percentage:.1f}% of your energy. "
                    "Consider upgrading to a more efficient model or adjusting usage patterns."
                )
            
            # Peak usage hour
            if 'hour' in df.columns:
                hourly_df = df.groupby('hour')['energy_consumed'].sum().reset_index()
                peak_hour = hourly_df.loc[hourly_df['energy_consumed'].idxmax(), 'hour']
                recommendations.append(
                    f"Your peak energy usage occurs around {peak_hour}:00. "
                    "Consider shifting energy-intensive activities to off-peak hours."
                )
        except Exception as e:
            print(f"Error generating personalized recommendations: {str(e)}")
    
    # Create figure with modern styling
    fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
    fig.subplots_adjust(top=0.9, bottom=0.15, left=0.15, right=0.85)
    
    # Title section
    plt.suptitle("Energy Saving Recommendations", fontsize=24, y=0.98, color=PRIMARY_COLOR, weight='bold')
    
    # Create an axis for the recommendations
    ax = plt.gca()
    ax.axis('off')
    
    # Display recommendations with icons and enhanced styling
    y_pos = 0.85
    icons = ['💡', '⚡', '🌡️', '☀️', '🏠', '📊', '⏰']
    
    for i, rec in enumerate(recommendations):
        icon = icons[i % len(icons)]
        text = plt.text(
            0.1, y_pos, 
            f"{icon} {rec}", 
            fontsize=12, 
            wrap=True, 
            transform=ax.transAxes,
            bbox=dict(
                facecolor=NEUTRAL_COLOR if i % 2 == 0 else 'white',
                edgecolor=MUTED_COLOR,
                boxstyle='round,pad=0.5',
                alpha=0.8
            )
        )
        
        # Manually wrap text by adjusting y_pos
        text_size = text.get_window_extent().height
        y_pos -= text_size / fig.get_window_extent().height + 0.04
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)
