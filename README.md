# Analyzing popular artists and their Pitchfork reviews
[Pitchfork](https://pitchfork.com/) is an influential publication in the music world, and it's known for
its coverage of indie music and somewhat esoteric reviews. However, they also review more "mainstream"
popular music. I was curious to see which popular artists
are most favored by Pitchfork, and how Pitchfork's treatment of popular music
might have changed over time.

## Questions to consider
- Which popular artists have gotten the best/worst Pitchfork reviews?
- What genres of popular music get the best/worst reviews?
- Best/worst single album reviews (vs. average)?
- Has Pitchfork reviewed more/less popular music over the past decade?

## Findings
**DISCLAIMER:** I am figuring out some data issues, so the results below are subject to change. The main problem is the inconsistency of my Wikipedia scraper - the logic for finding disambiguated artist pages and parsing the Discography section isn't robust enough. Working on this.

### Artist Rankings by Average Album Score (2008-2018)
Albums are given scores out of 10. Genres were taken manually from the artists' Wikipedia pages.

### Top 10
FWIW, Pitchfork classifies a 8.0+ album rating as "Best New Music".
| Artist | Avg album score | Genre(s) |
| :----- | :-------------: | :------- |
| Kendrick Lamar | 9.00 | Hip Hop |
| Chance The Rapper | 8.75 | Hip Hop, R&B |
| Cardi B | 8.70 | Hip Hop |
| Kanye West | 8.70 | Hip Hop |
| Maxwell | 8.56 | R&B, Soul
| Miguel | 8.47 | R&B |
| SZA | 8.40 | Alternative R&B |
| The-Dream | 8.20 | R&B, Hip Hop |
| ScHoolboy Q | 8.17 | Hip Hop |
| Jazmine Sullivan | 8.10 | R&B, Soul |

### Bottom 10
Unlike Rotten Tomatoes, Pitchfork doesn't have a "Certified Rotten"-type classification. I guess that's nice of them. They can still be pretty brutal though.
| Artist | Avg album score | Genre(s) |
| :----- | :-------------: | :------- |
| Panic! At The Disco | 1.50 | Pop Rock |
| Jessie J | 2.00 | R&B, Pop |
| Charlie Puth | 2.50 | Pop |
| Kevin Rudolf | 2.70 | Rock |
| Mumford & Sons | 3.30 | Folk Rock |
| 6ix9ine | 3.40 | Hip Hop |
| Tyga | 3.60 | Hip Hop |
| The Chainsmokers | 3.65 | EDM, Pop |
| Tiesto | 3.80 | House |
| Lil Pump | 3.80 | Hip Hop, Trap |


## Methodology
I wrote all the data scraping and processing code in Python. I used the following libraries (all created/maintained by independent developers):
- [Billboard Charts API](https://github.com/guoguo12/billboard-charts) by [guoguo12](https://github.com/guoguo12)
- [Wikipedia API](https://github.com/goldsmith/Wikipedia) by [goldsmith](https://github.com/goldsmith)
- [Pitchfork API](https://github.com/michalczaplinski/pitchfork) by [michalczaplinski](https://github.com/michalczaplinski)

### Identifying popular artists
I looked at Billboard's [Hot 100 Artists](https://www.billboard.com/charts/artist-100) chart to find popular artists. The chart is updated weekly - I felt this was too granular for my purposes, so I took the following steps to get a list of the most popular artists from a given year:
1. Get the Hot 100 list from the first of every month (12 lists in total)
2. Clean up artist names by eliminating the "Featured" artists (although looking at Featured artists could be interesting in the future)
3. Sum up how many times each unique artist appeared on the 12 Hot 100 lists
4. Sort the master list and only keep artists that appeared 6+ times in total

You can see the master list of unique artists + number of appearances each year in `unique-hot-100-artists-2008-2018.json`.

### Getting albums
The [Pitchfork API](https://github.com/michalczaplinski/pitchfork) requires both artist and album names (or at least the first few words of the album name) to get a review. Billboard didn't have a mapping from artists to albums, so I turned to trusty ol' Wikipedia.

I chose to use a lightweight [Wikipedia library](https://github.com/goldsmith/Wikipedia) that supports searching for pages with keywords. The basic functionality worked, but I ran into a couple interesting problems with the search queries.

##### Disambiguation
There are a handful of artists that have ambiguous names. For example, searching "Pitbull" yields a list of results from dog breeds to sports teams. In cases with ambiguity, the Wikipedia API throws an error - what I actually need to search for in this case is "Pitbull (rapper)".

My solution was to use nested try/catch blocks to first search for the artist name, then "[Artist Name] (singer)" if the first query throws, then "[Artist Name] (musician)" if the second query throws, and so on - you get the idea. It's a clunky solution and I'd like to come up with something more graceful.

##### Parsing Discography
Once I have the Wikipedia page for an artist, I want to get a comprehensive list of their albums. Thankfully, it seems that most (if not all) artist pages have a Discography section. However, parsing the text from that section is tricky. Splitting by newline does not always yield a clean list, and some of the more prolific artists have dedicated Wikipedia pages just for their discography.

I solved this problem partially using regex, but this needs to be worked on as well.

### Fetching album reviews & ranking
Once I had a list of albums for each artist, I queried the Pitchfork API to get the scores for each album. If an album didn't have a review, I gave it a 0. Then, I calculated an average score for each artist across all of their albums and sorted the list by average score.

I am a beginner in the world of statistics/data science, so I'm aware that there may be major problems with this approach. Some open questions I'm trying to answer are:
- Should an album with no review be counted as 0 or something else?
- Should I be looking at averages for all albums, or some other measure?

### Running the scripts
As I wrote this code, I tested it by running the scripts for artists in 2008. My initial implementation naively rewrote all the CSV/JSON files for every run. That worked for a single year, but when I started trying to look at the whole decade, the script would often encounter some HTTP error and terminate early. Because I was overwriting and not appending to the files, nothing would get written during a failed run and I would have to restart.

The biggest bottleneck was fetching the reviews from Pitchfork. This step had the highest volume of individual requests. I realized I could change the script to append to a file if it already existed, and also to read the existing file to see which artists had not already been processed from the previous run(s). These simple changes allowed me to finally complete a list of aggregated album scores for all the artists fetched from Billboard.
