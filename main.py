import spotipy
import time
import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect, render_template

### Load in env variables
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
scope = "playlist-read-private"
redirect_uri = os.getenv("REDIRECT_URI")

# initialize Flask app
app = Flask(__name__)
app.config['SESSION_COOKIE_NAME'] = os.getenv("SESSION_COOKIE_NAME")
app.secret_key = os.getenv("COOKIE_SECRET_KEY")

TOKEN_INFO = "token_info"

@app.route('/')
def spotify_login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    code = request.args.get('code')
    print(f"Received code: {code}")

    if code:
        token_info = create_spotify_oauth().get_access_token(code)
        session[TOKEN_INFO] = token_info
        return redirect(url_for('get_playlists', _external=True))
    else:
        flash("OAuth authentication failed.")
        return redirect(url_for('spotify_login', _external=True))


@app.route('/getPlaylists')
def get_playlists():
        
    token_info = get_token()
    sp = spotipy.Spotify(auth=token_info['access_token'])
    current_playlists = sp.current_user_playlists()['items']
    return render_template('playlists.html', playlists=current_playlists)


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('spotify_login', _external=False))

    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = client_id,
        client_secret = client_secret,
        redirect_uri = redirect_uri,
        scope = scope
    )


app.run(debug=True)