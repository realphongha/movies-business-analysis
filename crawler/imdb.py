import json
import requests
from bs4 import BeautifulSoup
from utils import *
from multiprocessing.pool import ThreadPool

BASE_LINK = "https://www.imdb.com/search/title/?title_type=feature&user_rating=1.0,10.0&countries=us&adult=include&sort=release_date,desc&count=250"
URL_PREFIX = "https://www.imdb.com"
LIMIT = 20000
OUTPUT_FILE = "output/imdb.json"
SAVE_FREQ = 10
PROCESSES = 10


counter = None
results = None


def save_to_file():
    global results
    if results:
        print("Saving %d movie(s)..." % counter)
        with open(OUTPUT_FILE, "a", encoding="utf8") as file:
            for movie in results:
                json.dump(movie, file)
                file.write("\n")
    results = []


class IMDBMovie:

    def __init__(self, title=None, rating=None, date=None, genre=None, actor=None, director=None, duration=None,
                 rating_count=None, content_rating=None, oscar=None, metascore=None):
        self.title = title
        self.rating = rating
        self.date = date
        self.genre = genre
        self.actor = actor
        self.director = director
        self.duration = duration
        self.rating_count = rating_count
        self.content_rating = content_rating
        self.oscar = oscar
        self.metascore = metascore

    def to_json(self):
        return {"title": self.title,
                "rating": self.rating,
                "date": self.date,
                "genre": self.genre,
                "actor": self.actor,
                "director": self.director,
                "duration": self.duration,
                "rating_count": self.rating_count,
                "content_rating": self.content_rating,
                "oscar": self.oscar,
                "metascore": self.metascore}


def crawl_movie(args):
    url, movie = args
    global counter, results
    print("Crawling %s..." % url)
    source = requests.get(url, headers=HDR)
    if source.status_code != 200:
        print("Cannot get movie details! Status code: %d"
              % source.status_code)
        print(source.text)
        return
    soup = BeautifulSoup(source.text, 'html.parser')
    try:
        info = json.loads(soup.find("script", {"type": "application/ld+json"}).contents[0])
    except json.decoder.JSONDecodeError:
        print(soup.find("script", {"type": "application/ld+json"}).text)
        print("JSON decode error!")
        return
    except TypeError:
        print("Type error!")
        return
    try:
        movie.genre = info["genre"]
        movie.actor = info["actor"]
        movie.director = info["director"]
        movie.duration = info["duration"]
    except KeyError as e:
        print(e)
        return
    try:
        movie.rating_count = info["aggregateRating"]["ratingCount"]
    except KeyError:
        pass
    movie.content_rating = info.get("contentRating", None)
    movie.date = info.get("datePublished", None)
    awards = soup.select("div#titleAwardsRanks span.awards-blurb b")
    for award in awards:
        if "oscars" in award.text.lower():
            movie.oscar = award.text.lower()
    try:
        movie.metascore = \
            soup.select("div.titleReviewBarItem a div.metacriticScore.score_favorable.titleReviewBarSubItem span")[0]\
                .text
    except IndexError:
        pass
    results.append(movie.to_json())
    print(movie.to_json())
    counter += 1
    print("Crawled %d movie(s)!" % counter)
    if counter % SAVE_FREQ == 0 and counter > 0:
        save_to_file()
    if counter == LIMIT:
        raise Enough()


def crawl_page(url, page=1):
    global counter
    print("Getting movies list in page %d...\nFrom URL: %s"
          % (page, url))
    source = requests.get(url, headers=HDR)
    if source.status_code != 200:
        print("Cannot get movies list! Status code: %d"
              % source.status_code)
        print(source.text)
        return
    soup = BeautifulSoup(source.text, 'html.parser')
    pre_counter = counter
    movies = soup.select("div.lister-item.mode-advanced")
    if PROCESSES > 1:
        args_list = []
    for movie in movies:
        new_movie = IMDBMovie()
        try:
            new_movie.rating = movie.select("div.ratings-bar div.inline-block.ratings-imdb-rating")[0].get("data-value")
            title = movie.select("h3.lister-item-header a")[0]
        except IndexError:
            continue
        new_movie.title = title.text
        if PROCESSES > 1:
            args_list.append((URL_PREFIX + title.get("href"), new_movie))
        else:
            crawl_movie((URL_PREFIX + title.get("href"), new_movie))
    if PROCESSES > 1:
        with ThreadPool(PROCESSES) as pool:
            for result in pool.map(crawl_movie, args_list):
                pass
    if pre_counter != counter:
        try:
            next_url = soup.select("a.lister-page-next.next-page")[0].get("href")
        except IndexError:
            raise Enough()
        crawl_page(URL_PREFIX + next_url, page + 1)
    else:
        raise Enough()


def main():
    global counter, results
    counter = 0
    results = list()
    try:
        crawl_page(BASE_LINK, 1)
    except Enough:
        print("Completed!")
    except Exception as e:
        print("Cannot complete crawling!")
        print(e)
        import traceback
        traceback.print_exc()
    except KeyboardInterrupt:
        print("Stop crawling! (Keyboard interrupt)")
    finally:
        save_to_file()


if __name__ == "__main__":
    main()
