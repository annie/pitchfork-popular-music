from sets import Set
import spotipy
import spotipy.util as util


def get_auth():
    return util.prompt_for_user_token(
        '1248014422',
        'playlist-read-private',
        client_id='c09297e252f746b3b215d468b6004eae',
        client_secret='998f71143af84854804ece7cecf3305e',
        redirect_uri='https://example.com/callback'
    )


def get_artist_id(sp, artist):
    results = sp.search(q='artist:' + artist, type='artist')
    if len(results) == 0:
        return None
    return results['artists']['items'][0]['href'].split('/')[-1]


def get_albums(sp, artist):
    artist_id = get_artist_id(sp, artist)
    print(artist_id)
    if artist_id is None:
        return []
    album_list = []
    for obj in sp.artist_albums(artist_id)['items']:
        album_list.append(obj['name'])
    return Set(album_list)


def main():
    token = get_auth()
    if token:
        sp = spotipy.Spotify(auth=token)
        print(get_albums(sp, 'Beyonce'))


main()
