import random
import math
import pandas as pd
from baseprobabilities import *
from teamclasses import *
from play_by_play_collector import *
from matchdata import *
import csv
import os


def neutralInput():
    while True:
        Neutral = input("Neutral court? (yes/no): ")
        if Neutral not in ("yes", "no", "y", "n"):
            print("Not an appropriate choice.")
        else:
            return Neutral


def GetNeutralValue(num):
    if num == 1 or num == "1":
        return "y"
    return "n"


def GetBooleanValue(str_value):
    if str_value == 1 or str_value == "1":
        return True
    return False


def rungame(gameid, awayteam, hometeam, is_neutral, is_nba, filePath):
    Home = hometeam
    Away = awayteam
    Neutral = GetNeutralValue(is_neutral)
    nba_match = GetBooleanValue(is_nba)

    t1 = Home
    t2 = Away
    if Neutral == "no" or Neutral == "n":
        HCA = -0.01
        HCAAdj = round(-0.01 / -3, 12)
    elif Neutral == "yes" or Neutral == "y":
        HCA = 0
        HCAAdj = 0

    # Get the Match Data
    match_data = GetMatchData(t1, t2)
    # Coach Info
    HomeCoach = match_data["HomeTeam"]["Coach"]
    AwayCoach = match_data["AwayTeam"]["Coach"]

    # Gameplan and Bonuses
    t1InsShootingBonus = 0
    t1MidShootingBonus = 0
    t13ptShootingBonus = 0
    t1BallworkBonus = 0
    t1ReboundingBonus = 0
    t1TurnoverBonus = 0
    t1team_df = match_data["HomeTeamGameplan"]
    t1FocusPlayer = t1team_df["FocusPlayer"]
    t2team_df = match_data["AwayTeamGameplan"]
    t2FocusPlayer = t2team_df["FocusPlayer"]
    t2InsShootingBonus = 0
    t2MidShootingBonus = 0
    t23ptShootingBonus = 0
    t2BallworkBonus = 0
    t2ReboundingBonus = 0
    t2TurnoverBonus = 0

    if t1team_df["OffensiveFormation"] == "Motion":
        t1InsShootingBonus += 2
        t13ptShootingBonus += 1
        t1BallworkBonus -= 2
        t1ReboundingBonus -= 1
    elif t1team_df["OffensiveFormation"] == "Pick-and-Roll":
        t1InsShootingBonus += 2
        t1BallworkBonus += 2
        t1MidShootingBonus -= 1
        t1ReboundingBonus -= 1
    elif t1team_df["OffensiveFormation"] == "Post-Up":
        t1InsShootingBonus += 2
        t1ReboundingBonus += 2
        t1MidShootingBonus -= 1
        t13ptShootingBonus -= 1
    elif t1team_df["OffensiveFormation"] == "Space-and-Post":
        t1MidShootingBonus += 2
        t13ptShootingBonus += 1
        t1BallworkBonus -= 2
        t1ReboundingBonus -= 1

    if t2team_df["DefensiveFormation"] == "Man-to-Man":
        if t2team_df["FocusPlayer"] in t1team_df["FocusPlayer"]:
            t1InsShootingBonus += 2
            t1MidShootingBonus += 2
            t13ptShootingBonus += 2
    elif t2team_df["DefensiveFormation"] == "1-3-1 Zone":
        t1MidshootingBonus -= 2
        t13ptShootingBonus += 1
        t1InsShootingBonus += 1
        t2TurnoverBonus += 1
    elif t2team_df["DefensiveFormation"] == "3-2 Zone":
        t13ptShootingBonus -= 2
        t1InsShootingBonus += 1
        t1ReboundingBonus += 1
    elif t2team_df["DefensiveFormation"] == "2-3 Zone":
        t1InsShootingBonus -= 2
        t2ReboundingBonus += 2
        t13ptShootingBonus += 1
    elif t2team_df["DefensiveFormation"] == "Box-and-One Zone":
        t1InsShootingBonus += 2
        t1MidShootingBonus += 2
        t13ptShootingBonus += 2

    if t2team_df["OffensiveFormation"] == "Motion":
        t2InsShootingBonus += 2
        t23ptShootingBonus += 1
        t2BallworkBonus -= 2
        t2ReboundingBonus -= 1
    elif t2team_df["OffensiveFormation"] == "Pick-and-Roll":
        t2InsShootingBonus += 2
        t2BallworkBonus += 2
        t2MidShootingBonus -= 1
        t2ReboundingBonus -= 1
    elif t2team_df["OffensiveFormation"] == "Post-Up":
        t2InsShootingBonus += 2
        t2ReboundingBonus += 2
        t2MidShootingBonus -= 1
        t23ptShootingBonus -= 1
    elif t2team_df["OffensiveFormation"] == "Space-and-Post":
        t2MidShootingBonus += 2
        t23ptShootingBonus += 1
        t2BallworkBonus -= 2
        t2ReboundingBonus -= 1

    if t1team_df["DefensiveFormation"] == "Man-to-Man":
        if t1team_df["FocusPlayer"] in t2team_df["FocusPlayer"]:
            t2InsShootingBonus += 2
            t2MidShootingBonus += 2
            t23ptShootingBonus += 2
    elif t1team_df["DefensiveFormation"] == "1-3-1 Zone":
        t2MidshootingBonus -= 2
        t23ptShootingBonus += 1
        t2InsShootingBonus += 1
        t1TurnoverBonus += 1
    elif t1team_df["DefensiveFormation"] == "3-2 Zone":
        t23ptShootingBonus -= 2
        t2InsShootingBonus += 1
        t2ReboundingBonus += 1
    elif t1team_df["DefensiveFormation"] == "2-3 Zone":
        t2InsShootingBonus -= 2
        t1ReboundingBonus += 2
        t23ptShootingBonus += 1
    elif t1team_df["DefensiveFormation"] == "Box-and-One Zone":
        t2InsShootingBonus += 2
        t2MidShootingBonus += 2
        t23ptShootingBonus += 2

    # Rosters
    team_one_roster = []
    team_two_roster = []
    t1rosterRaw_df = match_data["HomeTeamRoster"]
    t2rosterRaw_df = match_data["AwayTeamRoster"]
    t1Rebounding = round(sum(cp["Rebounding"] for cp in t1rosterRaw_df))
    t1StealBlock = round(
        sum(cp["InteriorDefense"] + cp["PerimeterDefense"] for cp in t1rosterRaw_df)
    )
    t1Ballwork = round(sum(cp["Ballwork"] for cp in t1rosterRaw_df))
    t2Rebounding = round(sum(cp["Rebounding"] for cp in t2rosterRaw_df))
    t2StealBlock = round(
        sum(cp["InteriorDefense"] + cp["PerimeterDefense"] for cp in t2rosterRaw_df)
    )
    t2Ballwork = round(sum(cp["Ballwork"] for cp in t2rosterRaw_df))
    t1InsPro = sum(cp["InsideProportion"] for cp in t1rosterRaw_df)
    t1MidPro = sum(cp["MidRangeProportion"] for cp in t1rosterRaw_df)
    t13ptPro = sum(cp["ThreePointProportion"] for cp in t1rosterRaw_df)
    t2InsPro = sum(cp["InsideProportion"] for cp in t2rosterRaw_df)
    t2MidPro = sum(cp["MidRangeProportion"] for cp in t2rosterRaw_df)
    t23ptPro = sum(cp["ThreePointProportion"] for cp in t2rosterRaw_df)

    t1roster_df = team_one_roster

    for x in t1rosterRaw_df:
        cp = Player(
            x,
            t1InsShootingBonus,
            t1MidShootingBonus,
            t13ptShootingBonus,
            t1BallworkBonus,
            t1ReboundingBonus,
        )
        cp.get_advanced_stats(
            t1Rebounding,
            t1StealBlock,
            t1Ballwork,
            t1InsPro,
            t1MidPro,
            t13ptPro,
            t1TurnoverBonus,
        )
        team_one_roster.append(cp)

    for x in t2rosterRaw_df:
        cp = Player(
            x,
            t2InsShootingBonus,
            t2MidShootingBonus,
            t23ptShootingBonus,
            t2BallworkBonus,
            t2ReboundingBonus,
        )
        cp.get_advanced_stats(
            t2Rebounding,
            t2StealBlock,
            t2Ballwork,
            t2InsPro,
            t2MidPro,
            t23ptPro,
            t2TurnoverBonus,
        )
        team_two_roster.append(cp)
    t2roster_df = team_two_roster

    t1Height = round(sum(cp.Height for cp in t1roster_df))

    t1InteriorDef = round(sum(cp.InteriorDefense for cp in t1roster_df))
    t1OutsideDef = round(sum(cp.PerimeterDefense for cp in t1roster_df))
    t1InsPro = sum(cp.InsideProportion for cp in t1roster_df)
    t1MidPro = sum(cp.MidRangeProportion for cp in t1roster_df)
    t13ptPro = sum(cp.ThreePointProportion for cp in t1roster_df)

    t2Height = round(sum(cp.Height for cp in t2roster_df))

    t2InteriorDef = round(sum(cp.InteriorDefense for cp in t2roster_df))
    t2OutsideDef = round(sum(cp.PerimeterDefense for cp in t2roster_df))
    t2InsPro = sum(cp.InsideProportion for cp in t2roster_df)
    t2MidPro = sum(cp.MidRangeProportion for cp in t2roster_df)
    t23ptPro = sum(cp.ThreePointProportion for cp in t2roster_df)

    t1SortByMinutes = sorted(t1roster_df, key=lambda x: x.Minutes, reverse=True)
    t1Tip1 = t1SortByMinutes[0:4]
    t1SortByHeight = sorted(t1Tip1, key=lambda x: x.Height, reverse=True)
    t2SortByMinutes = sorted(t2roster_df, key=lambda x: x.Minutes, reverse=True)
    t2Tip1 = t2SortByMinutes[0:4]
    t2SortByHeight = sorted(t2Tip1, key=lambda x: x.Height, reverse=True)
    t1Tip2 = t1SortByHeight[0]
    t2Tip2 = t2SortByHeight[0]

    t1TipChance = ((t1Tip2.Height - t2Tip2.Height) * 0.01) + 0.5
    t2TipChance = ((t2Tip2.Height - t1Tip2.Height) * 0.01) + 0.5

    t1HeightDiff = t1Height - t2Height
    t2HeightDiff = t2Height - t1Height

    # Team Based Adjusted Variables
    t1_adj_Height_Diff = t1HeightDiff * 10
    t1_adj_shooting = round(sum(cp.AdjShooting for cp in t1roster_df))
    t1_adj_finishing = round(sum(cp.AdjFinishing for cp in t1roster_df))
    t1_adj_ballwork = round(sum(cp.AdjBallwork for cp in t1roster_df))
    t1_adj_rebound = round(sum(cp.AdjRebounding for cp in t1roster_df))
    t1_adj_defense = round(sum(cp.AdjStealing for cp in t1roster_df))
    t1_def_rate_to = round(sum(cp.DefRateTO for cp in t1roster_df))
    t1_adj_perimeter_defense = round(sum(cp.AdjPerimeterDefense for cp in t1roster_df))
    t1_adj_interior_defense = round(sum(cp.AdjInteriorDefense for cp in t1roster_df))

    t2_adj_Height_Diff = t2HeightDiff * 10
    t2_adj_shooting = round(sum(cp.AdjShooting for cp in t2roster_df))
    t2_adj_finishing = round(sum(cp.AdjFinishing for cp in t2roster_df))
    t2_adj_ballwork = round(sum(cp.AdjBallwork for cp in t2roster_df))
    t2_adj_rebound = round(sum(cp.AdjRebounding for cp in t2roster_df))
    t2_adj_defense = round(sum(cp.AdjStealing for cp in t2roster_df))
    t2_def_rate_to = round(sum(cp.DefRateTO for cp in t2roster_df))
    t2_adj_perimeter_defense = round(sum(cp.AdjPerimeterDefense for cp in t2roster_df))
    t2_adj_interior_defense = round(sum(cp.AdjInteriorDefense for cp in t2roster_df))
    t1Offense = round((t1_adj_shooting + t1_adj_finishing + t1_adj_ballwork) / 3)
    t1RebDiff = round(t1_adj_rebound - t2_adj_defense + t1_adj_Height_Diff)
    t1BallDef = round(t1_adj_ballwork - t2_adj_defense + t1_adj_Height_Diff)
    t1TO = round(t1_adj_ballwork - t2_def_rate_to + t1_adj_Height_Diff)
    t1OffensiveRebound = round((0.00003 * t1RebDiff) + 0.28, 6)
    t1StealsAdj = round(-0.000008 * t1TO, 6)
    t1OtherTO = round(-0.000005 * t1TO, 6)
    t1StealsAdjNeg = t1StealsAdj / (-3)
    t1OtherTOAdjNeg = t1OtherTO / (-3)
    t1threeptAttemptGPAdj = (0.81 * (t13ptPro / 100)) - threeptAttemptProbability
    t1twoptJumperGPAdj = (0.81 * (t1MidPro / 100)) - twoptJumperProbability
    t1twoptInsideGPAdj = (0.81 * (t1InsPro / 100)) - twoptInsideProbability
    t1BaseCutoff = 0
    t1StealCutoff = stealProbability + t1StealsAdj + t1BaseCutoff
    t1OtherTOCutoff = otherTurnoverProbability + HCA + t1OtherTO + t1StealCutoff
    t1threeptAttemptCutoff = round(
        threeptAttemptProbability
        + HCAAdj
        + t1StealsAdjNeg
        + t1OtherTOAdjNeg
        + t1threeptAttemptGPAdj
        + t1OtherTOCutoff,
        5,
    )
    t1twoJumperCutoff = round(
        twoptJumperProbability
        + HCAAdj
        + t1StealsAdjNeg
        + t1OtherTOAdjNeg
        + t1twoptJumperGPAdj
        + t1threeptAttemptCutoff,
        5,
    )
    t1twoInsideCutoff = round(
        twoptInsideProbability
        + HCAAdj
        + t1StealsAdjNeg
        + t1OtherTOAdjNeg
        + t1twoptInsideGPAdj
        + t1twoJumperCutoff
    )

    t2Offense = round((t2_adj_shooting + t2_adj_finishing + t2_adj_ballwork) / 3)
    t2RebDiff = round(t2_adj_rebound - t1_adj_rebound + t2_adj_Height_Diff)
    t2BallDef = round(t2_adj_ballwork - t1_adj_defense + t2_adj_Height_Diff)
    t2TO = round(t2_adj_ballwork - t1_def_rate_to + t2_adj_Height_Diff)
    t2OffensiveRebound = round((0.00003 * t2RebDiff) + 0.28, 6)
    t2StealsAdj = round(-0.000008 * t2TO, 6)
    t2OtherTO = round(-0.000005 * t2TO, 6)
    t2StealsAdjNeg = round(t2StealsAdj / -3, 12)
    t2OtherTOAdjNeg = round(t2OtherTO / -3, 12)
    t2threeptAttemptGPAdj = round(
        (0.81 * (t23ptPro / 100)) - threeptAttemptProbability, 5
    )
    t2twoptJumperGPAdj = round((0.81 * (t2MidPro / 100)) - twoptJumperProbability, 6)
    t2twoptInsideGPAdj = round((0.81 * (t2InsPro / 100)) - twoptInsideProbability, 6)
    t2BaseCutoff = 0
    t2StealCutoff = stealProbability + t2StealsAdj + t2BaseCutoff
    t2OtherTOCutoff = otherTurnoverProbability + t2OtherTO + t2StealCutoff
    t2threeptAttemptCutoff = round(
        threeptAttemptProbability
        + t2StealsAdjNeg
        + t2OtherTOAdjNeg
        + t2threeptAttemptGPAdj
        + t2OtherTOCutoff,
        5,
    )
    t2twoJumperCutoff = round(
        twoptJumperProbability
        + t2StealsAdjNeg
        + t2OtherTOAdjNeg
        + t2twoptJumperGPAdj
        + t2threeptAttemptCutoff,
        5,
    )
    t2twoInsideCutoff = round(
        twoptInsideProbability
        + t2StealsAdjNeg
        + t2OtherTOAdjNeg
        + t2twoptInsideGPAdj
        + t2twoJumperCutoff
    )

    if t1team_df["Pace"] == "Very Fast":
        if nba_match:
            t1pace = random.randint(105, 110)
        else:
            t1pace = random.randint(80, 85)
    elif t1team_df["Pace"] == "Fast":
        if nba_match:
            t1pace = random.randint(100, 105)
        else:
            t1pace = random.randint(75, 80)
    elif t1team_df["Pace"] == "Balanced":
        if nba_match:
            t1pace = random.randint(95, 100)
        else:
            t1pace = random.randint(70, 75)
    elif t1team_df["Pace"] == "Slow":
        if nba_match:
            t1pace = random.randint(90, 95)
        else:
            t1pace = random.randint(65, 70)
    elif t1team_df["Pace"] == "Very Slow":
        if nba_match:
            t1pace = random.randint(85, 90)
        else:
            t1pace = random.randint(60, 65)

    if t2team_df["Pace"] == "Very Fast":
        if nba_match:
            t2pace = random.randint(105, 110)
        else:
            t2pace = random.randint(80, 85)
    elif t2team_df["Pace"] == "Fast":
        if nba_match:
            t2pace = random.randint(100, 105)
        else:
            t2pace = random.randint(75, 80)
    elif t2team_df["Pace"] == "Balanced":
        if nba_match:
            t2pace = random.randint(95, 100)
        else:
            t2pace = random.randint(70, 75)
    elif t2team_df["Pace"] == "Slow":
        if nba_match:
            t2pace = random.randint(90, 95)
        else:
            t2pace = random.randint(65, 70)
    elif t2team_df["Pace"] == "Very Slow":
        if nba_match:
            t2pace = random.randint(85, 90)
        else:
            t2pace = random.randint(60, 65)

    possessionNum = 0
    total_possessions = t1pace + t2pace
    halftime_point = total_possessions / 2
    t1pts = 0
    t2pts = 0
    is_ot = False
    gett1Players = team_one_roster
    gett2Players = team_two_roster
    team_one = Team(match_data["HomeTeam"])
    team_two = Team(match_data["AwayTeam"])
    play_by_play = []
    collector = Play_By_Play_Collector()

    while possessionNum <= total_possessions:
        if possessionNum == 0:
            tipOff = random.random()
            if tipOff < t1TipChance:
                possession = t2
                collector.AppendPlay(
                    t2,
                    t2Tip2.FirstName + " wins the tipoff for " + t2 + "!",
                    "Tipoff",
                    0,
                    0,
                    0,
                    total_possessions,
                )
            else:
                possession = t1
                collector.AppendPlay(
                    t1,
                    t1Tip2.FirstName + " wins the tipoff for " + t1 + "!",
                    "Tipoff",
                    0,
                    0,
                    0,
                    total_possessions,
                )

        if Neutral == "no" or Neutral == "n":
            HCA = 0.025
        elif Neutral == "yes" or Neutral == "y":
            HCA = 0

        possessionNum += 1

        possrand = random.random()

        if possession == t1:
            team_one.Stats.AddPossession()
            if possrand < t1StealCutoff:
                pickPlayer = random.choices(
                    gett2Players, weights=[x.DefensePer for x in team_two_roster], k=1
                )
                stealPlayer = pickPlayer[0]
                stealPlayer.Stats.AddPossession()
                stealPlayer.Stats.AddSteal()
                team_one.Stats.AddTurnover()
                printShooter = stealPlayer.FirstName + " " + stealPlayer.LastName
                msg = printShooter + " steals the ball for " + t2 + "!"
                possession = t2
                collector.AppendPlay(
                    possession,
                    msg,
                    "Turnover",
                    t1pts,
                    t2pts,
                    possessionNum,
                    total_possessions,
                )
            elif possrand < t1OtherTOCutoff:
                otherTO = random.random()
                pickPlayer = random.choices(
                    gett1Players, weights=[x.Usage for x in team_one_roster], k=1
                )
                toPlayer = pickPlayer[0]
                toPlayer.Stats.AddPossession()
                printShooter = toPlayer.FirstName + " " + toPlayer.LastName
                team_one.Stats.AddTurnover()
                if otherTO < 0.582:
                    msg = t1 + " " + printShooter + " lost the ball out of bounds."
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Out of Bounds",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                elif otherTO < 0.64:
                    msg = (
                        possession
                        + ": Shot clock violation on "
                        + t1
                        + " "
                        + printShooter
                        + "."
                    )
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Shot Clock Violation",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                elif otherTO < 1:
                    msg = (
                        possession
                        + ": Offensive foul on "
                        + t1
                        + " "
                        + printShooter
                        + "."
                    )
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Foul",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                    toPlayer.Stats.AddFoul()
                possession = t2
            elif possrand < t1threeptAttemptCutoff:
                pickPlayer = random.choices(
                    gett1Players,
                    weights=[x.ThreePointUsage for x in team_one_roster],
                    k=1,
                )
                shooter = pickPlayer[0]
                shooter.Stats.AddPossession()
                printShooter = shooter.FirstName + " " + shooter.LastName
                blockAdj = (0.00001 * t2_adj_perimeter_defense) - 0.0153
                made3nf = 0
                if shooter.ID == t2team_df["FocusPlayer"]:
                    made3nf = (0.015 * shooter.Shooting3) - 4 + 0.185 + HCA
                else:
                    made3nf = (0.015 * shooter.Shooting3) + 0.185 + HCA
                madeDiff = made3nf - 0.335
                missed3nf = 0.635 - madeDiff - blockAdj
                made3foul = 0.005
                missed3foul = 0.015
                blocked = 0.01 + blockAdj
                base3Cutoff = 0
                made3Cutoff = base3Cutoff + made3nf
                missed3Cutoff = made3Cutoff + missed3nf
                blocked3Cutoff = missed3Cutoff + blocked
                missed3foulCutoff = blocked3Cutoff + missed3foul
                made3foulCutoff = missed3foulCutoff + made3foul
                eventOutcome = random.random()
                if eventOutcome < made3Cutoff:
                    play = printShooter + " 3-point attempt...Score!"
                    t1pts += 3
                    shooter.Stats.AddFieldGoal(True, 3)
                    team_one.Stats.AddPoints(3, possessionNum, halftime_point, is_ot)
                    team_one.Stats.CalculateLead(3, t1pts - t2pts)
                    team_one.Stats.AddThreePointShot(True)
                    assistRand = random.random()
                    if assistRand > 0.173:
                        assistList = [x for x in gett1Players if x.ID != shooter.ID]
                        pickPlayer = random.choices(
                            assistList, weights=[x.AssistPer for x in assistList], k=1
                        )
                        assister = pickPlayer[0]
                        if assister.ID != shooter.ID:
                            assister.Stats.AddAssist()
                            team_one.Stats.AddAssist()
                            printAssister = assister.FirstName + " " + assister.LastName
                            play += "       Assisted by: " + printAssister
                    collector.AppendPlay(
                        possession,
                        play,
                        "Score",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                    possession = t2
                elif eventOutcome < missed3Cutoff:
                    play = printShooter + " 3-point attempt...Missed!"
                    shooter.Stats.AddFieldGoal(False, 3)
                    team_one.Stats.AddThreePointShot(False)
                    rebrand = random.random()
                    if rebrand < t1OffensiveRebound:
                        pickt1Rebounder = random.choices(
                            gett1Players,
                            weights=[x.ReboundingPer for x in team_one_roster],
                            k=1,
                        )
                        t1rebounder = pickt1Rebounder[0]
                        t1rebounder.Stats.AddRebound(True)
                        team_one.Stats.AddRebound(True)
                        printt1Rebounder = (
                            t1rebounder.FirstName + " " + t1rebounder.LastName
                        )
                        play += (
                            "       Rebounded by " + t1 + " " + printt1Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            play,
                            "Missed",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t1
                    else:
                        pickt2Rebounder = random.choices(
                            gett2Players,
                            weights=[x.ReboundingPer for x in team_two_roster],
                            k=1,
                        )
                        t2rebounder = pickt2Rebounder[0]
                        t2rebounder.Stats.AddRebound(False)
                        team_two.Stats.AddRebound(False)
                        printt2Rebounder = (
                            t2rebounder.FirstName + " " + t2rebounder.LastName
                        )
                        play += (
                            "       Rebounded by " + t2 + " " + printt2Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            play,
                            "Miss",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t2
                elif eventOutcome < blocked3Cutoff:
                    pickBlocker = random.choices(
                        gett2Players,
                        weights=[x.DefensePer for x in team_two_roster],
                        k=1,
                    )
                    blocker = pickBlocker[0]
                    shooter.Stats.AddFieldGoal(False, 3)
                    team_one.Stats.AddThreePointShot(False)
                    blocker.Stats.AddBlock()
                    team_two.Stats.AddBlocks()
                    printBlocker = blocker.FirstName + " " + blocker.LastName
                    play = (
                        printShooter
                        + " 3-point attempt...BLOCKED by "
                        + t2
                        + " "
                        + printBlocker
                        + "."
                    )
                    rebrand = random.random()
                    if rebrand < 0.43:
                        pickt1Rebounder = random.choices(
                            gett1Players,
                            weights=[x.ReboundingPer for x in team_one_roster],
                            k=1,
                        )
                        t1rebounder = pickt1Rebounder[0]
                        t1rebounder.Stats.AddRebound(True)
                        team_one.Stats.AddRebound(True)
                        printt1Rebounder = (
                            t1rebounder.FirstName + " " + t1rebounder.LastName
                        )
                        play += (
                            "       Rebounded by " + t1 + " " + printt1Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            play,
                            "Score",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t1
                    else:
                        pickt2Rebounder = random.choices(
                            gett2Players,
                            weights=[x.ReboundingPer for x in team_two_roster],
                            k=1,
                        )
                        t2rebounder = pickt2Rebounder[0]
                        t2rebounder.Stats.AddRebound(False)
                        team_two.Stats.AddRebound(False)
                        printt2Rebounder = (
                            t2rebounder.FirstName + " " + t2rebounder.LastName
                        )
                        play += (
                            "       Rebounded by " + t2 + " " + printt2Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            play,
                            "Score",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t2
                elif eventOutcome < missed3foulCutoff:
                    play_by_play.append(
                        printShooter
                        + " 3-point attempt... Missed. There is a foul on the play."
                    )
                    foulShots = 3
                    shooter.Stats.AddFieldGoal(False, 3)
                    team_one.Stats.AddThreePointShot(False)
                    team_two.Stats.AddFoul()
                    ftCutoff = (0.02 * shooter.FreeThrow) + 0.5
                    while foulShots > 0:
                        if random.random() <= ftCutoff:
                            msg = "Free throw coming up... good!"
                            t1pts += 1
                            team_one.Stats.AddPoints(
                                1, possessionNum, halftime_point, is_ot
                            )
                            team_one.Stats.CalculateLead(1, t1pts - t2pts)
                            shooter.Stats.AddFTMade()
                            team_one.Stats.AddFreeThrow(True)
                            foulShots -= 1
                            collector.AppendPlay(
                                possession,
                                msg,
                                "FreeThrow",
                                t1pts,
                                t2pts,
                                possessionNum,
                                total_possessions,
                            )
                            if foulShots == 0:
                                possession = t2
                        else:
                            play = "Free throw coming up... rattled out."
                            shooter.Stats.AddFTAttempt()
                            team_one.Stats.AddFreeThrow(False)
                            foulShots -= 1
                            if foulShots == 0:
                                rebrand = random.random()
                                if rebrand < t1OffensiveRebound:
                                    pickt1Rebounder = random.choices(
                                        gett1Players,
                                        weights=[
                                            x.ReboundingPer for x in team_one_roster
                                        ],
                                        k=1,
                                    )
                                    t1rebounder = pickt1Rebounder[0]
                                    team_one.Stats.AddRebound(True)
                                    t1rebounder.Stats.AddRebound(True)
                                    printt1Rebounder = (
                                        t1rebounder.FirstName
                                        + " "
                                        + t1rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t1
                                        + " "
                                        + printt1Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t1
                                else:
                                    pickt2Rebounder = random.choices(
                                        gett2Players,
                                        weights=[
                                            x.ReboundingPer for x in team_two_roster
                                        ],
                                        k=1,
                                    )
                                    t2rebounder = pickt2Rebounder[0]
                                    t2rebounder.Stats.AddRebound(False)
                                    team_two.Stats.AddRebound(False)
                                    printt2Rebounder = (
                                        t2rebounder.FirstName
                                        + " "
                                        + t2rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t2
                                        + " "
                                        + printt2Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t2
                elif eventOutcome < made3foulCutoff:
                    play = (
                        printShooter
                        + " 3-point attempt...Score! Fouled on the play... and one!"
                    )
                    t1pts += 3
                    shooter.Stats.AddFieldGoal(True, 3)
                    team_one.Stats.AddThreePointShot(True)
                    team_one.Stats.AddPoints(
                        3, possessionNum, total_possessions / 2, is_ot
                    )
                    team_one.Stats.CalculateLead(3, t1pts - t2pts)
                    assistRand = random.random()
                    if assistRand > 0.173:
                        assistList = [x for x in gett1Players if x.ID != shooter.ID]
                        pickAssister = random.choices(
                            assistList, weights=t1roster_df["assistper"], k=1
                        )
                        assister = pickAssister[0]
                        if assister.ID != shooter.ID:
                            assister.Stats.AddAssist()
                            team_one.Stats.AddAssist()
                            printAssister = assister.FirstName + " " + assister.LastName
                            play += "       Assisted by: " + printAssister
                    collector.AppendPlay(
                        possession,
                        play,
                        "Score",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                    foulShots = 1
                    ftCutoff = (0.02 * shooter.FreeThrow) + 0.5
                    while foulShots > 0:
                        if random.random() <= ftCutoff:
                            msg = "Free throw coming up... good!"
                            shooter.Stats.AddFTMade()
                            team_one.Stats.AddFreeThrow(True)
                            team_one.Stats.AddPoints(
                                1, possessionNum, halftime_point, is_ot
                            )
                            t1pts += 1
                            team_one.Stats.CalculateLead(1, t1pts - t2pts)
                            foulShots -= 1
                            collector.AppendPlay(
                                possession,
                                msg,
                                "FreeThrow",
                                t1pts,
                                t2pts,
                                possessionNum,
                                total_possessions,
                            )
                        else:
                            msg = "Free throw coming up... rattled out."
                            shooter.Stats.AddFTAttempt()
                            team_one.Stats.AddFreeThrow(False)
                            foulShots -= 1
                            collector.AppendPlay(
                                possession,
                                msg,
                                "FreeThrow",
                                t1pts,
                                t2pts,
                                possessionNum,
                                total_possessions,
                            )
                    if foulShots == 0:
                        possession = t2
            elif possrand < t1twoJumperCutoff:
                pickPlayer = random.choices(
                    gett1Players, weights=[x.MidUsage for x in team_one_roster], k=1
                )
                shooter = pickPlayer[0]
                shooter.Stats.AddPossession()
                printShooter = shooter.FirstName + " " + shooter.LastName
                blockAdj = (0.00001 * t2_adj_interior_defense) - 0.0153
                made2jnf = 0
                if shooter.ID == t2team_df["FocusPlayer"]:
                    made2jnf = (0.006 * shooter.Shooting2) - 4 + 0.185 + HCA
                else:
                    made2jnf = (0.006 * shooter.Shooting2) + 0.185 + HCA
                madeDiff = made2jnf - 0.335
                missed2jnf = 0.53 - madeDiff - blockAdj
                made2jfoul = 0.01
                missed2jfoul = 0.02
                blocked = 0.07 + blockAdj
                base2jCutoff = 0
                made2jCutoff = base2jCutoff + made2jnf
                missed2jCutoff = made2jCutoff + missed2jnf
                blocked2jCutoff = missed2jCutoff + blocked
                missed2jfoulCutoff = blocked2jCutoff + missed2jfoul
                made2jfoulCutoff = missed2jfoulCutoff + made2jfoul
                eventOutcome = random.random()
                if eventOutcome < made2jCutoff:
                    play = printShooter + " 2-point jumper...Score!"
                    t1pts += 2
                    shooter.Stats.AddFieldGoal(True, 2)
                    team_one.Stats.AddFieldGoal(True)
                    team_one.Stats.AddPoints(2, possessionNum, halftime_point, is_ot)
                    team_one.Stats.CalculateLead(2, t1pts - t2pts)
                    assistRand = random.random()
                    if assistRand > 0.678:
                        assistList = [x for x in gett1Players if x.ID != shooter.ID]
                        pickAssister = random.choices(
                            assistList, weights=[x.AssistPer for x in assistList], k=1
                        )
                        assister = pickAssister[0]
                        if assister.ID != shooter.ID:
                            assister.Stats.AddAssist()
                            team_one.Stats.AddAssist()
                            printAssister = assister.FirstName + " " + assister.LastName
                            play += "       Assisted by: " + printAssister
                    collector.AppendPlay(
                        possession,
                        play,
                        "Score",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                    possession = t2
                elif eventOutcome < missed2jCutoff:
                    play = printShooter + " 2-point jumper...Missed!"
                    shooter.Stats.AddFieldGoal(False, 2)
                    team_one.Stats.AddFieldGoal(False)
                    rebrand = random.random()
                    if rebrand < t1OffensiveRebound:
                        pickt1Rebounder = random.choices(
                            gett1Players,
                            weights=[x.ReboundingPer for x in team_one_roster],
                            k=1,
                        )
                        t1rebounder = pickt1Rebounder[0]
                        t1rebounder.Stats.AddRebound(True)
                        team_one.Stats.AddRebound(True)
                        printt1Rebounder = (
                            t1rebounder.FirstName + " " + t1rebounder.LastName
                        )
                        play += (
                            "       Rebounded by " + t1 + " " + printt1Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            play,
                            "Missed",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t1
                    else:
                        pickt2Rebounder = random.choices(
                            gett2Players,
                            weights=[x.ReboundingPer for x in team_two_roster],
                            k=1,
                        )
                        t2rebounder = pickt2Rebounder[0]
                        t2rebounder.Stats.AddRebound(False)
                        team_two.Stats.AddRebound(False)
                        printt2Rebounder = (
                            t2rebounder.FirstName + " " + t2rebounder.LastName
                        )
                        play += (
                            "       Rebounded by " + t2 + " " + printt2Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            play,
                            "Missed",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t2
                elif eventOutcome < blocked2jCutoff:
                    pickBlocker = random.choices(
                        gett2Players,
                        weights=[x.DefensePer for x in team_two_roster],
                        k=1,
                    )
                    blocker = pickBlocker[0]
                    shooter.Stats.AddFieldGoal(False, 2)
                    team_one.Stats.AddFieldGoal(False)
                    team_two.Stats.AddBlocks()
                    blocker.Stats.AddBlock()
                    printBlocker = blocker.FirstName + " " + blocker.LastName
                    play = (
                        printShooter
                        + " 2-point jumper...BLOCKED by "
                        + t2
                        + " "
                        + printBlocker
                        + "."
                    )
                    rebrand = random.random()
                    if rebrand < 0.43:
                        pickt1Rebounder = random.choices(
                            gett1Players,
                            weights=[x.ReboundingPer for x in team_one_roster],
                            k=1,
                        )
                        t1rebounder = pickt1Rebounder[0]
                        t1rebounder.Stats.AddRebound(True)
                        team_one.Stats.AddRebound(True)
                        printt1Rebounder = (
                            t1rebounder.FirstName + " " + t1rebounder.LastName
                        )
                        play += (
                            "       Rebounded by " + t1 + " " + printt1Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            play,
                            "Turnover",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t1
                    else:
                        pickt2Rebounder = random.choices(
                            gett2Players,
                            weights=[x.ReboundingPer for x in team_two_roster],
                            k=1,
                        )
                        t2rebounder = pickt2Rebounder[0]
                        t2rebounder.Stats.AddRebound(False)
                        team_two.Stats.AddRebound(False)
                        team_one.Stats.AddTurnover()
                        shooter.Stats.AddTurnover()
                        printt2Rebounder = (
                            t2rebounder.FirstName + " " + t2rebounder.LastName
                        )
                        play += (
                            "       Rebounded by " + t2 + " " + printt2Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            play,
                            "Turnover",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t2
                elif eventOutcome < missed2jfoulCutoff:
                    msg = (
                        printShooter
                        + " 2-point jumper... Missed with a foul on the play."
                    )
                    shooter.Stats.AddFieldGoal(False, 2)
                    team_one.Stats.AddFieldGoal(False)
                    team_two.Stats.AddFoul()
                    foulShots = 2
                    ftCutoff = (0.02 * shooter.FreeThrow) + 0.5
                    while foulShots > 0:
                        if random.random() <= ftCutoff:
                            play = "       Free throw coming up... good!"
                            t1pts += 1
                            shooter.Stats.AddFTMade()
                            team_one.Stats.AddFreeThrow(True)
                            team_one.Stats.AddPoints(
                                1, possessionNum, halftime_point, is_ot
                            )
                            collector.AppendPlay(
                                possession,
                                msg,
                                "FreeThrow",
                                t1pts,
                                t2pts,
                                possessionNum,
                                total_possessions,
                            )
                            foulShots -= 1
                            if foulShots == 0:
                                possession = t2
                        else:
                            play = "       Free throw coming up... rattled out."
                            shooter.Stats.AddFTAttempt()
                            team_one.Stats.AddFreeThrow(False)
                            foulShots -= 1
                            if foulShots == 0:
                                rebrand = random.random()
                                if rebrand < t1OffensiveRebound:
                                    pickt1Rebounder = random.choices(
                                        gett1Players,
                                        weights=[
                                            x.ReboundingPer for x in team_one_roster
                                        ],
                                        k=1,
                                    )
                                    t1rebounder = pickt1Rebounder[0]
                                    t1rebounder.Stats.AddRebound(True)
                                    team_one.Stats.AddRebound(True)
                                    printt1Rebounder = (
                                        t1rebounder.FirstName
                                        + " "
                                        + t1rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t1
                                        + " "
                                        + printt1Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "Turnover",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t1
                                else:
                                    pickt2Rebounder = random.choices(
                                        gett2Players,
                                        weights=[
                                            x.ReboundingPer for x in team_two_roster
                                        ],
                                        k=1,
                                    )
                                    t2rebounder = pickt2Rebounder[0]
                                    t2rebounder.Stats.AddRebound(False)
                                    team_two.Stats.AddRebound(False)
                                    printt2Rebounder = (
                                        t2rebounder.FirstName
                                        + " "
                                        + t2rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t2
                                        + " "
                                        + printt2Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "Turnover",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t2
                elif eventOutcome < made2jfoulCutoff:
                    msg = (
                        printShooter
                        + " 2-point jumper...Score! Foul on the play and one!"
                    )
                    t1pts += 2
                    shooter.Stats.AddFieldGoal(True, 2)
                    team_one.Stats.AddFieldGoal(True)
                    team_one.Stats.AddPoints(2, possessionNum, halftime_point, is_ot)
                    team_one.Stats.CalculateLead(2, t1pts - t2pts)
                    team_two.Stats.AddFoul()
                    assistRand = random.random()
                    if assistRand > 0.678:
                        assistList = [x for x in gett1Players if x.ID != shooter.ID]
                        pickAssister = random.choices(
                            assistList, weights=[x.AssistPer for x in assistList], k=1
                        )
                        assister = pickAssister[0]
                        if assister.ID != shooter.ID:
                            assister.Stats.AddAssist()
                            team_one.Stats.AddAssist()
                            printAssister = assister.FirstName + " " + assister.LastName
                            msg += "       Assisted by: " + printAssister
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Score",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                    foulShots = 1
                    ftCutoff = (0.02 * shooter.FreeThrow) + 0.5
                    while foulShots > 0:
                        if random.random() <= ftCutoff:
                            play = "Free throw coming up... good!"
                            t1pts += 1
                            shooter.Stats.AddFTMade()
                            team_one.Stats.AddFreeThrow(True)
                            team_one.Stats.AddPoints(
                                1, possessionNum, halftime_point, is_ot
                            )
                            team_one.Stats.CalculateLead(1, t1pts - t2pts)
                            collector.AppendPlay(
                                possession,
                                play,
                                "FreeThrow",
                                t1pts,
                                t2pts,
                                possessionNum,
                                total_possessions,
                            )
                            foulShots -= 1
                            if foulShots == 0:
                                possession = t2
                        else:
                            play = "       Free throw coming up... rattled out."
                            shooter.Stats.AddFTAttempt()
                            team_one.Stats.AddFreeThrow(False)
                            foulShots -= 1
                            if foulShots == 0:
                                rebrand = random.random()
                                if rebrand < t1OffensiveRebound:
                                    pickt1Rebounder = random.choices(
                                        gett1Players,
                                        weights=[
                                            x.ReboundingPer for x in team_one_roster
                                        ],
                                        k=1,
                                    )
                                    t1rebounder = pickt1Rebounder[0]
                                    t1rebounder.Stats.AddRebound(True)
                                    team_one.Stats.AddRebound(True)
                                    printt1Rebounder = (
                                        t1rebounder.FirstName
                                        + " "
                                        + t1rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t1
                                        + " "
                                        + printt1Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t1
                                else:
                                    pickt2Rebounder = random.choices(
                                        gett2Players,
                                        weights=[
                                            x.ReboundingPer for x in team_two_roster
                                        ],
                                        k=1,
                                    )
                                    t2rebounder = pickt2Rebounder[0]
                                    t2rebounder.Stats.AddRebound(False)
                                    team_two.Stats.AddRebound(False)
                                    printt2Rebounder = (
                                        t2rebounder.FirstName
                                        + " "
                                        + t2rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t2
                                        + " "
                                        + printt2Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t2
                            else:
                                collector.AppendPlay(
                                    possession,
                                    play,
                                    "FreeThrow",
                                    t1pts,
                                    t2pts,
                                    possessionNum,
                                    total_possessions,
                                )
            elif possrand < t1twoInsideCutoff:
                pickPlayer = random.choices(
                    gett1Players, weights=[x.InsideUsage for x in team_one_roster], k=1
                )
                shooter = pickPlayer[0]
                shooter.Stats.AddPossession()
                printShooter = shooter.FirstName + " " + shooter.LastName
                blockAdj = (0.00001 * t2_adj_interior_defense) - 0.0153
                if shooter.ID == t2team_df["FocusPlayer"]:
                    made2inf = (0.005 * shooter.Finishing) - 4 + 0.185 + HCA
                else:
                    made2inf = (0.005 * shooter.Finishing) + 0.185 + HCA
                madeDiff = made2inf - 0.563
                missed2inf = 0.147 - madeDiff - blockAdj
                made2ifoul = 0.05
                missed2ifoul = 0.14
                blocked = 0.1 + blockAdj
                base2iCutoff = 0
                made2iCutoff = base2iCutoff + made2inf
                missed2iCutoff = made2iCutoff + missed2inf
                blocked2iCutoff = missed2iCutoff + blocked
                missed2ifoulCutoff = blocked2iCutoff + missed2ifoul
                made2ifoulCutoff = missed2ifoulCutoff + made2ifoul
                eventOutcome = random.random()
                if eventOutcome < made2iCutoff:
                    play = printShooter + " Inside shot...Score!"
                    shooter.Stats.AddFieldGoal(True, 2)
                    team_one.Stats.AddFieldGoal(True)
                    t1pts += 2
                    assistRand = random.random()
                    if assistRand > 0.57:
                        assistList = [x for x in gett1Players if x.ID != shooter.ID]
                        pickAssister = random.choices(
                            assistList, weights=[x.AssistPer for x in assistList], k=1
                        )
                        assister = pickAssister[0]
                        if assister.ID != shooter.ID:
                            assister.Stats.AddAssist()
                            team_one.Stats.AddAssist()
                            printAssister = assister.FirstName + " " + assister.LastName
                            play += "       Assisted by: " + printAssister
                    collector.AppendPlay(
                        possession,
                        play,
                        "Score",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                    possession = t2
                elif eventOutcome < missed2iCutoff:
                    play = printShooter + " Inside shot...Missed!"
                    shooter.Stats.AddFieldGoal(False, 2)
                    team_one.Stats.AddFieldGoal(False)
                    rebrand = random.random()
                    if rebrand < t1OffensiveRebound:
                        pickt1Rebounder = random.choices(
                            gett1Players,
                            weights=[x.ReboundingPer for x in team_one_roster],
                            k=1,
                        )
                        t1rebounder = pickt1Rebounder[0]
                        t1rebounder.Stats.AddRebound(True)
                        team_one.Stats.AddRebound(True)
                        printt1Rebounder = (
                            t1rebounder.FirstName + " " + t1rebounder.LastName
                        )
                        play += (
                            "       Rebounded by " + t1 + " " + printt1Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            play,
                            "Score",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t1
                    else:
                        pickt2Rebounder = random.choices(
                            gett2Players,
                            weights=[x.ReboundingPer for x in team_two_roster],
                            k=1,
                        )
                        t2rebounder = pickt2Rebounder[0]
                        printt2Rebounder = (
                            t2rebounder.FirstName + " " + t2rebounder.LastName
                        )
                        play += (
                            "       Rebounded by " + t2 + " " + printt2Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            play,
                            "Score",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t2
                        t2rebounder.Stats.AddRebound(False)
                        team_two.Stats.AddRebound(False)
                elif eventOutcome < blocked2iCutoff:
                    pickBlocker = random.choices(
                        gett2Players,
                        weights=[x.DefensePer for x in team_two_roster],
                        k=1,
                    )
                    blocker = pickBlocker[0]
                    blocker.Stats.AddBlock()
                    printBlocker = blocker.FirstName + " " + blocker.LastName
                    play = (
                        printShooter
                        + " Inside shot...BLOCKED by "
                        + t2
                        + " "
                        + printBlocker
                        + "."
                    )
                    rebrand = random.random()
                    if rebrand < 0.43:
                        pickt1Rebounder = random.choices(
                            gett1Players,
                            weights=[x.ReboundingPer for x in team_one_roster],
                            k=1,
                        )
                        t1rebounder = pickt1Rebounder[0]
                        t1rebounder.Stats.AddRebound(True)
                        team_one.Stats.AddRebound(True)
                        printt1Rebounder = (
                            t1rebounder.FirstName + " " + t1rebounder.LastName
                        )
                        play += (
                            "       Rebounded by " + t1 + " " + printt1Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            play,
                            "Turnover",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t1
                    else:
                        pickt2Rebounder = random.choices(
                            gett2Players,
                            weights=[x.ReboundingPer for x in team_two_roster],
                            k=1,
                        )
                        t2rebounder = pickt2Rebounder[0]
                        t2rebounder.Stats.AddRebound(False)
                        team_two.Stats.AddRebound(False)
                        shooter.Stats.AddTurnover()
                        team_one.Stats.AddTurnover()
                        printt2Rebounder = (
                            t2rebounder.FirstName + " " + t2rebounder.LastName
                        )
                        play += (
                            "       Rebounded by " + t2 + " " + printt2Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            play,
                            "Turnover",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t2
                elif eventOutcome < missed2ifoulCutoff:
                    msg = (
                        printShooter + " Inside shot... Missed with a foul on the play."
                    )
                    shooter.Stats.AddFieldGoal(False, 2)
                    team_one.Stats.AddFieldGoal(False)
                    team_two.Stats.AddFoul()
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Fouled",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                    foulShots = 2
                    ftCutoff = (0.02 * shooter.FreeThrow) + 0.5
                    while foulShots > 0:
                        if random.random() <= ftCutoff:
                            msg = "Free throw coming up... good!"
                            shooter.Stats.AddFTMade()
                            team_one.Stats.AddFreeThrow(True)
                            t1pts += 1
                            team_one.Stats.AddPoints(
                                1, possessionNum, halftime_point, is_ot
                            )
                            team_one.Stats.CalculateLead(1, t1pts - t2pts)
                            foulShots -= 1
                            collector.AppendPlay(
                                possession,
                                msg,
                                "FreeThrow",
                                t1pts,
                                t2pts,
                                possessionNum,
                                total_possessions,
                            )
                            if foulShots == 0:
                                possession = t2
                        else:
                            play = "Free throw coming up... rattled out."
                            shooter.Stats.AddFTAttempt()
                            team_one.Stats.AddFreeThrow(False)
                            foulShots -= 1
                            if foulShots == 0:
                                rebrand = random.random()
                                if rebrand < t1OffensiveRebound:
                                    pickt1Rebounder = random.choices(
                                        gett1Players,
                                        weights=[
                                            x.ReboundingPer for x in team_one_roster
                                        ],
                                        k=1,
                                    )
                                    t1rebounder = pickt1Rebounder[0]
                                    t1rebounder.Stats.AddRebound(True)
                                    team_one.Stats.AddRebound(True)
                                    printt1Rebounder = (
                                        t1rebounder.FirstName
                                        + " "
                                        + t1rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t1
                                        + " "
                                        + printt1Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t1
                                else:
                                    pickt2Rebounder = random.choices(
                                        gett2Players,
                                        weights=[
                                            x.ReboundingPer for x in team_two_roster
                                        ],
                                        k=1,
                                    )
                                    t2rebounder = pickt2Rebounder[0]
                                    t2rebounder.Stats.AddRebound(False)
                                    team_two.Stats.AddRebound(False)
                                    printt2Rebounder = (
                                        t2rebounder.FirstName
                                        + " "
                                        + t2rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t2
                                        + " "
                                        + printt2Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t2
                elif eventOutcome < made2ifoulCutoff:
                    msg = (
                        printShooter + " Inside shot...Score! Foul on the play and one!"
                    )
                    t1pts += 2
                    shooter.Stats.AddFieldGoal(True, 2)
                    team_one.Stats.AddFieldGoal(True)
                    team_one.Stats.AddPoints(2, possessionNum, halftime_point, is_ot)
                    team_one.Stats.CalculateLead(2, t1pts - t2pts)
                    team_two.Stats.AddFoul()
                    assistRand = random.random()
                    if assistRand > 0.57:
                        assistList = [x for x in gett1Players if x.ID != shooter.ID]
                        pickAssister = random.choices(
                            assistList, weights=[x.AssistPer for x in assistList], k=1
                        )
                        assister = pickAssister[0]
                        if assister.ID != shooter.ID:
                            assister.Stats.AddAssist()
                            team_one.Stats.AddAssist()
                            printAssister = assister.FirstName + " " + assister.LastName
                            msg += "       Assisted by: " + printAssister
                    foulShots = 1
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Score",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                    ftCutoff = (0.02 * shooter.FreeThrow) + 0.5
                    while foulShots > 0:
                        if random.random() <= ftCutoff:
                            play = "Free throw coming up... good!"
                            t1pts += 1
                            shooter.Stats.AddFTMade()
                            team_one.Stats.AddFreeThrow(True)
                            team_one.Stats.AddPoints(
                                1, possessionNum, halftime_point, is_ot
                            )
                            team_one.Stats.CalculateLead(1, t1pts - t2pts)
                            foulShots -= 1
                            collector.AppendPlay(
                                possession,
                                play,
                                "FreeThrow",
                                t1pts,
                                t2pts,
                                possessionNum,
                                total_possessions,
                            )
                            if foulShots == 0:
                                possession = t2
                        else:
                            play = "Free throw coming up... rattled out."
                            shooter.Stats.AddFTAttempt()
                            team_one.Stats.AddFreeThrow(False)
                            foulShots -= 1
                            if foulShots == 0:
                                rebrand = random.random()
                                if rebrand < t1OffensiveRebound:
                                    pickt1Rebounder = random.choices(
                                        gett1Players,
                                        weights=[
                                            x.ReboundingPer for x in team_one_roster
                                        ],
                                        k=1,
                                    )
                                    t1rebounder = pickt1Rebounder[0]
                                    t1rebounder.Stats.AddRebound(True)
                                    team_one.Stats.AddRebound(True)
                                    printt1Rebounder = (
                                        t1rebounder.FirstName
                                        + " "
                                        + t1rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t1
                                        + " "
                                        + printt1Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t1
                                else:
                                    pickt2Rebounder = random.choices(
                                        gett2Players,
                                        weights=[
                                            x.ReboundingPer for x in team_two_roster
                                        ],
                                        k=1,
                                    )
                                    t2rebounder = pickt2Rebounder[0]
                                    t2rebounder.Stats.AddRebound(False)
                                    team_two.Stats.AddRebound(False)
                                    printt2Rebounder = (
                                        t2rebounder.FirstName
                                        + " "
                                        + t2rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t2
                                        + " "
                                        + printt2Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t2
        elif possession == t2:
            if possrand < t2StealCutoff:
                pickPlayer = random.choices(
                    gett1Players, weights=[x.DefensePer for x in team_one_roster], k=1
                )
                stealPlayer = pickPlayer[0]
                stealPlayer.Stats.AddPossession()
                stealPlayer.Stats.AddSteal()
                team_one.Stats.AddSteal()
                team_two.Stats.AddTurnover()
                printShooter = stealPlayer.FirstName + " " + stealPlayer.LastName
                msg = printShooter + " steals the ball for " + t1 + "!"
                possession = t1
                collector.AppendPlay(
                    possession,
                    msg,
                    "Turnover",
                    t1pts,
                    t2pts,
                    possessionNum,
                    total_possessions,
                )
            elif possrand < t2OtherTOCutoff:
                otherTO = random.random()
                pickPlayer = random.choices(
                    gett2Players, weights=[x.Usage for x in team_two_roster], k=1
                )
                toPlayer = pickPlayer[0]
                toPlayer.Stats.AddPossession()
                printShooter = toPlayer.FirstName + " " + toPlayer.LastName
                toPlayer.Stats.AddTurnover()
                team_two.Stats.AddTurnover()
                if otherTO < 0.582:
                    msg = t2 + " " + printShooter + " lost the ball out of bounds."
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Turnover",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                elif otherTO < 0.64:
                    msg = (
                        possession
                        + ": Shot clock violation on "
                        + t2
                        + " "
                        + printShooter
                        + "."
                    )
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Turnover",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                elif otherTO < 1:
                    msg = (
                        possession
                        + ": Offensive foul on "
                        + t2
                        + " "
                        + printShooter
                        + "."
                    )
                    toPlayer.Stats.AddFoul()
                    team_two.Stats.AddFoul()
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Turnover",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                possession = t1
            elif possrand < t2threeptAttemptCutoff:
                pickPlayer = random.choices(
                    gett2Players,
                    weights=[x.ThreePointUsage for x in team_two_roster],
                    k=1,
                )
                shooter = pickPlayer[0]
                printShooter = shooter.FirstName + " " + shooter.LastName
                shooter.Stats.AddPossession()
                blockAdj = (0.00001 * t1_adj_perimeter_defense) - 0.0153
                made3nf = 0
                if shooter.ID == t1team_df["FocusPlayer"]:
                    made3nf = (0.015 * shooter.Shooting3) - 4 + 0.185 + HCA
                else:
                    made3nf = (0.015 * shooter.Shooting3) + 0.185 + HCA
                madeDiff = made3nf - 0.335
                missed3nf = 0.635 - madeDiff - blockAdj
                made3foul = 0.005
                missed3foul = 0.015
                blocked = 0.01 + blockAdj
                base3Cutoff = 0
                made3Cutoff = base3Cutoff + made3nf
                missed3Cutoff = made3Cutoff + missed3nf
                blocked3Cutoff = missed3Cutoff + blocked
                missed3foulCutoff = blocked3Cutoff + missed3foul
                made3foulCutoff = missed3foulCutoff + made3foul
                eventOutcome = random.random()
                if eventOutcome < made3Cutoff:
                    msg = printShooter + " 3-point attempt...Score!"
                    shooter.Stats.AddFieldGoal(True, 3)
                    team_two.Stats.AddThreePointShot(True)
                    team_two.Stats.AddPoints(3, possessionNum, halftime_point, is_ot)
                    team_two.Stats.CalculateLead(3, t2pts - t1pts)
                    t2pts += 3
                    assistRand = random.random()
                    if assistRand > 0.173:
                        assistList = [x for x in gett2Players if x.ID != shooter.ID]
                        pickAssister = random.choices(
                            assistList, weights=[x.AssistPer for x in assistList], k=1
                        )
                        assister = pickAssister[0]
                        if assister.ID != shooter.ID:
                            assister.Stats.AddAssist()
                            team_two.Stats.AddAssist()
                            printAssister = assister.FirstName + " " + assister.LastName
                            msg += "       Assisted by: " + printAssister
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Score",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                    possession = t1
                elif eventOutcome < missed3Cutoff:
                    shooter.Stats.AddFieldGoal(False, 3)
                    team_two.Stats.AddThreePointShot(False)
                    msg = printShooter + " 3-point attempt...Missed!"
                    rebrand = random.random()
                    if rebrand < t2OffensiveRebound:
                        pickt2Rebounder = random.choices(
                            gett2Players,
                            weights=[x.ReboundingPer for x in team_two_roster],
                            k=1,
                        )
                        t2rebounder = pickt2Rebounder[0]
                        t2rebounder.Stats.AddRebound(True)
                        team_two.Stats.AddRebound(True)
                        printt2Rebounder = (
                            t2rebounder.FirstName + " " + t2rebounder.LastName
                        )
                        msg += (
                            "       Rebounded by " + t2 + " " + printt2Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            msg,
                            "Score",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t2
                    else:
                        pickt1Rebounder = random.choices(
                            gett1Players,
                            weights=[x.ReboundingPer for x in team_one_roster],
                            k=1,
                        )
                        t1rebounder = pickt1Rebounder[0]
                        t1rebounder.Stats.AddRebound(False)
                        team_one.Stats.AddRebound(False)
                        printt1Rebounder = (
                            t1rebounder.FirstName + " " + t1rebounder.LastName
                        )
                        msg += "Rebounded by " + t1 + " " + printt1Rebounder + "."
                        collector.AppendPlay(
                            possession,
                            msg,
                            "Score",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t1
                elif eventOutcome < blocked3Cutoff:
                    pickBlocker = random.choices(
                        gett1Players,
                        weights=[x.DefensePer for x in team_one_roster],
                        k=1,
                    )
                    blocker = pickBlocker[0]
                    blocker.Stats.AddBlock()
                    team_one.Stats.AddBlocks()
                    shooter.Stats.AddTurnover()
                    shooter.Stats.AddFieldGoal(False, 3)
                    team_two.Stats.AddThreePointShot(False)
                    printBlocker = blocker.FirstName + " " + blocker.LastName
                    rebrand = random.random()
                    if rebrand < 0.43:
                        pickt2Rebounder = random.choices(
                            gett2Players,
                            weights=[x.ReboundingPer for x in team_two_roster],
                            k=1,
                        )
                        t2rebounder = pickt2Rebounder[0]
                        t2rebounder.Stats.AddRebound(True)
                        team_two.Stats.AddRebound(True)
                        printt2Rebounder = (
                            t2rebounder.FirstName + " " + t2rebounder.LastName
                        )
                        msg += (
                            "       Rebounded by " + t2 + " " + printt2Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            msg,
                            "Score",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t2
                    else:
                        pickt1Rebounder = random.choices(
                            gett1Players,
                            weights=[x.ReboundingPer for x in team_one_roster],
                            k=1,
                        )
                        t1rebounder = pickt1Rebounder[0]
                        t1rebounder.Stats.AddRebound(False)
                        team_one.Stats.AddRebound(False)
                        printt1Rebounder = (
                            t1rebounder.FirstName + " " + t1rebounder.LastName
                        )
                        msg += "Rebounded by " + t1 + " " + printt1Rebounder + "."
                        collector.AppendPlay(
                            possession,
                            msg,
                            "Score",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t1
                elif eventOutcome < missed3foulCutoff:
                    msg = (
                        printShooter
                        + " 3-point attempt... Missed with a foul on the play."
                    )
                    shooter.Stats.AddFieldGoal(False, 3)
                    team_two.Stats.AddThreePointShot(False)
                    team_one.Stats.AddFoul()
                    foulShots = 3
                    ftCutoff = (0.02 * shooter.FreeThrow) + 0.5
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Fouled",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                    while foulShots > 0:
                        if random.random() <= ftCutoff:
                            play = "       Free throw coming up... good!"
                            t2pts += 1
                            shooter.Stats.AddFTMade()
                            team_two.Stats.AddFreeThrow(True)
                            team_two.Stats.AddPoints(
                                1, possessionNum, halftime_point, is_ot
                            )
                            team_two.Stats.CalculateLead(1, t2pts - t1pts)
                            collector.AppendPlay(
                                possession,
                                play,
                                "FreeThrow",
                                t1pts,
                                t2pts,
                                possessionNum,
                                total_possessions,
                            )
                            foulShots -= 1
                            if foulShots == 0:
                                possession = t1
                        else:
                            play = "       Free throw coming up... rattled out."
                            shooter.Stats.AddFTAttempt()
                            team_two.Stats.AddFreeThrow(False)
                            foulShots -= 1
                            if foulShots == 0:
                                rebrand = random.random()
                                if rebrand < t2OffensiveRebound:
                                    pickt2Rebounder = random.choices(
                                        gett2Players,
                                        weights=[
                                            x.ReboundingPer for x in team_two_roster
                                        ],
                                        k=1,
                                    )
                                    t2rebounder = pickt2Rebounder[0]
                                    t2rebounder.Stats.AddRebound(True)
                                    team_two.Stats.AddRebound(True)
                                    printt2Rebounder = (
                                        t2rebounder.FirstName
                                        + " "
                                        + t2rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t2
                                        + " "
                                        + printt2Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        msg,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t2
                                else:
                                    pickt1Rebounder = random.choices(
                                        gett1Players,
                                        weights=[
                                            x.ReboundingPer for x in team_one_roster
                                        ],
                                        k=1,
                                    )
                                    t1rebounder = pickt1Rebounder[0]
                                    t1rebounder.Stats.AddRebound(False)
                                    team_one.Stats.AddRebound(False)
                                    printt1Rebounder = (
                                        t1rebounder.FirstName
                                        + " "
                                        + t1rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t1
                                        + " "
                                        + printt1Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        msg,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t1
                elif eventOutcome < made3foulCutoff:
                    msg = (
                        printShooter
                        + " 3-point attempt...Score! There is a foul on the play and one!"
                    )
                    t2pts += 3
                    shooter.Stats.AddFieldGoal(True, 3)
                    team_two.Stats.AddThreePointShot(True)
                    team_two.Stats.AddPoints(3, possessionNum, halftime_point, is_ot)
                    team_two.Stats.CalculateLead(3, t2pts - t1pts)
                    team_one.Stats.AddFoul()
                    assistRand = random.random()
                    if assistRand > 0.173:
                        assistList = [x for x in gett2Players if x.ID != shooter.ID]
                        pickAssister = random.choices(
                            assistList, weights=[x.AssistPer for x in assistList], k=1
                        )
                        assister = pickAssister[0]
                        if assister.ID != shooter.ID:
                            assister.Stats.AddAssist()
                            team_two.Stats.AddAssist()
                            printAssister = assister.FirstName + " " + assister.LastName
                        msg += "       Assisted by: " + printAssister
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Score",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                    foulShots = 1
                    ftCutoff = (0.02 * shooter.FreeThrow) + 0.5
                    while foulShots > 0:
                        if random.random() <= ftCutoff:
                            play = "Free throw coming up... good!"
                            t2pts += 1
                            shooter.Stats.AddFTMade()
                            team_two.Stats.AddFreeThrow(True)
                            team_two.Stats.AddPoints(
                                1, possessionNum, halftime_point, is_ot
                            )
                            team_two.Stats.CalculateLead(1, t2pts - t1pts)
                            foulShots -= 1
                            collector.AppendPlay(
                                possession,
                                play,
                                "Score",
                                t1pts,
                                t2pts,
                                possessionNum,
                                total_possessions,
                            )
                            if foulShots == 0:
                                possession = t1
                        else:
                            play = "Free throw coming up... rattled out."
                            shooter.Stats.AddFTAttempt()
                            team_two.Stats.AddFreeThrow(False)
                            foulShots -= 1
                            if foulShots == 0:
                                rebrand = random.random()
                                if rebrand < t2OffensiveRebound:
                                    pickt2Rebounder = random.choices(
                                        gett2Players,
                                        weights=[
                                            x.ReboundingPer for x in team_two_roster
                                        ],
                                        k=1,
                                    )
                                    t2rebounder = pickt2Rebounder[0]
                                    t2rebounder.Stats.AddRebound(True)
                                    team_two.Stats.AddRebound(True)
                                    printt2Rebounder = (
                                        t2rebounder.FirstName
                                        + " "
                                        + t2rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t2
                                        + " "
                                        + printt2Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t2
                                else:
                                    pickt1Rebounder = random.choices(
                                        gett1Players,
                                        weights=[
                                            x.ReboundingPer for x in team_one_roster
                                        ],
                                        k=1,
                                    )
                                    t1rebounder = pickt1Rebounder[0]
                                    t1rebounder.Stats.AddRebound(False)
                                    team_one.Stats.AddRebound(False)
                                    printt1Rebounder = (
                                        t1rebounder.FirstName
                                        + " "
                                        + t1rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t1
                                        + " "
                                        + printt1Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t1
            elif possrand < t2twoJumperCutoff:
                pickPlayer = random.choices(
                    gett2Players, weights=[x.MidUsage for x in team_two_roster], k=1
                )
                shooter = pickPlayer[0]
                shooter.Stats.AddPossession()
                printShooter = shooter.FirstName + " " + shooter.LastName
                blockAdj = (0.00001 * t1_adj_interior_defense) - 0.0153
                if shooter.ID == t1team_df["FocusPlayer"]:
                    made2jnf = (0.006 * shooter.Shooting2) - 4 + 0.185 + HCA
                else:
                    made2jnf = (0.006 * shooter.Shooting2) + 0.185 + HCA
                madeDiff = made2jnf - 0.335
                missed2jnf = 0.53 - madeDiff - blockAdj
                made2jfoul = 0.01
                missed2jfoul = 0.02
                blocked = 0.07 + blockAdj
                base2jCutoff = 0
                made2jCutoff = base2jCutoff + made2jnf
                missed2jCutoff = made2jCutoff + missed2jnf
                blocked2jCutoff = missed2jCutoff + blocked
                missed2jfoulCutoff = blocked2jCutoff + missed2jfoul
                made2jfoulCutoff = missed2jfoulCutoff + made2jfoul
                eventOutcome = random.random()
                if eventOutcome < made2jCutoff:
                    msg = printShooter + " 2-point jumper...Score!"
                    t2pts += 2
                    shooter.Stats.AddFieldGoal(True, 2)
                    team_two.Stats.AddFieldGoal(True)
                    team_two.Stats.AddPoints(2, possessionNum, halftime_point, is_ot)
                    team_two.Stats.CalculateLead(2, t2pts - t1pts)
                    assistRand = random.random()
                    if assistRand > 0.678:
                        assistList = [x for x in gett2Players if x.ID != shooter.ID]
                        pickAssister = random.choices(
                            assistList, weights=[x.AssistPer for x in assistList], k=1
                        )
                        assister = pickAssister[0]
                        if assister.ID != shooter.ID:
                            assister.Stats.AddAssist()
                            team_two.Stats.AddAssist()
                            printAssister = assister.FirstName + " " + assister.LastName
                        msg += "       Assisted by: " + printAssister
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Score",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                    possession = t1
                elif eventOutcome < missed2jCutoff:
                    msg = printShooter + " 2-point jumper...Missed!"
                    shooter.Stats.AddFieldGoal(False, 2)
                    team_two.Stats.AddFieldGoal(False)
                    rebrand = random.random()
                    if rebrand < t2OffensiveRebound:
                        pickt2Rebounder = random.choices(
                            gett2Players,
                            weights=[x.ReboundingPer for x in team_two_roster],
                            k=1,
                        )
                        t2rebounder = pickt2Rebounder[0]
                        t2rebounder.Stats.AddRebound(True)
                        team_two.Stats.AddRebound(True)
                        printt2Rebounder = (
                            t2rebounder.FirstName + " " + t2rebounder.LastName
                        )
                        msg += (
                            "       Rebounded by " + t2 + " " + printt2Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            msg,
                            "Score",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t2
                    else:
                        pickt1Rebounder = random.choices(
                            gett1Players,
                            weights=[x.ReboundingPer for x in team_one_roster],
                            k=1,
                        )
                        t1rebounder = pickt1Rebounder[0]
                        t1rebounder.Stats.AddRebound(False)
                        team_one.Stats.AddRebound(False)
                        printt1Rebounder = (
                            t1rebounder.FirstName + " " + t1rebounder.LastName
                        )
                        msg += (
                            "       Rebounded by " + t1 + " " + printt1Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            msg,
                            "Score",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t1
                elif eventOutcome < blocked2jCutoff:
                    pickBlocker = random.choices(
                        gett1Players,
                        weights=[x.DefensePer for x in team_one_roster],
                        k=1,
                    )
                    blocker = pickBlocker[0]
                    blocker.Stats.AddBlock()
                    team_one.Stats.AddBlocks()
                    shooter.Stats.AddTurnover()
                    printBlocker = blocker.FirstName + " " + blocker.LastName
                    msg = (
                        printShooter
                        + " 2-point jumper...BLOCKED by "
                        + printBlocker
                        + "."
                    )
                    rebrand = random.random()
                    if rebrand < 0.43:
                        pickt2Rebounder = random.choices(
                            gett2Players,
                            weights=[x.ReboundingPer for x in team_two_roster],
                            k=1,
                        )
                        t2rebounder = pickt2Rebounder[0]
                        t2rebounder.Stats.AddRebound(True)
                        team_two.Stats.AddRebound(True)
                        printt2Rebounder = (
                            t2rebounder.FirstName + " " + t2rebounder.LastName
                        )
                        msg += (
                            "       Rebounded by " + t2 + " " + printt2Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            msg,
                            "Turnover",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t2
                    else:
                        pickt1Rebounder = random.choices(
                            gett1Players,
                            weights=[x.ReboundingPer for x in team_one_roster],
                            k=1,
                        )
                        t1rebounder = pickt1Rebounder[0]
                        t1rebounder.Stats.AddRebound(False)
                        team_one.Stats.AddRebound(False)
                        printt1Rebounder = (
                            t1rebounder.FirstName + " " + t1rebounder.LastName
                        )
                        msg += (
                            "       Rebounded by " + t1 + " " + printt1Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            msg,
                            "Turnover",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t1
                elif eventOutcome < missed2jfoulCutoff:
                    msg = (
                        printShooter
                        + " 2-point jumper... Missed but there is a foul on the play."
                    )
                    shooter.Stats.AddFieldGoal(False, 2)
                    team_two.Stats.AddFieldGoal(False)
                    team_one.Stats.AddFoul()
                    foulShots = 2
                    ftCutoff = (0.02 * shooter.FreeThrow) + 0.5
                    while foulShots > 0:
                        if random.random() <= ftCutoff:
                            play = "Free throw coming up... good!"
                            t2pts += 1
                            shooter.Stats.AddFTMade()
                            team_two.Stats.AddFreeThrow(True)
                            team_two.Stats.AddPoints(
                                1, possessionNum, halftime_point, is_ot
                            )
                            team_two.Stats.CalculateLead(1, t2pts - t1pts)
                            collector.AppendPlay(
                                possession,
                                play,
                                "FreeThrow",
                                t1pts,
                                t2pts,
                                possessionNum,
                                total_possessions,
                            )
                            foulShots -= 1
                            if foulShots == 0:
                                possession = t1
                        else:
                            play = "Free throw coming up... rattled out."
                            shooter.Stats.AddFTAttempt()
                            team_two.Stats.AddFreeThrow(False)
                            foulShots -= 1
                            if foulShots == 0:
                                rebrand = random.random()
                                if rebrand < t2OffensiveRebound:
                                    pickt2Rebounder = random.choices(
                                        gett2Players,
                                        weights=[
                                            x.ReboundingPer for x in team_two_roster
                                        ],
                                        k=1,
                                    )
                                    t2rebounder = pickt2Rebounder[0]
                                    t2rebounder.Stats.AddRebound(True)
                                    team_two.Stats.AddRebound(True)
                                    printt2Rebounder = (
                                        t2rebounder.FirstName
                                        + " "
                                        + t2rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t2
                                        + " "
                                        + printt2Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "Score",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t2
                                else:
                                    pickt1Rebounder = random.choices(
                                        gett1Players,
                                        weights=[
                                            x.ReboundingPer for x in team_one_roster
                                        ],
                                        k=1,
                                    )
                                    t1rebounder = pickt1Rebounder[0]
                                    t1rebounder.Stats.AddRebound(True)
                                    team_one.Stats.AddRebound(True)
                                    printt1Rebounder = (
                                        t1rebounder.FirstName
                                        + " "
                                        + t1rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t1
                                        + " "
                                        + printt1Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "Score",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t1
                elif eventOutcome < made2jfoulCutoff:
                    msg = (
                        printShooter
                        + " 2-point jumper...Score! Foul on the play and we go to a free throw!"
                    )
                    t2pts += 2
                    shooter.Stats.AddFieldGoal(True, 2)
                    team_two.Stats.AddFieldGoal(True)
                    team_two.Stats.AddPoints(2, possessionNum, halftime_point, is_ot)
                    team_two.Stats.CalculateLead(2, t2pts - t1pts)
                    team_one.Stats.AddFoul()
                    assistRand = random.random()
                    if assistRand > 0.678:
                        assistList = [x for x in gett2Players if x.ID != shooter.ID]
                        pickAssister = random.choices(
                            assistList, weights=[x.AssistPer for x in assistList], k=1
                        )
                        assister = pickAssister[0]
                        if assister.ID != shooter.ID:
                            assister.Stats.AddAssist()
                            team_two.Stats.AddAssist()
                            printAssister = assister.FirstName + " " + assister.LastName
                            msg += "       Assisted by: " + printAssister
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Score",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                    foulShots = 1
                    ftCutoff = (0.02 * shooter.FreeThrow) + 0.5
                    while foulShots > 0:
                        if random.random() <= ftCutoff:
                            play = "Free throw coming up... good!"
                            t2pts += 1
                            shooter.Stats.AddFTMade()
                            team_two.Stats.AddFreeThrow(True)
                            team_two.Stats.AddPoints(
                                1, possessionNum, halftime_point, is_ot
                            )
                            team_two.Stats.CalculateLead(1, t2pts - t1pts)
                            foulShots -= 1
                            if foulShots == 0:
                                possession = t1
                        else:
                            play = "Free throw coming up... rattled out."
                            shooter.Stats.AddFTAttempt()
                            team_two.Stats.AddFreeThrow(False)
                            foulShots -= 1
                            if foulShots == 0:
                                rebrand = random.random()
                                if rebrand < t2OffensiveRebound:
                                    pickt2Rebounder = random.choices(
                                        gett2Players,
                                        weights=[
                                            x.ReboundingPer for x in team_two_roster
                                        ],
                                        k=1,
                                    )
                                    t2rebounder = pickt2Rebounder[0]
                                    t2rebounder.Stats.AddRebound(True)
                                    team_two.Stats.AddRebound(True)
                                    printt2Rebounder = (
                                        t2rebounder.FirstName
                                        + " "
                                        + t2rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t2
                                        + " "
                                        + printt2Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t2
                                else:
                                    pickt1Rebounder = random.choices(
                                        gett1Players,
                                        weights=[
                                            x.ReboundingPer for x in team_one_roster
                                        ],
                                        k=1,
                                    )
                                    t1rebounder = pickt1Rebounder[0]
                                    printt1Rebounder = (
                                        t1rebounder.FirstName
                                        + " "
                                        + t1rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t1
                                        + " "
                                        + printt1Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t1
                            else:
                                collector.AppendPlay(
                                    possession,
                                    play,
                                    "FreeThrow",
                                    t1pts,
                                    t2pts,
                                    possessionNum,
                                    total_possessions,
                                )
            elif possrand < t2twoInsideCutoff:
                pickPlayer = random.choices(
                    gett2Players, weights=[x.InsideUsage for x in team_two_roster], k=1
                )
                shooter = pickPlayer[0]
                printShooter = shooter.FirstName + " " + shooter.LastName
                blockAdj = (0.00001 * t2_adj_interior_defense) - 0.0153
                if shooter.ID == t1team_df["FocusPlayer"]:
                    made2inf = (0.005 * shooter.Finishing) - 4 + 0.185 + HCA
                else:
                    made2inf = (0.005 * shooter.Finishing) + 0.185 + HCA
                madeDiff = made2inf - 0.563
                missed2inf = 0.147 - madeDiff - blockAdj
                made2ifoul = 0.05
                missed2ifoul = 0.14
                blocked = 0.1 + blockAdj
                base2iCutoff = 0
                made2iCutoff = base2iCutoff + made2inf
                missed2iCutoff = made2iCutoff + missed2inf
                blocked2iCutoff = missed2iCutoff + blocked
                missed2ifoulCutoff = blocked2iCutoff + missed2ifoul
                made2ifoulCutoff = missed2ifoulCutoff + made2ifoul
                eventOutcome = random.random()
                if eventOutcome < made2iCutoff:
                    msg = printShooter + " Inside shot...Score!"
                    t2pts += 2
                    shooter.Stats.AddFieldGoal(True, 2)
                    team_two.Stats.AddFieldGoal(True)
                    team_two.Stats.AddPoints(2, possessionNum, halftime_point, is_ot)
                    team_two.Stats.CalculateLead(2, t2pts - t1pts)
                    assistRand = random.random()
                    if assistRand > 0.57:
                        assistList = [x for x in gett2Players if x.ID != shooter.ID]
                        pickAssister = random.choices(
                            assistList, weights=[x.AssistPer for x in assistList], k=1
                        )
                        assister = pickAssister[0]
                        if assister.ID != shooter.ID:
                            assister.Stats.AddAssist()
                            team_two.Stats.AddAssist()
                            printAssister = assister.FirstName + " " + assister.LastName
                            msg += "       Assisted by: " + printAssister
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Score",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                    possession = t1
                elif eventOutcome < missed2iCutoff:
                    msg = printShooter + " Inside shot...Missed!"
                    shooter.Stats.AddFieldGoal(False, 2)
                    team_two.Stats.AddFieldGoal(False)
                    rebrand = random.random()
                    if rebrand < t2OffensiveRebound:
                        pickt2Rebounder = random.choices(
                            gett2Players,
                            weights=[x.ReboundingPer for x in team_two_roster],
                            k=1,
                        )
                        t2rebounder = pickt2Rebounder[0]
                        t2rebounder.Stats.AddRebound(True)
                        team_two.Stats.AddRebound(True)
                        printt2Rebounder = (
                            t2rebounder.FirstName + " " + t2rebounder.LastName
                        )
                        msg += (
                            "       Rebounded by " + t2 + " " + printt2Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            msg,
                            "Score",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t2
                    else:
                        pickt1Rebounder = random.choices(
                            gett1Players,
                            weights=[x.ReboundingPer for x in team_one_roster],
                            k=1,
                        )
                        t1rebounder = pickt1Rebounder[0]
                        t1rebounder.Stats.AddRebound(False)
                        team_one.Stats.AddRebound(False)
                        printt1Rebounder = (
                            t1rebounder.FirstName + " " + t1rebounder.LastName
                        )
                        msg += (
                            "       Rebounded by " + t1 + " " + printt1Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            msg,
                            "Score",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t1
                elif eventOutcome < blocked2iCutoff:
                    pickBlocker = random.choices(
                        gett1Players,
                        weights=[x.DefensePer for x in team_one_roster],
                        k=1,
                    )
                    blocker = pickBlocker[0]
                    blocker.Stats.AddBlock()
                    team_one.Stats.AddBlocks()
                    shooter.Stats.AddTurnover()
                    printBlocker = blocker.FirstName + " " + blocker.LastName
                    msg = (
                        printShooter + " Inside shot...BLOCKED by " + printBlocker + "."
                    )
                    rebrand = random.random()
                    if rebrand < 0.43:
                        pickt2Rebounder = random.choices(
                            gett2Players,
                            weights=[x.ReboundingPer for x in team_two_roster],
                            k=1,
                        )
                        t2rebounder = pickt2Rebounder[0]
                        t2rebounder.Stats.AddRebound(True)
                        team_two.Stats.AddRebound(True)
                        printt2Rebounder = (
                            t2rebounder.FirstName + " " + t2rebounder.LastName
                        )
                        msg += (
                            "       Rebounded by " + t2 + " " + printt2Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            msg,
                            "Turnover",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t2
                    else:
                        pickt1Rebounder = random.choices(
                            gett1Players,
                            weights=[x.ReboundingPer for x in team_one_roster],
                            k=1,
                        )
                        t1rebounder = pickt1Rebounder[0]
                        t1rebounder.Stats.AddRebound(False)
                        team_one.Stats.AddRebound(False)
                        printt1Rebounder = (
                            t1rebounder.FirstName + " " + t1rebounder.LastName
                        )
                        msg += (
                            "       Rebounded by " + t1 + " " + printt1Rebounder + "."
                        )
                        collector.AppendPlay(
                            possession,
                            msg,
                            "Turnover",
                            t1pts,
                            t2pts,
                            possessionNum,
                            total_possessions,
                        )
                        possession = t1
                elif eventOutcome < missed2ifoulCutoff:
                    msg = (
                        printShooter
                        + " Inside shot... Missed but with a foul on the play."
                    )
                    team_one.Stats.AddFoul()
                    shooter.Stats.AddFieldGoal(False, 2)
                    team_two.Stats.AddFieldGoal(False)
                    foulShots = 2
                    ftCutoff = (0.02 * shooter.FreeThrow) + 0.5
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Fouled",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                    while foulShots > 0:
                        if random.random() <= ftCutoff:
                            play = "Free throw coming up... good!"
                            t2pts += 1
                            shooter.Stats.AddFTMade()
                            team_two.Stats.AddFreeThrow(True)
                            team_two.Stats.AddPoints(
                                1, possessionNum, halftime_point, is_ot
                            )
                            team_two.Stats.CalculateLead(1, t2pts - t1pts)
                            collector.AppendPlay(
                                possession,
                                play,
                                "FreeThrow",
                                t1pts,
                                t2pts,
                                possessionNum,
                                total_possessions,
                            )
                            foulShots -= 1
                            if foulShots == 0:
                                possession = t1
                        else:
                            play = "Free throw coming up... rattled out."
                            shooter.Stats.AddFTAttempt()
                            team_two.Stats.AddFreeThrow(False)
                            foulShots -= 1
                            if foulShots == 0:
                                rebrand = random.random()
                                if rebrand < t2OffensiveRebound:
                                    pickt2Rebounder = random.choices(
                                        gett2Players,
                                        weights=[
                                            x.ReboundingPer for x in team_two_roster
                                        ],
                                        k=1,
                                    )
                                    t2rebounder = pickt2Rebounder[0]
                                    t2rebounder.Stats.AddRebound(True)
                                    team_two.Stats.AddRebound(True)
                                    printt2Rebounder = (
                                        t2rebounder.FirstName
                                        + " "
                                        + t2rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t2
                                        + " "
                                        + printt2Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t2
                                else:
                                    pickt1Rebounder = random.choices(
                                        gett1Players,
                                        weights=[
                                            x.ReboundingPer for x in team_one_roster
                                        ],
                                        k=1,
                                    )
                                    t1rebounder = pickt1Rebounder[0]
                                    printt1Rebounder = (
                                        t1rebounder.FirstName
                                        + " "
                                        + t1rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t1
                                        + " "
                                        + printt1Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t1
                            else:
                                collector.AppendPlay(
                                    possession,
                                    play,
                                    "FreeThrow",
                                    t1pts,
                                    t2pts,
                                    possessionNum,
                                    total_possessions,
                                )
                elif eventOutcome < made2ifoulCutoff:
                    msg = (
                        printShooter
                        + " Inside shot...Score! Fouled and we have a free throw folks!"
                    )
                    t2pts += 2
                    shooter.Stats.AddFieldGoal(True, 2)
                    team_two.Stats.AddFieldGoal(True)
                    team_two.Stats.AddPoints(2, possessionNum, halftime_point, is_ot)
                    team_two.Stats.CalculateLead(2, t2pts - t1pts)
                    team_one.Stats.AddFoul()
                    assistRand = random.random()
                    if assistRand > 0.57:
                        assistList = [x for x in gett2Players if x.ID != shooter.ID]
                        pickAssister = random.choices(
                            assistList, weights=[x.AssistPer for x in assistList], k=1
                        )
                        assister = pickAssister[0]
                        if assister.ID != shooter.ID:
                            assister.Stats.AddAssist()
                            team_two.Stats.AddAssist()
                            printAssister = assister.FirstName + " " + assister.LastName
                            msg += "       Assisted by: " + printAssister
                    foulShots = 1
                    collector.AppendPlay(
                        possession,
                        msg,
                        "Score",
                        t1pts,
                        t2pts,
                        possessionNum,
                        total_possessions,
                    )
                    ftCutoff = (0.02 * shooter.FreeThrow) + 0.5
                    while foulShots > 0:
                        if random.random() <= ftCutoff:
                            play = "Free throw coming up... good!"
                            t2pts += 1
                            shooter.Stats.AddFTMade()
                            team_two.Stats.AddFreeThrow(True)
                            team_two.Stats.AddPoints(
                                1, possessionNum, halftime_point, is_ot
                            )
                            team_two.Stats.CalculateLead(1, t2pts - t1pts)
                            collector.AppendPlay(
                                possession,
                                play,
                                "FreeThrow",
                                t1pts,
                                t2pts,
                                possessionNum,
                                total_possessions,
                            )
                            foulShots -= 1
                            if foulShots == 0:
                                possession = t1
                        else:
                            play = "Free throw coming up... rattled out."
                            shooter.Stats.AddFTAttempt()
                            team_two.Stats.AddFreeThrow(False)
                            foulShots -= 1
                            if foulShots == 0:
                                rebrand = random.random()
                                if rebrand < t2OffensiveRebound:
                                    pickt2Rebounder = random.choices(
                                        gett2Players,
                                        weights=[
                                            x.ReboundingPer for x in team_two_roster
                                        ],
                                        k=1,
                                    )
                                    t2rebounder = pickt2Rebounder[0]
                                    t2rebounder.Stats.AddRebound(True)
                                    team_two.Stats.AddRebound(True)
                                    printt2Rebounder = (
                                        t2rebounder.FirstName
                                        + " "
                                        + t2rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t2
                                        + " "
                                        + printt2Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t2
                                else:
                                    pickt1Rebounder = random.choices(
                                        gett1Players,
                                        weights=[
                                            x.ReboundingPer for x in team_one_roster
                                        ],
                                        k=1,
                                    )
                                    t1rebounder = pickt1Rebounder[0]
                                    printt1Rebounder = (
                                        t1rebounder.FirstName
                                        + " "
                                        + t1rebounder.LastName
                                    )
                                    play += (
                                        "       Rebounded by "
                                        + t1
                                        + " "
                                        + printt1Rebounder
                                        + "."
                                    )
                                    collector.AppendPlay(
                                        possession,
                                        play,
                                        "FreeThrow",
                                        t1pts,
                                        t2pts,
                                        possessionNum,
                                        total_possessions,
                                    )
                                    possession = t1
                            else:
                                collector.AppendPlay(
                                    possession,
                                    play,
                                    "FreeThrow",
                                    t1pts,
                                    t2pts,
                                    possessionNum,
                                    total_possessions,
                                )

        # if NBA GAME
        if possessionNum == math.floor((total_possessions) / 4) and nba_match:
            print("\n")
            print("-----End of the 1st Quarter!-----")
            print("Halftime score")
            print(t2 + ": " + str(t2pts))
            print(t1 + ": " + str(t1pts))
            msg = ""
            collector.AppendPlay(
                "",
                msg,
                "END OF 1ST QUARTER",
                t1pts,
                t2pts,
                possessionNum,
                total_possessions,
            )
            print("\n")

        if possessionNum == math.floor((total_possessions) / 2):
            print("\n")
            print("-----HALFTIME!-----")
            print("Halftime score")
            print(t2 + ": " + str(t2pts))
            print(t1 + ": " + str(t1pts))
            msg = ""
            collector.AppendPlay(
                "", msg, "HALFTIME", t1pts, t2pts, possessionNum, total_possessions
            )
            print("\n")

        # if NBA GAME
        if possessionNum == math.floor((total_possessions) / 1.5) and nba_match:
            print("\n")
            print("-----End of the 3rd Quarter!-----")
            print("Halftime score")
            print(t2 + ": " + str(t2pts))
            print(t1 + ": " + str(t1pts))
            msg = ""
            collector.AppendPlay(
                "",
                msg,
                "END OF 3rd QUARTER",
                t1pts,
                t2pts,
                possessionNum,
                total_possessions,
            )
            print("\n")

        if possessionNum >= total_possessions and t1pts == t2pts:
            print("-----OVERTIME!-----")
            total_possessions += math.floor((total_possessions) / 8)
            msg = "...and we're going to Overtime!"
            collector.AppendPlay(
                "", msg, "OVERTIME", t1pts, t2pts, possessionNum, total_possessions
            )
            is_ot = True

    print("\n")
    print("Final Score")
    print(t2 + ": " + str(t2pts))
    print(t1 + ": " + str(t1pts))
    print("\n")
    msg = "Match Complete"
    collector.AppendPlay(
        "", msg, "FinalScore", t1pts, t2pts, possessionNum, total_possessions
    )
    play_by_play_path = filePath + "/play_by_plays"
    box_score_path = filePath + "/box_scores"
    if not os.path.exists(play_by_play_path):
        os.makedirs(play_by_play_path)

    if not os.path.exists(box_score_path):
        os.makedirs(box_score_path)

    UserString = ""
    if (HomeCoach != "AI" and HomeCoach != "") or (
        AwayCoach != "AI" and AwayCoach != ""
    ):
        UserString = "USER_"

    file_name = (
        play_by_play_path + "/" + UserString + gameid + "_" + t1 + "_" + t2 + ".csv"
    )
    with open(file_name, "w", newline="") as csvfile:
        fieldnames = [
            "Team",
            "Result",
            "PlayType",
            "TeamOneScore",
            "TeamTwoScore",
            "Possession",
            "Total Possessions",
        ]
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "HomeTeam",
                "AwayTeam",
                "HomeTeamScore",
                "AwayTeamScore",
                "Total Possessions",
            ]
        )
        writer.writerow(
            [hometeam, awayteam, str(t1pts), str(t2pts), str(total_possessions)]
        )
        writer.writerow([""])
        writer.writerow(fieldnames)
        for x in collector.List:
            writer.writerow(
                [
                    x["Team"],
                    x["Result"],
                    x["PlayType"],
                    x["TeamOneScore"],
                    x["TeamTwoScore"],
                    x["Possession"],
                    x["Total Possessions"],
                ]
            )

    file_name = box_score_path + "/" + gameid + "_" + t1 + "_" + t2 + ".csv"
    with open(file_name, "w", newline="") as csvfile:
        box_score_writer = csv.writer(csvfile)
        box_score_writer.writerow(["=====BOX SCORE====="])
        box_score_writer.writerow(["", "", "1st", "2nd", "OT", "Total"])
        box_score_writer.writerow(
            [
                team_one.TeamName,
                team_one.Mascot,
                str(team_one.Stats.FirstHalfScore),
                str(team_one.Stats.SecondHalfScore),
                str(team_one.Stats.OvertimeScore),
                str(t1pts),
            ]
        )
        box_score_writer.writerow(
            [
                team_two.TeamName,
                team_two.Mascot,
                str(team_two.Stats.FirstHalfScore),
                str(team_two.Stats.SecondHalfScore),
                str(team_two.Stats.OvertimeScore),
                str(t2pts),
            ]
        )
        box_score_writer.writerow([""])
        box_score_writer.writerow([""])
        box_score_writer.writerow(["=====" + team_one.TeamName + " Players====="])
        box_score_writer.writerow(
            [
                "Player",
                "Minutes",
                "Possessions",
                "FGM",
                "FGA",
                "FG%",
                "3PM",
                "3PA",
                "3P%",
                "FTM",
                "FTA",
                "FT%",
                "Points",
                "Rebounds",
                "Assists",
                "Steals",
                "Blocks",
                "TOs",
                "Fouls",
            ]
        )
        for player in gett1Players:
            box_score_writer.writerow(
                [
                    player.FirstName + " " + player.LastName,
                    str(player.Minutes),
                    str(player.Stats.Possessions),
                    str(player.Stats.FGM),
                    str(player.Stats.FGA),
                    str(player.Stats.FGPercent),
                    str(player.Stats.ThreePointsMade),
                    str(player.Stats.ThreePointAttempts),
                    str(player.Stats.ThreePointPercent),
                    str(player.Stats.FTM),
                    str(player.Stats.FTA),
                    str(player.Stats.FTPercent),
                    str(player.Stats.Points),
                    str(player.Stats.TotalRebounds),
                    str(player.Stats.Assists),
                    str(player.Stats.Steals),
                    str(player.Stats.Blocks),
                    str(player.Stats.Turnovers),
                    str(player.Stats.Fouls),
                ]
            )
        box_score_writer.writerow([""])
        box_score_writer.writerow(["=====" + team_two.TeamName + " Players====="])
        box_score_writer.writerow(
            [
                "Player",
                "Minutes",
                "Possessions",
                "FGM",
                "FGA",
                "FG%",
                "3PM",
                "3PA",
                "3P%",
                "FTM",
                "FTA",
                "FT%",
                "Points",
                "Rebounds",
                "Assists",
                "Steals",
                "Blocks",
                "TOs",
                "Fouls",
            ]
        )
        for player in gett2Players:
            box_score_writer.writerow(
                [
                    player.FirstName + " " + player.LastName,
                    str(player.Minutes),
                    str(player.Stats.Possessions),
                    str(player.Stats.FGM),
                    str(player.Stats.FGA),
                    str(player.Stats.FGPercent),
                    str(player.Stats.ThreePointsMade),
                    str(player.Stats.ThreePointAttempts),
                    str(player.Stats.ThreePointPercent),
                    str(player.Stats.FTM),
                    str(player.Stats.FTA),
                    str(player.Stats.FTPercent),
                    str(player.Stats.Points),
                    str(player.Stats.TotalRebounds),
                    str(player.Stats.Assists),
                    str(player.Stats.Steals),
                    str(player.Stats.Blocks),
                    str(player.Stats.Turnovers),
                    str(player.Stats.Fouls),
                ]
            )
        box_score_writer.writerow([""])
        box_score_writer.writerow([""])
        box_score_writer.writerow(["=====TEAM STATS====="])
        box_score_writer.writerow(["Stat", team_one.TeamName, team_two.TeamName])
        box_score_writer.writerow(
            ["Points", team_one.Stats.Points, team_two.Stats.Points]
        )
        box_score_writer.writerow(
            ["Possessions", team_one.Stats.Possessions, team_two.Stats.Possessions]
        )
        box_score_writer.writerow(["FGM", team_one.Stats.FGM, team_two.Stats.FGM])
        box_score_writer.writerow(["FGA", team_one.Stats.FGA, team_two.Stats.FGA])
        box_score_writer.writerow(
            ["FGPercent", team_one.Stats.FGPercent, team_two.Stats.FGPercent]
        )
        box_score_writer.writerow(
            ["3PM", team_one.Stats.ThreePointsMade, team_two.Stats.ThreePointsMade]
        )
        box_score_writer.writerow(
            [
                "3PA",
                team_one.Stats.ThreePointAttempts,
                team_two.Stats.ThreePointAttempts,
            ]
        )
        box_score_writer.writerow(
            ["3P%", team_one.Stats.ThreePointPercent, team_two.Stats.ThreePointPercent]
        )
        box_score_writer.writerow(["FTM", team_one.Stats.FTM, team_two.Stats.FTM])
        box_score_writer.writerow(["FTA", team_one.Stats.FTA, team_two.Stats.FTA])
        box_score_writer.writerow(
            ["FT%", team_one.Stats.FTPercent, team_two.Stats.FTPercent]
        )
        box_score_writer.writerow(
            ["Rebounds", team_one.Stats.Rebounds, team_two.Stats.Rebounds]
        )
        box_score_writer.writerow(
            ["OffRebounds", team_one.Stats.OffRebounds, team_two.Stats.OffRebounds]
        )
        box_score_writer.writerow(
            ["DefRebounds", team_one.Stats.DefRebounds, team_two.Stats.DefRebounds]
        )
        box_score_writer.writerow(
            ["Assists", team_one.Stats.Assists, team_two.Stats.Assists]
        )
        box_score_writer.writerow(
            ["Steals", team_one.Stats.Steals, team_two.Stats.Steals]
        )
        box_score_writer.writerow(
            ["Blocks", team_one.Stats.Blocks, team_two.Stats.Blocks]
        )
        box_score_writer.writerow(
            [
                "Total Turnovers",
                team_one.Stats.TotalTurnovers,
                team_two.Stats.TotalTurnovers,
            ]
        )
        box_score_writer.writerow(
            ["Largest Lead", team_one.Stats.LargestLead, team_two.Stats.LargestLead]
        )

    results = MatchResults(
        team_one, team_two, gett1Players, gett2Players, gameid, is_nba
    )

    return results


num = input("Which week of Games do you want to run? ")

newPath = "./NCAA Week " + num + " Results/"
if not os.path.exists(newPath):
    os.makedirs(newPath)

resultList = []

with open("NCAA Schedule - Week " + num + ".csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",", quotechar="|")
    for row in reader:
        if (
            row[0] == "Monday"
            or row[0] == "GameID"
            or row[0] == "Tuesday"
            or row[0] == "Wednesday"
            or row[0] == "Thursday"
            or row[0] == "Friday"
            or row[0] == "Saturday"
            or row[0] == ""
        ):
            continue
        results = rungame(row[0], row[1], row[2], row[3], row[4], newPath)
        resultList.append(results)

# dto = ImportDTO(resultList)
