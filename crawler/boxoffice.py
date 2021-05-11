import json
import requests
from bs4 import BeautifulSoup
from utils import *
from multiprocessing.pool import ThreadPool
from data_utils import read_json_file

URL_PREFIX = "https://www.boxofficemojo.com"
OUTPUT_FILE = "output/boxoffice.json"
SAVE_FREQ = 100
PROCESSES = 8
MIN_RATING_COUNT = 1000
DATA_PATH = "output/imdb.json"


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


class Movie:

    def __init__(self):
        self.title = None
        self.budget = None
        self.opening = None
        self.domestic = None
        self.worldwide = None
        self.url = None

    def to_json(self):
        return {"title": self.title,
                "budget": self.budget,
                "opening": self.opening,
                "domestic": self.domestic,
                "worldwide": self.worldwide,
                "url": self.url}


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
        summary = soup.select("div.a-section.a-spacing-none.mojo-performance-summary-table div")
        for div in summary:
            if "domestic" in div.select("span.a-size-small")[0].text.lower():
                movie.domestic = div.select("span.money")[0].text
            elif "worldwide" in div.select("span.a-size-small")[0].text.lower():
                movie.worldwide = div.select("span.money")[0].text
            if movie.domestic is not None and movie.worldwide is not None:
                break
        infos = soup.select("div.a-section.a-spacing-none.mojo-summary-values.mojo-hidden-from-mobile div")
        for info in infos:
            if "domestic opening" in info.select("span")[0].text.lower():
                movie.opening = info.select("span a.a-link-normal span.money")[0].text
            elif "budget" in info.select("span")[0].text.lower():
                movie.budget = info.select("span span.money")[0].text
            if movie.opening is not None and movie.budget is not None:
                break
    except IndexError:
        pass
    results.append(movie.to_json())
    print(movie.to_json())
    counter += 1
    print("Crawled %d movie(s)!" % counter)
    if counter % SAVE_FREQ == 0 and counter > 0:
        save_to_file()


def main():
    global counter, results
    counter = 0
    results = list()
    try:
        movies = read_json_file(DATA_PATH)
        if PROCESSES > 1:
            args_list = []
            for movie in movies:
                new_movie = Movie()
                new_movie.title = movie["title"]
                new_movie.url = movie["url"]
                args_list.append((URL_PREFIX + movie["url"], new_movie))
        else:
            for movie in movies:
                new_movie = Movie()
                new_movie.title = movie["title"]
                new_movie.url = movie["url"]
                crawl_movie((URL_PREFIX + movie["url"], new_movie))
        if PROCESSES > 1:
            with ThreadPool(PROCESSES) as pool:
                for result in pool.map(crawl_movie, args_list):
                    pass
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
