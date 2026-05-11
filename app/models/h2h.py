from pydantic import BaseModel
from typing import List

class H2HMatchRow(BaseModel):
    date: str
    league: str
    home: str
    halfTimeScore: str
    fullTimeScore: str
    away: str

class H2HSummary(BaseModel):
    over25: str
    bttsYes: str
    htOver05: str
    matches: List[H2HMatchRow]