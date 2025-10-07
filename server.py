import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime


def loadClubs():
    with open('clubs.json') as c:
        return json.load(c)['clubs']


def loadCompetitions():
    with open('competitions.json') as comps:
        return json.load(comps)['competitions']


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


@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form['email']
    club = next((c for c in clubs if c['email'] == email), None)
    if club:
        return render_template('welcome.html', club=club, competitions=competitions, message="Welcome")
    else:
        error = "Sorry, that email wasn't found."
        return render_template('index.html', error=error), 400


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)

    if not foundClub or not foundCompetition:
        flash("Something went wrong - please try again")
        return render_template('welcome.html', club=foundClub, competitions=competitions)

    comp_name = foundCompetition["name"]
    max_places = 12 - int(foundClub.get(comp_name, 0))
    return render_template('booking.html', club=foundClub, competition=foundCompetition, max_places=max_places)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)
    placesRequired = int(request.form['places'])

    if placesRequired < 0:
        error = 'Vous ne pouvez pas réserver un nombre de places négatif'
        return render_template("booking.html", club=club, competition=competition, error=error), 400

    if placesRequired > int(club['points']):
        error = "Vous n'avez pas assez de points pour réserver autant de places"
        return render_template("booking.html", club=club, competition=competition, error=error), 400

    if placesRequired > 12:
        error = 'Vous ne pouvez pas réserver plus de 12 places par compétition'
        return render_template("booking.html", club=club, competition=competition, error=error), 400

    if competition["name"] in club:
        already_booking = int(club[competition["name"]])
        if placesRequired + already_booking > 12:
            error = 'Vous ne pouvez pas réserver plus de 12 places par compétition'
            return render_template("booking.html", club=club, competition=competition, error=error), 400

    if "date" in competition:
        try:
            comp_date = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")
            if comp_date < datetime.now():
                error = "Il est impossible de réserver des places dans une compétition terminée"
                return render_template("booking.html", club=club, competition=competition, error=error), 400
        except Exception:
            pass

    nbrPlaces = int(competition["numberOfPlaces"]) - placesRequired
    if nbrPlaces < 0:
        error = "Le nombre de places ne peut pas être inférieur à zéro"
        return render_template("booking.html", club=club, competition=competition, error=error), 400

    competition['numberOfPlaces'] = nbrPlaces
    club['points'] = int(club['points']) - placesRequired
    comp_name = competition["name"]
    club[comp_name] = club.get(comp_name, 0) + placesRequired

    saveClubs(clubs)
    saveCompetitions(competitions)

    message = "Great-booking complete"
    return render_template('welcome.html',club=club, competitions=competitions, message=message), 200


@app.route("/club_table")
def club_table():
    return render_template("/club_table.html", clubs=clubs, competitions=competitions)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
