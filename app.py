from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# In-memory users and songs
users = {"admin": "superpublicpassword01"}  # Admin credentials
songs = []

# Home route to display the song list and form for adding songs
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Add a song
        song_name = request.form['song_name']
        artist_name = request.form['artist_name']

        if song_name and artist_name:
            song_id = len(songs) + 1
            songs.append({'id': song_id, 'song': song_name, 'artist': artist_name})

        return redirect(url_for('home'))

    return render_template('index.html', songs=songs)

# Route to remove a song (admin only)
@app.route('/remove/<int:song_id>', methods=['POST'])
def remove_song(song_id):
    if 'username' not in session:  # Ensure user is logged in as admin
        return redirect(url_for('login'))

    global songs
    songs = [song for song in songs if song['id'] != song_id]
    return redirect(url_for('home'))

# Random song selection route
@app.route('/random')
def random_song():
    if songs:
        selected_song = random.choice(songs)
        return render_template('random.html', selected_song=selected_song)
    return "No songs available to select."

# Login route for admin
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)