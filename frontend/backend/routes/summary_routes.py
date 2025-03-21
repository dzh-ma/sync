"""
This module defines a FastAPI router for managing energy consumption summaries. It provides endpoints 
    to generate, retrieve, list, and delete energy summaries for authenticated users.
"""
from typing import List, Optional, Dict
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from bson.objectid import ObjectId
import pandas as pd
import numpy as np

from ..models.energy_summary import EnergySummary
from ..core.security import get_current_user, role_required
from ..db.database import energy_collection, summary_collection, users_collection, get_energy_data

router = APIRouter(
    prefix="/api/v1/summaries",
    tags=["Energy Summaries"],
    responses={404: {"description": "Not found"}},
)

# Default energy cost per kWh
# NOTE: 0.23 AED/kWh till 2'000 AED; 0.28 AED/kWh till 4'000 AED; 0.32 AED/kWh till 6'000 AED; 0.36 AED/kWh from 6'000 AED
DEFAULT_ENERGY_COST = 0.23  # AED per kWh

@router.post("/generate", dependencies=[Depends(get_current_user)])
async def generate_energy_summary(
    user_id: str, 
    period: str = Query(..., enum=["daily", "weekly", "monthly"]),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Generate an energy consumption summary for the specified period
    
    Args:
        user_id (str): The user ID to generate the summary for
        period (str): The period type (daily, weekly, monthly)
        start_date (Optional[str]): Start date for the summary period (YYYY-MM-DD)
        end_date (Optional[str]): End date for the summary period (YYYY-MM-DD)
        
    Returns:
        dict: The generated energy summary
    
    Raises:
        HTTPException: If generation fails or parameters are invalid
    """
    try:
        # Validate user exists
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Set default dates if not provided
        now = datetime.now(timezone.utc)
        if not end_date:
            end_date = now.date().isoformat()
        
        if not start_date:
            if period == "monthly":
                start_date = (now - timedelta(days=30)).date().isoformat()
            elif period == "weekly":
                start_date = (now - timedelta(days=7)).date().isoformat()
            else:
                start_date = now.date().isoformat()
        
        # Parse dates
        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = datetime.fromisoformat(end_date)
        
        if start_datetime > end_datetime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before end date"
            )
        
        # Query energy data for the period
        query = {
            "timestamp": {
                "$gte": start_datetime,
                "$lte": end_datetime
            }
        }
        
        energy_data = list(energy_collection.find(query))
        
        if not energy_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No energy data available for the selected period"
            )
        
        # Calculate total consumption
        total_consumption = sum(item.get("energy_consumed", 0) for item in energy_data)
        
        # Calculate cost estimate (example rate: $0.15 per kWh)
        cost_estimate = total_consumption * 0.15
        
        # Calculate comparison to previous period
        previous_start = start_datetime - (end_datetime - start_datetime)
        previous_end = start_datetime - timedelta(days=1)
        
        previous_query = {
            "timestamp": {
                "$gte": previous_start,
                "$lte": previous_end
            }
        }
        
        previous_data = list(energy_collection.find(previous_query))
        previous_consumption = sum(item.get("energy_consumed", 0) for item in previous_data) if previous_data else 0
        
        comparison = None
        if previous_consumption > 0:
            comparison = ((total_consumption - previous_consumption) / previous_consumption) * 100
        
        # Create summary object
        summary = EnergySummary(
            user_id=user_id,
            period=period,
            start_date=start_datetime,
            end_date=end_datetime,
            total_consumption=total_consumption,
            cost_estimate=cost_estimate,
            comparison_to_previous=comparison
        )
        
        # Check if summary already exists
        existing_summary = summary_collection.find_one({
            "user_id": user_id,
            "period": period,
            "start_date": start_datetime,
        })
        
        if existing_summary:
            # Update existing summary
            summary_collection.update_one(
                {"_id": existing_summary["_id"]},
                {"$set": summary.model_dump()}
            )
            summary_id = str(existing_summary["_id"])
        else:
            # Insert new summary
            result = summary_collection.insert_one(summary.model_dump())
            summary_id = str(result.inserted_id)
        
        return {
            "message": "Energy summary generated successfully",
            "summary_id": summary_id,
            "summary": summary.model_dump()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate energy summary: {str(e)}"
        )

@router.get("/", response_model=List[EnergySummary])
async def get_energy_summaries(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    period: Optional[str] = Query(None, description="Filter by period type", enum=["daily", "weekly", "monthly"]),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all energy summaries with optional filtering
    
    Args:
        user_id (Optional[str]): Filter summaries by user ID
        period (Optional[str]): Filter summaries by period type
        current_user (dict): The current authenticated user
        
    Returns:
        List[EnergySummary]: List of energy summaries matching the filter criteria
    """
    query = {}
    if user_id:
        query["user_id"] = user_id
    if period:
        query["period"] = period
        
    summaries = list(summary_collection.find(query))
    
    # Convert ObjectId to string
    for summary in summaries:
        if '_id' in summary:
            summary['_id'] = str(summary['_id'])
            
    return summaries

@router.get("/{summary_id}", response_model=EnergySummary)
async def get_energy_summary(summary_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get a specific energy summary by ID
    
    Args:
        summary_id (str): The ID of the summary to retrieve
        current_user (dict): The current authenticated user
        
    Returns:
        EnergySummary: The requested energy summary
        
    Raises:
        HTTPException: If the summary is not found
    """
    try:
        summary = summary_collection.find_one({"_id": ObjectId(summary_id)})
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Energy summary not found"
            )
        
        # Convert ObjectId to string
        if '_id' in summary:
            summary['_id'] = str(summary['_id'])
            
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving energy summary: {str(e)}"
        )

@router.delete("/{summary_id}", dependencies=[Depends(role_required("admin"))])
async def delete_energy_summary(summary_id: str):
    """
    Delete an energy summary (admin only)
    
    Args:
        summary_id (str): The ID of the summary to delete
        
    Returns:
        dict: Confirmation of deletion
        
    Raises:
        HTTPException: If the summary is not found or deletion fails
    """
    try:
        # Check if summary exists
        summary = summary_collection.find_one({"_id": ObjectId(summary_id)})
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Energy summary not found"
            )
        
        # Delete the summary
        result = summary_collection.delete_one({"_id": ObjectId(summary_id)})
        
        if result.deleted_count:
            return {"message": "Energy summary deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete energy summary"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting energy summary: {str(e)}"
        )

@router.get("/anomalies")
async def get_energy_anomalies(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    sensitivity: float = Query(0.05, ge=0.01, le=0.1, description="Anomaly detection sensitivity (0.01-0.1)"),
    _ = Depends(get_current_user)
) -> Dict:
    """
    Detect and return anomalies in energy consumption data
    
    Args:
        start_date (str, optional): The start date for filtering data (YYYY-MM-DD)
        end_date (str, optional): The end date for filtering data (YYYY-MM-DD)
        device_id (str, optional): Filter by specific device
        sensitivity (float): Anomaly detection sensitivity (lower = more sensitive)
        
    Returns:
        Dict: List of detected anomalies with explanations
    """
    try:
        # Get energy data
        energy_data = get_energy_data(start_date, end_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    
    if not energy_data or len(energy_data) < 10:
        return {
            "anomalies": [],
            "message": "Insufficient data for anomaly detection (minimum 10 records required)"
        }
    
    # Apply device filter if provided
    if device_id:
        energy_data = [record for record in energy_data if record.get("device_id") == device_id]
        if len(energy_data) < 10:
            return {
                "anomalies": [],
                "message": f"Insufficient data for device {device_id} (minimum 10 records required)"
            }
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(energy_data)
    
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    else:
        return {"anomalies": [], "message": "No timestamp data available"}
        
    # Perform anomaly detection
    anomalies = []
    threshold = 0
    
    try:
        # Use a simplified anomaly detection approach for direct integration
        # Group by day and device to reduce noise
        if 'device_id' in df.columns:
            df['date'] = df['timestamp'].dt.date
            daily_usage = df.groupby(['date', 'device_id'])['energy_consumed'].sum().reset_index()
            
            # For each device, find outliers
            for device in daily_usage['device_id'].unique():
                device_data = daily_usage[daily_usage['device_id'] == device]
                if len(device_data) <= 2:  # Need more data points
                    continue
                    
                # Calculate simple statistics-based outliers
                # Use 3 standard deviations from the mean as a threshold
                mean = device_data['energy_consumed'].mean()
                std = device_data['energy_consumed'].std()
                threshold = mean + (3 * std)
                
                # Find anomalies
                outliers = device_data[device_data['energy_consumed'] > threshold]
                
                for _, row in outliers.iterrows():
                    severity = "high" if row['energy_consumed'] > (threshold * 1.5) else "medium"
                    anomalies.append({
                        "device_id": row['device_id'],
                        "date": pd.to_datetime(row['date']).strftime('%Y-%m-%d'),
                        "energy_consumed": float(row['energy_consumed']),
                        "threshold": float(threshold),
                        "severity": severity,
                        "description": f"Unusual energy consumption of {row['energy_consumed']:.2f} kWh detected for {row['device_id']} on {row['date'].strftime('%Y-%m-%d')}."
                    })
        
        # Sort anomalies by severity and date
        anomalies = sorted(anomalies, key=lambda x: (0 if x['severity'] == 'high' else 1, x['date']), reverse=True)
        
    except Exception as e:
        return {"anomalies": [], "message": f"Error in anomaly detection: {str(e)}"}
    
    return {
        "anomalies": anomalies,
        "anomaly_count": len(anomalies),
        "threshold": float(threshold) if threshold else 0
    }

@router.get("/forecast")
async def get_energy_forecast(
    days_ahead: int = Query(7, ge=1, le=30, description="Number of days to forecast"),
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    _ = Depends(get_current_user)
) -> Dict:
    """
    Forecast future energy consumption based on historical data
    
    Args:
        days_ahead (int): Number of days to forecast (1-30)
        device_id (str, optional): Filter by specific device
        
    Returns:
        Dict: Forecasted energy consumption data
    """
    # Get historical data (last 30 days by default)
    today = datetime.now()
    start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    
    try:
        energy_data = get_energy_data(start_date, end_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    
    if not energy_data or len(energy_data) < 14:
        return {
            "forecast": [],
            "message": "Insufficient historical data for forecasting (minimum 14 days required)"
        }
    
    # Apply device filter if provided
    if device_id:
        energy_data = [record for record in energy_data if record.get("device_id") == device_id]
        if len(energy_data) < 14:
            return {
                "forecast": [],
                "message": f"Insufficient historical data for device {device_id} (minimum 14 days required)"
            }
    
    # Convert to DataFrame
    df = pd.DataFrame(energy_data)
    
    # Ensure timestamp is datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    else:
        return {"forecast": [], "message": "No timestamp data available"}
    
    # Forecast future energy consumption
    forecast_result = []
    
    try:
        # Group by day to get daily consumption
        df['date'] = df['timestamp'].dt.date
        daily_data = df.groupby('date')['energy_consumed'].sum().reset_index()
        daily_data['date'] = pd.to_datetime(daily_data['date'])
        
        if len(daily_data) < 14:
            return {"forecast": [], "message": "Insufficient daily data for forecasting"}
        
        # Sort by date
        daily_data = daily_data.sort_values('date')
        
        # Simple moving average forecast
        # This is a simplified forecast method that can be replaced with more advanced methods
        window_size = min(7, len(daily_data) // 2)
        # FIX: I don't understand this
        rolling_mean = daily_data['energy_consumed'].rolling(window_size).mean().iloc[-1]
        
        # Generate forecast dates
        last_date = daily_data['date'].max()
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
        
        # Create historical data for context
        for _, row in daily_data.iterrows():
            forecast_result.append({
                "date": pd.to_datetime(row['date']).strftime('%Y-%m-%d'),
                "energy_forecast": float(row['energy_consumed']),
                "type": "historical",
                "cost_estimate": float(row['energy_consumed'] * DEFAULT_ENERGY_COST)
            })
        
        # Add forecasted data
        # In a real implementation, you might use ARIMA, exponential smoothing, or other
        # time series forecasting methods for better accuracy
        for forecast_date in forecast_dates:
            # Add some random variation to make the forecast look more realistic
            variation = np.random.normal(0, rolling_mean * 0.1)
            forecasted_value = max(0, rolling_mean + variation)
            
            forecast_result.append({
                "date": forecast_date.strftime('%Y-%m-%d'),
                "energy_forecast": float(forecasted_value),
                "type": "forecast",
                "cost_estimate": float(forecasted_value * DEFAULT_ENERGY_COST)
            })
    
    except Exception as e:
        return {"forecast": [], "message": f"Error in forecasting: {str(e)}"}
    
    # Calculate totals for forecasted data only
    forecast_only = [item for item in forecast_result if item["type"] == "forecast"]
    total_energy_forecast = sum(item["energy_forecast"] for item in forecast_only)
    total_cost_estimate = sum(item["cost_estimate"] for item in forecast_only)
    
    return {
        "forecast": forecast_result,
        "days_forecast": days_ahead,
        "total_energy_forecast": round(total_energy_forecast, 2),
        "total_cost_estimate": round(total_cost_estimate, 2)
    }
