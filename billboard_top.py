import billboard
import datetime
import operator
import sys

HOT_100 = 'hot-100'


def get_chart(type, date):
    return billboard.ChartData(type, date)


def trim_featured_artist(artist):
    parsed = artist.split(' ')
    trimmed = []
    for word in parsed:
        if word == 'Featuring':
            return ' '.join(trimmed)
        trimmed.append(word)
    return ' '.join(trimmed)


def get_artist_list_for_year(year):
    counts = {}
    for i in range(1, 13):
        month = '0' + str(i) if i < 10 else str(i)
        date = str(year) + '-' + month + '-' + '01'
        print(date)
        month_list = get_chart(HOT_100, date)
        for obj in month_list:
            artist = trim_featured_artist(obj.artist)
            if artist in counts:
                counts[artist] += 1
            else:
                counts[artist] = 1
    sorted_list = sorted(
        counts.items(),
        key=operator.itemgetter(1),
        reverse=True
    )
    top_artists = []
    i = 0
    while i < len(sorted_list) and sorted_list[i][1] >= 6:
        top_artists.append(sorted_list[i])
        i += 1
    return top_artists


def get_artist_lists_for_range(start, end):
    for year in range(start, end):
        csv_name = 'data/hot_100/hot-100-artists-{}.csv'.format(year)
        f = open(csv_name, 'w')
        year_list = get_artist_list_for_year(year)
        for artist_count in year_list:
            row = artist_count[0] + ',' + str(artist_count[1]) + '\n'
            f.write(row)
        f.close()


def validate_year(year):
    try:
        year = int(year)
    except ValueError:
        print('{} must be an int'.format(year))

    now = datetime.datetime.now()
    if year < 1936 or year > now.year:
        print('{} is an invalid year'.format(year))
        return None
    return year


def main():
    if (len(sys.argv) != 3):
        print('valid use: python billboard_top.py <start_year> <end_year>')
        return

    start_year = validate_year(sys.argv[1])
    end_year = validate_year(sys.argv[2])
    if end_year < start_year:
        print('invalid date range')
        return
    get_artist_lists_for_range(start_year, end_year + 1)


main()
