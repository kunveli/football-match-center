from app.models.match import MatchSummary, GoalStats, CardStats, GameStats, OverUnderStats, MatchEvent, MatchStats, MatchDetail
from app.models.h2h import H2HMatchRow, H2HSummary

def get_mock_match_detail(match_id: str, home_team: str = "Home Team", away_team: str = "Away Team") -> MatchDetail:
    home_name = (home_team or "Home Team").strip()
    away_name = (away_team or "Away Team").strip()

    summary = MatchSummary(
        homeWins=15, draws=5, awayWins=10,
        avgGoals="2.8", avgCards="3.5", avgCorners="10.2",
        firstGoalTeam=home_name
    )
    
    goals = GoalStats(
        goals0_15="3", goals16_30="5", goals31_45="4",
        goals46_60="6", goals61_75="7", goals76_90="5",
        firstGoalTeam=f"{home_name} (%65)", lastGoalTeam=f"{away_name} (%55)",
        penaltyGoals="2", headerGoals="4"
    )
    
    cards = CardStats(
        yellowTotal="38", redTotal="3",
        yellowAvg="3.8", redAvg="0.3",
        foulAvg="12.4", cornerAvg="9.8", offsideAvg="2.1"
    )
    
    game = GameStats(
        totalShots="14", shotsOnTarget="6",
        possession="%58", penaltyAreaTouches="32",
        offsides="3", varChecks=None
    )
    
    over_under = OverUnderStats(
        over15="9/10", over25="7/10", over35="4/10", over45="2/10",
        bttsYes="6/10", bttsNo="4/10",
        htOver05="8/10", htOver15="4/10",
        htResultDist="1: %40 · X: %30 · 2: %30",
        ftResultDist="1: %50 · X: %20 · 2: %30"
    )
    
    events = [
        MatchEvent(type="goal", minute=23, team="home", player=f"{home_name} Player A", detail="penalty"),
        MatchEvent(type="yellowCard", minute=35, team="away", player=f"{away_name} Player B"),
        MatchEvent(type="goal", minute=67, team="away", player=f"{away_name} Player C", detail="header"),
        MatchEvent(type="substitution", minute=75, team="home", player=f"{home_name} Player D"),
        MatchEvent(type="redCard", minute=89, team="away", player=f"{away_name} Player E", detail="secondYellow")
    ]
    
    home_stats = MatchStats(
        teamName=home_name, matchesPlayed=10, wins=6, draws=2, losses=2,
        avgGoalsScored="1.8", avgGoalsConceded="1.0", avgShots="12.5",
        avgShotsOnTarget="5.2", avgPossession="55%", avgCorners="6.8",
        avgFouls="11.2", avgYellowCards="2.1", avgRedCards="0.1"
    )
    
    away_stats = MatchStats(
        teamName=away_name, matchesPlayed=10, wins=4, draws=2, losses=4,
        avgGoalsScored="1.2", avgGoalsConceded="1.8", avgShots="11.8",
        avgShotsOnTarget="4.8", avgPossession="45%", avgCorners="5.9",
        avgFouls="10.8", avgYellowCards="2.3", avgRedCards="0.2"
    )
    
    return MatchDetail(
        summary=summary, goals=goals, cards=cards, game=game,
        overUnder=over_under, events=events, homeStats=home_stats, awayStats=away_stats
    )

def get_mock_h2h(home_team: str, away_team: str) -> H2HSummary:
    matches = [
        H2HMatchRow(date="12.03.25", league="Premier League", home=home_team, halfTimeScore="2-1", fullTimeScore="3-2", away=away_team),
        H2HMatchRow(date="28.11.24", league="Premier League", home=away_team, halfTimeScore="0-0", fullTimeScore="1-0", away=home_team),
        H2HMatchRow(date="15.04.24", league="Premier League", home=home_team, halfTimeScore="1-1", fullTimeScore="2-2", away=away_team),
        H2HMatchRow(date="01.10.23", league="Premier League", home=away_team, halfTimeScore="0-1", fullTimeScore="0-2", away=home_team),
        H2HMatchRow(date="22.04.23", league="Premier League", home=home_team, halfTimeScore="2-0", fullTimeScore="3-1", away=away_team),
        H2HMatchRow(date="06.11.22", league="Premier League", home=away_team, halfTimeScore="0-0", fullTimeScore="0-1", away=home_team),
        H2HMatchRow(date="12.02.22", league="Premier League", home=home_team, halfTimeScore="1-0", fullTimeScore="2-1", away=away_team),
        H2HMatchRow(date="22.08.21", league="Premier League", home=home_team, halfTimeScore="0-1", fullTimeScore="0-2", away=away_team),
        H2HMatchRow(date="12.05.21", league="Premier League", home=away_team, halfTimeScore="1-0", fullTimeScore="2-0", away=home_team),
        H2HMatchRow(date="26.12.20", league="Premier League", home=home_team, halfTimeScore="1-1", fullTimeScore="3-1", away=away_team),
    ]
    
    return H2HSummary(over25="7/10", bttsYes="6/10", htOver05="8/10", matches=matches)