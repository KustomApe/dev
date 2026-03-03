import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import config

client_key = config.CLIENT_ID
client_secret = config.CLIENT_SECRET

# Spotifyの認証情報
client_credentials_manager = SpotifyClientCredentials(client_id='Your_Client_ID', client_secret='Your_Client_Secret')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# トラック情報の取得
track = sp.track('spotify:track:4cluDES4hQEUhmXj6TXkSo')
print(track)
