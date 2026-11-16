from bakery import assert_equal
from dataclasses import dataclass
from drafter import *
from user_info.py import user_database, User
from comp_challenges.py import emotional_challenges, rhythmic_challenges, get_daily_challenge
#go take a look at choosealicense.com

'''
UV HELPFUL COMMANDS
uv run main.py = run the script
uv add (extension) = add an extension to the project
Ctrl + C = stop the server
'''
#sets up user info for login

@dataclass
class Note:       #building block dataclass for music related programs
    pitch: str           
    length: float

@dataclass
class Measure:
    size: int
    notes: list[Note]
    beats: list[int]

#set up reusable rest/measure variables
whole_rest = Note("rest", 4)
half_rest = Note("rest", 2)
quarter_rest = Note("rest", 1)
eighth_rest = Note("rest", .5)

empty_measure = Measure(4, [whole_rest], [0])


@dataclass
class State:
    message: str
    username: str
    password: str
    challenge: Challenge = None
    user_composition: Sip = None


@dataclass
class Sip:        # a small composition
    playing_measure: Measure
    active_measure: Measure
    measure_length: int

empty_sip = Sip(empty_measure, empty_measure, 4)

@route
def index(state: State) -> Page:
    '''
    Login/Signup Page
        state(State): either will be the startup state up the updated username + password state 
        if the user signs up
    '''
    return Page(
        state,
        [Text(state.message),
         "\n",
        "Username:",
        TextBox("username", ''),
        "\n",
        "Password:",
        TextBox("password", ''),
        "\n",
        Button("Login", "login"),
        "\n",
        Button("Sign Up", "sign_up")])
assert_equal(index(State("Welcome to Sips of Ti-Do" + "\n" + "Please log in or sign up.", '', '')), Page(
        State("Welcome to Sips of Ti-Do" + "\n" + "Please log in or sign up.", '', '', None, None),
        [Text("Welcome to Sips of Ti-Do" + "\n" + "Please log in or sign up."),
         "\n",
        "Username:",
        TextBox("username", ''),
        "\n",
        "Password:",
        TextBox("password", ''),
        "\n",
        Button("Login", "login"),
        "\n",
        Button("Sign Up", "sign_up")]) )
@route
def login(state: State, username: str, password: str) -> Page:
    '''
    checks if a users login information matches a registered User from a seperate user database file
        if it does, they proceed to the main menu,
        else they are returned to the login page with an error message 
    state(State): here it just focuses on the current username + password
    username(str): the username the user inputs
    password(str): the password the user inputs
    '''
    is_user = False
    user_number = 0
    for user in user_database:
        user_number += 1
        if user.username == username:
            is_user = True
            break

    if is_user and password == user_database[user_number - 1].password:
        state = State("Login successful!", username, password)
        return main_menu(State("Welcome, " + username + "!", username, password))
    else:
        state = State("Login failed. Please try again.", '', '')
        return index(state)
#assert_equal
@route
def sign_up(state: State) -> Page:
    '''
    allows a user to sign up as a new user by inputing a new username and password
        state(State): will be updated with a new message prompting the user to enter 
        a new username and password
    '''
    state.message = "Please type in a username and a strong password!"
    return Page(state, [Text(state.message),
         "\n",
        "Username:",
        TextBox("username", ''),
        "\n",
        "Password:",
        TextBox("password", ''),
        "\n",
        Button("Back", "index"),
        "\n",
        Button("Sign Up", "save_login")])
#assert_equal
@route
def save_login(state: State, username: str, password: str) -> Page:
    '''
    takes the inputed user sign up info and stores it in the user database(temporarily), 
    then the user is sent back to the index/login page
        state(State): will be updated with new user info
        username(str): New user's username that they entered
        password(str): New user's password that they entered

    '''
    state.user = username
    state.password = password
    #add confirm password and astericks
    user_database.append(User(username, password))
    return index(state)
#assert_equal

   #end of login functions 
#######################################################################

@route
def main_menu(state: State) -> Page:
    '''
    the page where users select what composition challenge they'll do for the day
        state(State): has the saved user info, and will store the TYPE of challenge they select
    '''
    return Page(
        state,
        [Text(state.message),
         "\n",
         "What challenge do you want to sip today?",
         "\n",
         Button("Emotional Challenge", "composition_settings", [Argument("challenge_type", "emotional")]),
         "\n",
         Button("Rhythmic Challenge", "composition_settings", [Argument("challenge_type", "rhythmic")])])
#assert_equal

@route 
def composition_settings(state: State, challenge_type: str) -> Page:
    '''
    the page where the specifics of the user's choosen challenge is revealed,
    and also where the user selects how many measures they want to write
        state(State): will save the specific challenge and the number of measures the user wants to write
    '''
    user_challenge = rhythmic_challenges[0] #get_daily_challenge(emotional_challenges, rhythmic_challenges, "emotional")
    allowed_rhythm_types = ["whole", "half", "quarter","eighth"]
    allowed_pitch_types = ["A", "B", "C", "D", "E", "F"]
    if user_challenge != 'none':
        if user_challenge == 'quarter notes only':
            allowed_rhythm_types = ["quarter"]
        elif user_challenge.restrictions == 'half notes only':
            allowed_rhythm_types = ["half"]
    state.challenge = user_challenge


    
    return Page(state, ["Welcome to the " + str(challenge_type) + " challenge!",
                "\n",
                "Your Challenge:" + str(user_challenge.description),
                "\n",
                Button("Let's Sip!", "set_composition", 
                       [Argument("pitches", allowed_pitch_types), Argument("rhythms", allowed_rhythm_types), ])]
                )
#Can't assert_equal for composition_settings() since it involves random elements
@route
def set_composition(state: State, rhythms: list[str], pitches: list[str]) -> Page:
    state.user_composition = empty_sip
    state.message = "Take a Sip of some Music Composition" 
    return composition(state)   
      
def note_visual(note: Note) -> str:
    if note.pitch == 'rest':
        if note.length == 4:
            return "Whole Rest.png"
        elif note.length == 2:
            return "Half Rest.png"
        elif note.length == 1:
            return "Quarter Rest.png"
        else:
            return "Eighth Rest.png"
    else:
        if note.length == 4:
            return "Whole Note.png"
        elif note.length == 2:
            return "Half Note.png"
        elif note.length == 1:
            return "Quarter Note.png"  
        else:
            return "Eighth Note.png"        
@route
def composition(state: State) -> Page:
    '''
    the central page for composing, will be constantly updated based on user input
        state(State): user info + challenge info
        num_measures(int): total number of measures in the composition
        current_measure(int): which measure we are at in the composition, like an index
        current_beat(int): the current beat the user is working on within the current
        measure, again, like an index for the measure
    '''
    user_comp = state.user_composition
    current_measure = user_comp.active_measure
    sum_of_beats = 0
    
    for beat in current_measure.beats:
        sum_of_beats += beat
    if whole_rest in current_measure.notes:
        current_measure.notes.pop()
    content = [state.message + "\n"]
    content.append("\n")
    content.append(state.challenge.description)
    if current_measure.notes:
        count = 0
        for note in current_measure.notes:
            scale_factor = .1
            if current_measure.notes[count].length == 2:
                scale_factor = .5
            content.append((Picture.from_file(note_visual(note)).scale(scale_factor)))
            count += 1
        for note in current_measure.notes:
            content.append(Text(note.pitch))
    content.append("\n")
    content.append(Button("Add Note", "add_note"))
    content.append(SelectBox("note_name", ["A", "B", "C", "D", "E", "F"]))
    content.append(SelectBox("octave", [1, 2, 3, 4, 5, 6]))
    content.append(SelectBox("note_length", ["whole", "half", "quarter"]))
    content.append("Rest")
    content.append(CheckBox("is_rest", False))
    content.append("\n")
    content.append(Button("Reset Measure", reset_measure))
    content.append("\n")
    pitches = []
    lengths = []
    for note in current_measure.notes:
        pitches.append(note.pitch)
        lengths.append(note.length)
    if pitches:
        if len(pitches) == 1:
            content.append(Melody([(pitches[0], lengths[0])]))
        elif len(pitches) == 2:
            content.append(Melody([(pitches[0], lengths[0]), (pitches[1], lengths[1])]))
        elif len(pitches) == 3:
            content.append(Melody([(pitches[0], lengths[0]), (pitches[1], lengths[1]), (pitches[2], pitches[2])]))
        else:
            content.append(Melody([(pitches[0], lengths[0]), (pitches[1], lengths[1]), (pitches[2], pitches[2]), (pitches[3], lengths[3])]))
    #content.append(Button("Remove Note", "remove_note"))
    
    return Page(state, content)

@route
def reset_measure(state: State) -> Page:
    state.user_composition.active_measure = empty_measure
    state.user_composition.playing_measure = empty_measure
    return composition(state)

#assert_equal
'''
@route
def remove_note(state: State) -> Page:
    actual_beat = state.user_composition.current_beat-1
    current_note = state.user_composition.active_measure.notes[actual_beat]
    replace_length = state.user_composition.active_measure.notes[actual_beat].length
    if actual_beat > 0:
        actual_beat = 0  #makes sure we don't go to a negative measure index
    state.user_composition.active_measure.beats.pop(actual_beat)
    state.user_composition.active_measure.notes.pop(actual_beat)
    state.user_composition.active_measure.notes.insert(actual_beat, Note('rest', replace_length))
    state.user_composition.active_measure.beats.insert(actual_beat, replace_length)
    return composition(state)
'''
@route
def add_note(state: State, note_name: str, octave: str, note_length: str, is_rest: bool) -> Page:
    user_comp = state.user_composition
    current_measure_beats = user_comp.active_measure.beats #actual list of note lengths in the current measure
    measure_max = 4
    if not is_rest:
        new_pitch = note_name + octave
    else:
        new_pitch = 'rest'
    #converts note length input from selectbox into an int
    if note_length == "whole":
        new_note_length = 4
    elif note_length == "half":
        new_note_length = 2
    elif note_length == "quarter":
        new_note_length = 1
    else:
        new_note_length = 0.5
    current_measure_beats.append(new_note_length)
    beat_sum = 0
    for beat in current_measure_beats:
        beat_sum += beat
    # logic for adding notes
    if beat_sum > 4:
        state.message = "Error, note length too long for current measure"
        return composition(state)
    else:
        user_comp.active_measure.notes.append(Note(new_pitch, new_note_length))
        state.user_composition.active_measure = user_comp.active_measure
        state.user_composition.playing_measure = user_comp
        return composition(state)




#this function is still in progress


    '''
    adds a note to the current measure both visually, and systemically
        state(State): saved challenge settings and restrictions
        note_name(str): Note's letter (A,B,C,D,E,F, OR G)
        octave(str): Note's octave 1-6 (lowest to highest octave)

Functions needed
1. Add_note - when a user adds a note to the staff
2. Play_measure
3. Gen_measures - sets up measures based on user specifications
    '''
#stylistic things
set_website_title("Sips of Ti-Do")
set_website_style("latex")
set_site_information(
    author = "Gabriel Young",
    description = "A daily program for writting small 'sips' of music!",
    sources = "Brought to you via Drafter",
    planning = ["CS1 Final Project 0_ Pick a Problem.docx", "CS1 Final Project 1_ Design.docx"],
    links = ["https://github.com/SpartanKing424/cisc108_final_project"]
)
hide_debug_information()
set_website_framed(False)
start_server(State("Welcome to Sips of Ti-Do" + "\n" + "Please log in or sign up.", '', ''))

'''
Additonal Credits
https://www.pikpng.com - quarter rest & half rest PNGs
https://www.realclipart.com  - eighth rest, whole rest, & eighth note PNGs
https://www.pngwing.com - half note PNG
'''
