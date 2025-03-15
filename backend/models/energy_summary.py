"""
This module defines the EnergySummary model for analyzing & reporting energy consumption

The EnergySummary model:
- Aggregates energy consumption data over specified time periods
- Supports reporting & historical data analysis requirements
- Enables cost estimation based on energy usage
- Facilitates comparisons between current & past usage periods
- Provides the data foundation for energy-saving suggestions & insights
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class EnergySummary(BaseModel):
    """
    Pydantic model representing aggregated energy usage data for reporting
    
    Provides summarized energy consumption data for specific time periods,
        enabling users to track trends & compare usage over time
    
    Attributes:
        user_id (str): ID of the user this summary belongs to
        period (str): Time period of the summary ("daily", "weekly", "monthly")
        start_date (datetime): Beginning of the summary period
        end_date (datetime): End of the summary period
        total_consumption (float): Total energy consumed in kWh during the period
        cost_estimate (Optional[float]): Estimated cost of energy used
        comparison_to_previous (Optional[float]): Percentage change compared to previous period
    """
    user_id: str
    period: str     # daily, weekly, monthly
    start_date: datetime
    end_date: datetime
    total_consumption: float
    cost_estimate: Optional[float]
    comparison_to_previous: Optional[float]     # percentage change
