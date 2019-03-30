import csv
import json
import operator


def process_csv_file(file_name):
    parsed = []
    with open(file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if len(row) != 2:
                continue
            parsed.append((row[0], row[1]))
    return parsed


def process_json_file(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


def get_avg_scores(reviews):
    avg_scores = []
    for artist_info in reviews:
        # ignore nonexistent reviews for now
        score = 0
        non_null_reviews = 0
        for album in artist_info['albums']:
            if album['score'] is not None:
                score += album['score']
                non_null_reviews += 1
        avg_score = score/non_null_reviews if non_null_reviews > 0 else 0
        avg_scores.append((artist_info['artist'], avg_score))
    return sorted(avg_scores, key=operator.itemgetter(1), reverse=True)


def main():
    reviews = process_csv_file(
        'data/pitchfork_reviews/hot-100-artists-avgs.csv'
    )
    sorted_reviews = sorted(reviews, key=operator.itemgetter(1), reverse=True)
    for review in sorted_reviews:
        print(review)
    # get avg score for each artist
    # sort artists by avg score
    # write to file with avg scores


main()
