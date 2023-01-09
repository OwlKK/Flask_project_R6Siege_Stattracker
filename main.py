# Program to store score from a online game match and display average score
# http://localhost:5000
# https://www.tutorialspoint.com/flask/flask_sqlite.htm

# Use archivum to send one file
from flask import Flask, request, render_template
import sqlite3 as sql

# Creating a SQLite database (or connecting if exists) and table AND returning database object

sqlite_connection = sql.connect('database.db')
# sqlite_connection.execute('CREATE TABLE IF NOT EXISTS score '
#                          '(player_name TEXT, game_score NUMBER,  kills NUMBER, assists NUMBER, deaths NUMBER)')
# sqlite_connection.close()

app = Flask(__name__)


class Score:
    def __init__(self, player_name, game_score, kills, assists, deaths, won_or_lost):
        self.player_name = player_name
        self.game_score = game_score
        self.kills = kills
        self.assists = assists
        self.deaths = deaths
        self.won_or_lost = won_or_lost


@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/enter_new")
def new_match_score():
    return render_template('match_score.html')


@app.route('/add_record', methods=['POST', 'GET'])
def add_record():
    if request.method == 'POST':
        player_name = request.form['player_name']
        game_score = int(request.form['game_score'])  # - maybe has wrong type? else player_name would blow up...
        kills = int(request.form['kills'])
        assists = int(request.form['assists'])
        deaths = int(request.form['deaths'])
        won_or_lost = int(request.form['won_or_lost'])

        conn = sql.connect("database.db")

        cursor = conn.cursor()
        # Insert requested fields from form into table "score"
        # cursor.execute("ALTER TABLE score ADD COLUMN won_or_lost NUMBER")
        try:
            cursor.execute(
                "INSERT INTO score (player_name, game_score, kills, assists, deaths, won_or_lost) VALUES (?,?,?,?,?,?)",
                (player_name, game_score, kills, assists, deaths, won_or_lost)
            )

            conn.commit()
            msg = "Record added"
        except Exception as e:
            print(e)
            return 'Error during record addition'
        finally:
            conn.close()
    return render_template("result.html", msg=msg)


@app.route('/record_list')
def list():
    con = sql.connect('database.db')
    con.row_factory = sql.Row

    cursor = con.cursor()
    cursor.execute("select * from score")

    rows = cursor.fetchall()

    all_kills = 0
    all_deaths = 0
    all_matches_outcome = 0
    n_played_matches = 0

    for row in rows:
        kills_round = int(row[2])
        deaths_round = int(row[4])
        match_outcome = int(row[5])

        all_kills = all_kills + kills_round
        all_deaths = all_deaths + deaths_round
        all_matches_outcome = all_matches_outcome + match_outcome
        n_played_matches = n_played_matches + 1
    if n_played_matches == 0:
        kd = 1
        wl = 1
    else:
        kd = all_kills / all_deaths
        wl = all_matches_outcome / n_played_matches

    con.close()
    return render_template("records_list.html", rows=rows, kd=kd, wl=wl)


@app.route('/remove_record')
def remove_record():
    # Połącz się z bazą danych
    conn = sql.connect("database.db")

    # Utwórz kursor
    cursor = conn.cursor()

    # Usuń ostatni rekord z tabeli "score"
    cursor.execute("DELETE FROM score WHERE rowid = (SELECT MAX(rowid) FROM score);")

    # Zatwierdź zmiany
    conn.commit()

    # Zakończ połączenie z bazą danych
    conn.close()

    return list()


if __name__ == '__main__':
    app.run(debug=True)
