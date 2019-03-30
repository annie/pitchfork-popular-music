import csv
import json
import operator
import os
from pitchfork_api import pitchfork
import re
import sys
import wikipedia


def process_artists_file(year, artists):
    file_name = 'data/hot_100/hot-100-artists-{}.csv'.format(year)
    with open(file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if len(row) != 2:
                continue
            name = row[0]
            artist_info = {year: row[1]}
            if name not in artists:
                artists[name] = [artist_info]
            else:
                artists[name].append(artist_info)
    return artists


def process_artists_files(start_year, end_year):
    artists = {}
    for year in range(start_year, end_year):
        process_artists_file(year, artists)
    return artists


def get_wiki_page(artist):
    try:
        return wikipedia.WikipediaPage(title=artist)
    # there must be a better way to do this...lol
    except wikipedia.exceptions.WikipediaException:
        try:
            return wikipedia.WikipediaPage(
                title='{} (singer)'.format(artist)
            )
        except wikipedia.exceptions.WikipediaException:
            try:
                return wikipedia.WikipediaPage(
                    title='{} (musician)'.format(artist)
                )
            except wikipedia.exceptions.WikipediaException:
                try:
                    return wikipedia.WikipediaPage(
                        title='{} (rapper)'.format(artist)
                    )
                except wikipedia.exceptions.WikipediaException:
                    try:
                        return wikipedia.WikipediaPage(
                            title='{} (band)'.format(artist)
                        )
                    except wikipedia.exceptions.WikipediaException:
                        pass
    return None


def parse_discography(discography):
    if discography is None:
        return []
    parsed = []
    regex = r"(?:^.*[aA]lbums?:?[\s]*)?([^\(]*)[\s]*\(([0-9]{4})\)"
    for album in discography.split('\n'):
        match = re.match(regex, album)
        if (match is not None and
                len(match.groups()) == 2 and
                len(match.groups()[0].strip()) > 0):
            parsed.append({
                'name': match.groups()[0].strip(),
                'year': match.groups()[1],
            })
    return parsed


def get_score(artist, album):
    try:
        p = pitchfork.search(artist, album)
        return p.score()
    except IndexError:
        return None


def get_album_reviews(artist):
    wiki_page = get_wiki_page(artist)
    if wiki_page is None:
        return []
    parsed_discography = parse_discography(wiki_page.section('Discography'))
    return list(
        map(
            lambda album: {
                'album_name': album['name'],
                'score': get_score(artist, album['name']),
                'year': album['year'],
            },
            parsed_discography
        )
    )


def get_avg_score(albums):
    total_score = 0
    non_null_reviews = 0
    for album in albums:
        if album['score'] is not None:
            total_score += album['score']
            non_null_reviews += 1
    return total_score/non_null_reviews if non_null_reviews > 0 else 0


def write_artist_avg_scores_to_file(f, artists):
    for artist in artists:
        print(artist)
        album_reviews = get_album_reviews(artist)
        f.write('{},{}\n'.format(artist, get_avg_score(album_reviews)))


def get_artist_reviews(artists):
    artist_reviews = []
    for artist in artists:
        artist_albums = get_album_reviews(artist)
        if len(artist_albums) > 0:
            artist_reviews.append({
                'artist': artist,
                'albums': artist_albums
            })
    return artist_reviews


def write_unique_artists_file(start_year, end_year):
    artists = process_artists_files(start_year, end_year)
    unique_artists_file = 'data/unique-hot-100-artists-{}-{}.json'.format(
        start_year,
        end_year
    )
    with open(unique_artists_file, 'w') as f:
        f.write(json.dumps(artists, sort_keys=True, indent=4))


def get_unprocessed_artists(file_name, artists):
    with open(file_name, 'r') as avgs_file:
        processed_artists = set()
        csv_reader = csv.reader(avgs_file, delimiter=',')
        for row in csv_reader:
            processed_artists.add(row[0])
        return [artist for artist in artists if artist not in processed_artists]


def sort_and_write_file(file_name):
    parsed = []
    with open(file_name, 'r') as og_file:
        csv_reader = csv.reader(og_file, delimiter=',')
        for row in csv_reader:
            if len(row) != 2:
                continue
            parsed.append((row[0], row[1]))

    sorted_file_name = '{}-sorted.csv'.format(file_name)
    with open(sorted_file_name, 'w') as sorted_file:
        for row in sorted(parsed, key=operator.itemgetter(1), reverse=True):
            sorted_file.write('{},{}\n'.format(row[0], row[1]))


def main():
    start_year = int(sys.argv[1])
    end_year = int(sys.argv[2])

    unique_artists_file = 'data/unique-hot-100-artists-{}-{}.json'.format(
        start_year,
        end_year
    )
    if not os.path.exists(unique_artists_file):
        write_unique_artists_file(start_year, end_year)

    with open(unique_artists_file) as unique_file:
        artists = json.load(unique_file).keys()

        file_name = 'data/pitchfork_reviews/hot-100-artists-avgs-{}-{}.csv'.format(
            start_year,
            end_year
        )
        if os.path.exists(file_name):
            write_mode = 'a'
            artists = get_unprocessed_artists(file_name, artists)
        else:
            write_mode = 'w'

        # TODO: what to do if script terminated in the middle of processing an
        # artist?
        with open(file_name, write_mode) as avgs_file:
            # TODO: expand analysis beyond avg scores
            write_artist_avg_scores_to_file(avgs_file, artists)


main()
