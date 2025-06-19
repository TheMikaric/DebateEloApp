import csv # Za obradu CSV datoteka
import cyrtranslit # Za transliteraciju ćirilice u latinicu za potrebe namena
import re # Za obradu namena tj. uklanjanje suvišnih reči


def load_debater_elo(file_name:str,alt_mod:bool=False)->dict[str,(float,int)]:
    '''Function reads debater ELOs from a CSV file and returns a dictionary.
    Inputs:
    file_name: name of the file, including the extension (.csv)
    alt_mod: toggles joining names from separate columns, set True only if name and surname aren't in the same column in CSV file
    Output:
    dictionary whose keys are sanitized names of debaters and values are tuples
    where first tuple member is current elo and second is number of debates had so far '''
    elo_debaters = {} # Define empty dictionary
    try:
        with open(file_name, newline='\n', encoding='utf-8') as csvdat:
            reader = csv.reader(csvdat, delimiter=' ')
            for row in reader:
                if alt_mod:
                    name_debatera = clean_name(row[0]+' '+row[1])
                    elo_debaters[name_debatera] = (float(row[2]),int(row[3]))
                else:
                    name_debatera = clean_name(row[0])
                    elo_debaters[name_debatera] = (float(row[1]),int(row[2]))
    except FileNotFoundError:
        pass # If no file exists, simply return empty dictionary of "already existing" debaters
    return elo_debaters

def clean_name(name:str)->str:
    '''Function cleans names so Nikola Nikolić, Nikola nikolic and Никола Николић are the same person.
    Inputs: 
    name: full name exactly as it appears on speaker tab
    Outputs:
    sanitized name string'''
    name = name.lower()
    name = name.strip() # Remove empty spaces at the start and end of string
    name = cyrtranslit.to_latin(name, 'sr') # Cyrilic to latin
    name = name.replace('č', 'c')
    name = name.replace('š', 's')
    name = name.replace('ž', 'z')
    name = name.replace('ć', 'c')
    name = name.replace('đ', 'd')
    name = re.sub(r' .+? ', ' ', name) # Remove everything between first and last string
    return name

def load_teams_participants(file_name:str,speaker_csv_mode:bool=False,ignore_1:bool=True,no_of_rounds:int=5)->dict[str,str]:
    '''Function loads names of debaters from CSV files and returns their names and teams. If the file doesn't exist, empty dictionary is returned.
    Inputs:
    file_name: name of the file from which teams will be loaded
    speaker_csv_mode: toggle True if the data is being loaded from exported speaker tab
    ignore_1: toggle True to ignore first row (headers), toggle False if your file is just data and no headers
    no_of_rounds: number of the in-round in the tournament
    Output:
    dictionary whose keys are names of the debaters, and values are team names for the debater'''
    speakers_teams = {}
    first_row = True
    try:
        with open(file_name, newline='\n', encoding='utf-8') as csvdat:
            reader = csv.reader(csvdat, delimiter='\t')
            # Tab is the delimeter because that's default Tabbycat CSV format
            for row in reader:
                if len(row) == no_of_rounds+6:
                    speaker_csv_mode=True
                if ignore_1==False or first_row==False:
                    if speaker_csv_mode:
                        name_debater = clean_name(row[1])
                        speakers_teams[name_debater]=row[2]
                    else:
                        name_debater = clean_name(row[1])
                        speakers_teams[name_debater]=row[3]
                first_row=False
        return speakers_teams
    except FileNotFoundError:
        return speakers_teams
def load_team_ranks(file_name:str,ignore_1:bool=True,alt_instit:bool=False)->dict[str,int]:
    '''Load names of the teams and their ranks (without data abut their debates)
    Inputs:
    file_name: name of the file from which the data is being loaded
    ignore_1: toggle true if the first row of your file is columns, false if it's just data
    alt_instit: toggle true if the names of the institutions are not included in the export.
    Outputs:
    dictionary whose keys are team names and values are places in the debate'''
    teams_positions = {}
    first_row = True
    location = 2
    if alt_instit:
        location = 1
    with open(file_name, newline='\n',encoding='utf-8') as csvdat:
        reader = csv.reader(csvdat, delimiter='\t')
        for row in reader:
            if ignore_1==False or first_row==False:
                teams_positions[row[0]]=convert_rank(row[location])
            first_row=False
    return teams_positions

def convert_rank(rank:str)->int:
    ''' Converts ranks into numbers. e.g. 1st into 1'''
    if rank == '1st':
        return 1
    elif rank == '2nd':
        return 2
    elif rank == '3rd':
        return 3
    elif rank == '4th':
        return 4 
    
def load_debates(file_name:str,ignore_1:bool=True)->list[set[str]]:
    '''Function loads debates from a CSV file, but not the ranking of teams within the debates.
    Inputs:
    file_name: name of the CSV file, including the .CSV extension
    ignore_1: boolean that signifies whether first row is data or headers
    Outputs:
    list of sets where each sets contains all the teams within single debate,
    e.g. [(teamA,teamB,teamC,teamD),(teamE,teamF,teamG,teamH)...]'''
    debate_teams = []
    first_row=True
    with open(file_name, newline='\n', encoding='utf-8') as csvdat:
        reader = csv.reader(csvdat, delimiter='\t')
        for row in reader:
            if first_row==False or ignore_1==False:
                myset = set()
                myset.add(row[1])
                myset.add(row[2])
                myset.add(row[3])
                myset.add(row[4])
                debate_teams.append(myset)
            first_row=False
    return debate_teams

def export_debater_elo(debater_elo:dict[str,(float,int)], file_name:str)->None:
    '''Function writes ELO ratings to a file.
    Inputs:
    debater_elo: dictionary whose keys are names of debaters, value are tuples,
    first member of the tuple is ELO rating, and second is number of debates
    file_name: name of the file to be written to, including .csv extension
    Outputs:
    CSV file with a given name.
    Note: Writer works in 'w' mode, meaning it will OVERWRITE if the file already exists.
    '''
    with open(file_name, 'w', newline='\n', encoding='utf-8') as csvdat:
        writer = csv.writer(csvdat, delimiter=' ')
        for name, elo in debater_elo.items():
            writer.writerow([name, elo[0], elo[1]])  # Upisujemo name, ELO rejting i broj debata

def uvezi_spikere(file_name:str,no_of_rounds:int=5,ignore_1:bool=True)->dict[str, (str, list[int],float)]:
    '''Function loads speaker points from a .CSV file and converts them to a dictionary
    Inputs:
    file_name: name of the .csv file where the speakers are stored, including the .csv extension
    no_of_rouds: total number of the inrounds of the tournament
    ignore_1: boolean that determines if the first row should be ignored (it is a header) or not (it is data)
    Outputs:
    dictionary whose keys are sanitized debaters' names, and values are tuples,
    first member of the tuple is team name (unsanitized),
    second member is a list of ints (speaker points for a given round),
    third is average speaker points over all inrounds.'''
    speakers = {}
    first_row=True
    with open(file_name, newline='\n', encoding='utf-8') as csvdat:
        reader = csv.reader(csvdat, delimiter='\t')
        for row in reader:
            if first_row==False or ignore_1==False:    
                try:
                    average = float(row[no_of_rounds+4])
                except ValueError:
                    average = 0.0

                templist = []
                for i in range(4, 4+no_of_rounds): # Where the speaker points are depends on no of rounds
                    try:
                        templist.append(int(row[i]))
                    except ValueError:
                        templist.append(0)
                speakers[clean_name(row[1])] = (row[3],templist, average)  # Uzimamo namena i njihove rezultate
            first_row=False
        return speakers
    
def add_debaters(elo_debaters:dict[str,(float,int)], file_name:str, ignore_1:bool=True):
    '''Add debaters to an ELO dictionary from a file (if they aren't on the ELO list already).
    If the file exists already function just finishes without modifying the dictionary.
    Inputs:
    elo_debaters: existing ELO dictionary, keys are sanitized names of the debaters, values are tuples,
    first member of the tuple is current ELO rating, second member is number of debates so far
    ignore_1: boolean that determines if first row should be ignored (it is headers), or not (it is data)
    Output:
    Nothing, updates dictionary by reference
    '''
    first_row=True
    try:
        with open(file_name, newline='\n', encoding='utf-8') as csvdat:
            reader = csv.reader(csvdat, delimiter='\t')
            for row in reader:
                if first_row==False or ignore_1 == False:
                    if clean_name(row[1]) not in elo_debaters.keys():
                        elo_debaters[clean_name(row[1])]=(1000,0)  
                        # If debater isn't already on the list, assign defualt rating and debate numbber
                first_row=False
        print('majmun')
        print(elo_debaters)
        print('majmun')
    except FileNotFoundError:
        pass
    '''NOTE: Dictionary is updated by reference, since python only gives out reference 
    when an argument of a called function is a complex data structure like this dictionary.'''