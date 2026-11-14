from typing import List, Optional
from pydantic import BaseModel, Field

from datetime import datetime 

class PercentModel(BaseModel):
    percent: float