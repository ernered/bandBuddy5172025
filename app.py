from flask import Flask, render_template, request, redirect, url_for, session
import random
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Initialize the database
def init_db():
    with sqlite3.connect('songs.db') as conn:
        cursor = conn.cursor()
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        # Create songs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song TEXT NOT NULL,
                artist TEXT NOT NULL
            )
        ''')
        # Add default admin user if not exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                           ('admin', generate_password_hash('superpublicpassword01')))
        conn.commit()

# Add a song to the database
def add_song(song_name, artist_name):
    with sqlite3.connect('songs.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO songs (song, artist) VALUES (?, ?)', (song_name, artist_name))
        conn.commit()

# Get all songs from the database
def get_all_songs():
    with sqlite3.connect('songs.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM songs')
        return cursor.fetchall()

# Remove a song by ID
def remove_song_by_id(song_id):
    with sqlite3.connect('songs.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM songs WHERE id = ?', (song_id,))
        conn.commit()

# Get a random song
def get_random_song():
    songs = get_all_songs()
    if songs:
        return random.choice(songs)
    return None

# Initialize the database
init_db()

# Home route to display the song list and form for adding songs
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Add a song
        song_name = request.form['song_name']
        artist_name = request.form['artist_name']

        if song_name and artist_name:
            add_song(song_name, artist_name)

        return redirect(url_for('home'))

    songs = get_all_songs()
    return render_template('index.html', songs=songs)

# Route to remove a song (admin only)
@app.route('/remove/<int:song_id>', methods=['POST'])
def remove_song(song_id):
    if 'username' not in session:  # Ensure user is logged in as admin
        return redirect(url_for('login'))

    remove_song_by_id(song_id)
    return redirect(url_for('home'))

# Random song selection route
@app.route('/random')
def random_song():
    selected_song = get_random_song()
    if selected_song:
        return render_template('random.html', selected_song=selected_song)
    return "No songs available to select."

# Login route for admin
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('songs.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()

        if user and check_password_hash(user[0], password):
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
    app.run(host='0.0.0.0', port=8080)
