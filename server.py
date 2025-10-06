import json
from flask import Flask,render_template,request,redirect,flash,url_for
from datetime import datetime


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions

def saveClubs(listOfClubs):
    with open('clubs.json', 'w', encoding='utf-8') as c:
        json.dump({"clubs": listOfClubs}, c, indent=4, ensure_ascii=False)

def saveCompetitions(listOfCompetitions):
    with open('competitions.json', 'w', encoding='utf-8') as comps:
        json.dump({"competitions": listOfCompetitions}, comps, indent=4, ensure_ascii=False)

app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()


@app.template_filter("is_past")
def is_past_filter(value, fmt="%Y-%m-%d %H:%M:%S"):
    if isinstance(value, datetime):
        date_value = value
    else:
        try:
            date_value = datetime.strptime(value, fmt)
        except Exception:
            return False
    return date_value < datetime.now()

@app.route('/')
def index():
    return render_template('index.html')

# Page d'accueil, liste des compétitions
@app.route('/showSummary', methods=['POST'])
def showSummary():
    match_club = [club for club in clubs if club['email'] == request.form['email']]
    if match_club:
        club = match_club[0]
        flash('Bienvenue')
        return render_template('welcome.html', club=club, competitions=competitions)
    else:
        error = "Sorry, that email wasn't found."
        return render_template('index.html', error=error), 400


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]

    if foundClub and foundCompetition:
        comp_name = foundCompetition["name"]
        if comp_name not in foundClub:
            max_places = 12
        else:
            max_places = 12 - int(foundClub[comp_name])
        return render_template('booking.html', club=foundClub,
                               competition=foundCompetition,
                               max_places=max_places)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])

    if placesRequired > int(club['points']):
        error = "Vous n'avez pas assez de points pour réserver autant de places"
        return render_template("booking.html", club=club, competition=competition, error=error), 400
        
    if placesRequired > 12:
        error = 'Vous ne pouvez pas réserver plus de 12 places par compétition'
        return render_template("booking.html", club=club, competition=competition, error=error), 400

    if competition["name"] in club:
        already_booking = club[competition["name"]]
        if placesRequired + already_booking > 12:
            error = 'Vous ne pouvez pas réserver plus de 12 places par compétition'
            return render_template("booking.html", club=club, competition=competition, error=error), 400
            
    comp_date = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")
    if comp_date < datetime.now():
        error = "Il est impossible de réserver des places dans une compétition terminée"
        return render_template("booking.html", club=club, competition=competition, error=error), 400

    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired

    saveClubs(clubs)
    saveCompetitions(competitions)
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))