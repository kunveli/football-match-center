from pydantic import BaseModel
from typing import List, Optional

class MatchSummary(BaseModel):
    homeWins: int
    draws: int
    awayWins: int
    avgGoals: str
    avgCards: str
    avgCorners: str
    firstGoalTeam: Optional[str] = None

class GoalStats(BaseModel):
    goals0_15: str
    goals16_30: str
    goals31_45: str
    goals46_60: str
    goals61_75: str
    goals76_90: str
    firstGoalTeam: Optional[str] = None
    lastGoalTeam: Optional[str] = None
    penaltyGoals: str
    headerGoals: str

class CardStats(BaseModel):
    yellowTotal: str
    redTotal: str
    yellowAvg: str
    redAvg: str
    foulAvg: str
    cornerAvg: str
    offsideAvg: str

class GameStats(BaseModel):
    totalShots: str
    shotsOnTarget: str
    possession: str
    penaltyAreaTouches: str
    offsides: str
    varChecks: Optional[str] = None

class OverUnderStats(BaseModel):
    over15: str
    over25: str
    over35: str
    over45: str
    bttsYes: str
    bttsNo: str
    htOver05: str
    htOver15: str
    htResultDist: str
    ftResultDist: str

class MatchEvent(BaseModel):
    type: str
    minute: int
    team: str
    player: str
    detail: Optional[str] = None

class MatchStats(BaseModel):
    teamName: str
    matchesPlayed: int
    wins: int
    draws: int
    losses: int
    avgGoalsScored: str
    avgGoalsConceded: str
    avgShots: str
    avgShotsOnTarget: str
    avgPossession: str
    avgCorners: str
    avgFouls: str
    avgYellowCards: str
    avgRedCards: str

class MatchDetail(BaseModel):
    summary: MatchSummary
    goals: GoalStats
    cards: CardStats
    game: GameStats
    overUnder: OverUnderStats
    events: List[MatchEvent]
    homeStats: MatchStats
    awayStats: MatchStats