from operator import itemgetter # Za soritiranje liste listi po vrednosti u podlisti
import copy # Za pravljenje kopije rečnika
import csvio as csvio # Uvoz svih mojih funkcija iz csvio.py 
import webio as webio # Uvoz svih mojih funkcija iz webio.py
import datetime

version = 123456

def generate_pairs_teams(teams_ranks:dict[str,int], debates_teams:list[set[str]])->list[tuple[str,str]]:
    '''Generate ordered pairs of teams based on ranks. First team in the tuple is the winner, and second the loser.
    Input example: team A was 1st, B 2nd, C 3rd and D 4th.
    teams_ranks = {A:1,B:2,C:3,D:4}
    debates_teams = (A,B,C,D)
    Output example: [(A,B),(A,C),(A,D),(B,C),(B,D),(C,D)]
    '''
    pairs = []
    for debate in debates_teams: # Generate pairs of teams for each debate
        ranks = []
        for team in debate:
            if team not in teams_ranks:
                raise ValueError(f'Team {team} not found in rankings!')
            else:
                ranks.append([team,teams_ranks[team]]) # [team name, team rank]
            ranks = sorted(ranks, key=itemgetter(1)) # Sort by rank column, descending

        for i in range(len(ranks)): 
            for j in range(i+1, len(ranks)): # Cycles only thorugh teams further up the list (teams which lost to team in ranks[i])
                pairs.append((ranks[i][0], ranks[j][0])) # (winner,loser)
    
    return pairs

def generate_pairs_debaters(pairs_teams:list[tuple[str,str]],speakers_teams:dict[str,str])->list[tuple[str,str]]:
    '''
    Inputs:
    pairs_teams, list of tuples where first member is the winner and second the loser
    e.g. [(teamA,teamB),(teamA,teamC),(teamB,teamC)...]; teamA,teamB,teamC are team names
    speakers_teams, dictionary where spekaer name is the key, and team name is the value
    e.g. {(speakerA->teamA),(speakerB->teamB)...}
    Output:
    pairs_debaters, list of tuples where the first string is the winning debater, and the second losing debater.
    If team A beat team B, it is like every speaker in team A beat every speaker in team B
    '''
    pairs_debaters = []
    winners_debaters=[]
    losers_debaters=[]
    for pair in pairs_teams:
        winners_debaters = []
        losers_debaters = []
        for speaker,team in speakers_teams.items():
            if team == pair[0]:
                winners_debaters.append(speakers_teams)
            elif team == pair[1]:
                losers_debaters.append(speakers_teams)

        if not losers_debaters: # Swings are usually not on participant list, so we need to add them
            losers_debaters.append("UNKNOWN SWING 1")
            losers_debaters.append("UNKNOWN SWING 2")
        if not winners_debaters:
            winners_debaters.append("UNKNOWN SWING 1")
            winners_debaters.append("UNKNOWN SWING 2")
        if len(winners_debaters)<2:
            winners_debaters.append("UNKNOWN SINGLE SWING1")
        if len(losers_debaters)<2:
            losers_debaters.append("UNKNOWN SINGLE SWING1")

        pairs_debaters.append((winners_debaters[0], losers_debaters[0])) # Add all pairs of debaters for a pair of teams
        pairs_debaters.append((winners_debaters[1], losers_debaters[1]))
        pairs_debaters.append((winners_debaters[0], losers_debaters[1]))
        pairs_debaters.append((winners_debaters[1], losers_debaters[0]))
        
    return pairs_debaters

def calculate_k_factor(debater:tuple[float,int])->int:
    '''Function returns k factor used in determining ELO rating adjustment.
    Input: tuple where first value is current ELO rating, and second is number of debates so far.
    Output: k value'''
    
    base_k = 30

    if debater[0] > 1500:
        base_k -= 10
    elif debater[0] > 1250:
        base_k -= 5

    if debater[1] < 5:
        base_k *= 3
    elif debater[1] < 10:
        base_k *= 2
    elif debater[1] < 20:
        base_k *= 1.5

    return int(base_k)

def find_partner(debater:str, speakers:dict[str, (str, list[int], float)])->str:
    '''Function finds a partner for a given debater based on the spekaer tab.
    Inputs:
    debater: sanitized name of the debater whose partner we are trying to find
    speakers: dictionary where the key is speaker name, and value is tuple
    where the first element is team name, second is list of speaker points, and third is avg. speaker
    Outputs:
    Partner's name'''
    partner_team = []
    for name, data in speakers.items():
        if debater == name: # If the debater in the speaker tab is the debater whose partner we are trying to find
            partner_team = data[0] # partner's team name is the same as debater's
    for name, data in speakers.items():
        if partner_team == data[0] and debater!=name: # If the team is the same as debater's, and the name isn't the same as debater's
            return name
    return debater # If there is no partner, they debated alone, with themselves

def apply_speaker_modifier(debater:str, speakers:dict[str, (str, list[int], float)], winner:bool, round_no:int)->float:
    '''Function returns a modifier between 0,1 and 2 based on speaker points.
    Inputs:
    debater: debater's sanitized name
    speakers: dictionary where keys are debater's sanitized names and values are tuples,
    first member of a tuple is team name, second member is list of speaker points by rounds, 
    and third is the average speaker.
    winner: boolean that signifies whether the debater whose modifier we are calculating won or lost.
    round_no: number of the round for which we are calculating the modifier'''
    
    if debater not in speakers:
        return 1.0  # If debater isn't on the list of spekaers (most likely a swing), we return 1.0, not changing anything

    # Delta between partners' speaker points.
    # Positive delta means that a given debater outspoke their partner
    # Negative delta means that a given debater was outspoken by their parnter
    delta_speak = speakers[debater][1][round_no-1] - speakers[find_partner(debater,speakers)][1][round_no-1]

    # If debater wins, we want to increase ELO impact if debater outspoke the partner, and decrease it if debater was outspoken
    # If debater loses, we want to decrease ELO impact if debater outspoke the partner, and increase it if debater was outspoken
    preelim_modifier = 1+(delta_speak/10) if winner else 1-(delta_speak/10)

    if preelim_modifier > 2: return 2
    if preelim_modifier < 0: return 0.1
    return preelim_modifier
 
    
def calculate_elo(pairs_debaters:list[tuple[str,str]], elo_debaters:dict[str,(float,int)],speaker_pts:dict[str, (str, list[int], float)], round_no:int)->dict[str,(float,int)]:
    '''Function calculates and returns new ELO ratings.
    Throws value error if loser gains rating or winner loses rating.
    Inputs: 
    pairs_debaters: list of tuples where the first debater won over second debater
    elo_debaters: dictionary with keys being sanitized debater names, and values being
    tuples where first member is current ELO rating and second member is number of debates debated so far
    speaker_pts: dictionary with names of debaters as keys, and tuples as values,
    first member of the tuple is name of the eteam, second is list of speakers by rounds, and third is avg. speaker
    Outputs:
    dictionary in the same format as elo_debaters, as these are updated rankings.'''
    new_elo_debaters = copy.deepcopy(elo_debaters)  # Copy of the original dictionary so we don't change the original
    print('lolcina')
    print(elo_debaters)
    print('lolcina')
    for pair in pairs_debaters:
        winner = pair[0]
        loser = pair[1]
        print(winner)
        print(loser)
        k_winner = 1
        k_loser = 1
    
        if winner not in elo_debaters.keys(): #  Meaning winner isn't already on the list of debaters, most likely a swing
            print('nevirujem')
            elo_winner = 1000  # Default assumed ELO rating
            k_winner = 0 
        else:   
            elo_winner = elo_debaters[winner][0]
            k_winner = calculate_k_factor(elo_debaters[winner])

        if loser not in elo_debaters.keys():
            print('nevirujem')
            elo_loser = 1000
            k_loser = 0
        else: 
            elo_loser = elo_debaters[loser][0]
            k_loser = calculate_k_factor(elo_debaters[loser])

        delta_winner = 1 - (1 / (1 + 10 ** ((elo_winner - elo_loser) / 400))) # ELO mathematical formula
        delta_loser = 1 - (1 / (1 + 10 ** ((elo_winner - elo_loser) / 400)))
        
        delta_winner *= k_winner*apply_speaker_modifier(winner,speaker_pts,True,round_no)
        delta_loser *= k_loser*apply_speaker_modifier(loser,speaker_pts,False,round_no)
        if delta_winner < 0 or delta_loser < 0:
            raise ValueError(f'Winner or loser delta below 0!\nloser={delta_loser} winner={delta_winner}')
        
        new_elo_winner = elo_winner + delta_winner # new elo equals old one plus difference calculated by the formula
        new_elo_loser = elo_loser - delta_loser # delta is always positive, so the loser gets delta subtracted from old elo
        print(new_elo_loser)
        print(new_elo_winner)
        #Update the ELO of debaters by assigning new ELO value and incrementing number of debates had so far
        if winner in elo_debaters.keys():             
            new_elo_debaters[winner]=(new_elo_winner, elo_debaters[winner][1]+1)
        if loser in elo_debaters.keys(): 
            new_elo_debaters[loser]=(new_elo_loser, elo_debaters[loser][1]+1) # Ažuriramo ELO rejting gubitnika
    
    return new_elo_debaters

def enter_tournament(url:str,num_of_rounds:int=5,
spk_file:str='speakers.csv',new_elo_file:str='elo.csv')->None:
    '''Enter all results for given number of rounds and apply ELO calculation to participants.
    Inputs:
    url: URL of the tournament tab (only tabbycat URLs supported currently)
    num_of_rounds: number of the inrounds of the tournament (outrounds not supported currently)
    spk_file: name of the file in which speaker tab is located
    new_elo_file: name of the file where updated ELO rankings will be outputed, must be the same file where current rankings are'''
    global version
    version+=1
    elo_debaters = csvio.load_debater_elo(new_elo_file) # Loads existing rankings
    print(elo_debaters)
    webio.download_whole_tournament(url,num_of_rounds) # Downloads all files needed for ELO calculation
    csvio.add_debaters(elo_debaters,f'tournament_files/{spk_file}') # Adds debaters who aren't on the ELO list currently to the ELO list
    print(elo_debaters)
    speakers_teams = csvio.load_teams_participants(spk_file,no_of_rounds=num_of_rounds) # Loads speaker names and their team names
    speaker_pts= csvio.uvezi_spikere(f'tournament_files/{spk_file}',no_of_rounds=num_of_rounds) # Loads speaker tab

    for i in range(1,num_of_rounds+1): # For each round 
        teams_ranks = csvio.load_team_ranks(f'tournament_files/teams_ranks_round_{i}.csv',alt_instit=True) # Loads rankings of each team for a given round
        debates_teams = csvio.load_debates(f'tournament_files/teams_debates_round_{i}.csv') # Loads data about which teams debated which teams on a given round
        pairs_teams = generate_pairs_teams(teams_ranks, debates_teams) # Makes pairs of each two teams based on debate with four teams.
        pairs_debaters = generate_pairs_debaters(pairs_teams,speakers_teams) # Makes pairs of debaters from different teams based on two teams
        elo_debaters= calculate_elo(pairs_debaters, elo_debaters,speaker_pts,i) # Calculate new ELOs
    print(elo_debaters)
    csvio.export_debater_elo(elo_debaters, new_elo_file) # Export new elos to a file
    csvio.export_debater_elo(elo_debaters, f'tournament_files/new_elo_file_{version}.csv') # Additional file for archival purposes

enter_tournament('https://opencommunication2025.calicotab.com/prva2025/')