from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EnergyData(BaseModel):
    device_id: str
    timestamp: datetime
    energy_consumed: float      # tracking in kWh (kilowatt hours)
    location: Optional[str] = None
