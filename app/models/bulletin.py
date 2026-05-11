from pydantic import BaseModel
from typing import Optional

class BulletinMatch(BaseModel):
    matchId: str
    league: str
    leagueId: Optional[str] = None
    time: str
    home: str
    away: str
    homeId: Optional[str] = None
    awayId: Optional[str] = None
    homeScore: Optional[int] = None
    awayScore: Optional[int] = None
    score: Optional[str] = None
    status: Optional[str] = None
    elapsed: Optional[int] = None
    hasStats: bool = False
    hasEvents: bool = False
    hasLineups: bool = False