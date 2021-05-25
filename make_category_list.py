"""
Create genres, actors, directors and creators list from the dataset (used for demo webapp).
"""
import requests
from tqdm import tqdm
import pickle
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
from crawler.data_utils import read_json_file
from crawler.utils import HDR


global organizations
global count
PROCESSES = 10

def get_organization_name(url):
    global organizations, count
    print("Crawling %s..." % url)
    source = requests.get("https://www.imdb.com" + url, headers=HDR)
    if source.status_code != 200:
        print("Cannot get organization name! Status code: %d"
              % source.status_code)
        print(source.text)
        return
    soup = BeautifulSoup(source.text, 'html.parser')
    try:
        name = soup.select("title")[0].text
    except IndexError:
        print("Cannot get organization name!")
        return
    r_index = name.index("With") + 5
    l_index = name.index("\n(Sorted by Popularity Ascending) - IMDb")
    organizations[url] = name[r_index:l_index]
    count += 1
    print("Crawled %d" % count)


if __name__ == "__main__":
    global organizations
    global count
    data = read_json_file("crawler/output/imdb.json")
    genres = set()
    content_ratings = set()
    actors = set()
    directors = set()
    creators = set()
    organizations = dict()
    for movie in data:
        genre = movie["genre"] if type(movie["genre"]) == list else [movie["genre"]]
        for g in genre:
            genres.add(g)

        content_ratings.add(movie["content_rating"])

        actor = movie["actor"] if type(movie["actor"]) == list else [movie["actor"]]
        for a in actor:
            if a["@type"] == "Person":
                actors.add(a["name"])

        director = movie["director"] if type(movie["director"]) == list else [movie["director"]]
        for d in director:
            if d["@type"] == "Person":
                directors.add(d["name"])

        creator = movie["creator"] if type(movie["creator"]) == list else [movie["creator"]]
        for c in creator:
            if c["@type"] == "Person":
                creators.add(c["name"])
            elif c["@type"] == "Organization":
                if c["url"]:
                    organizations[c["url"]] = None
    try:
        genres.remove(None)
    except KeyError:
        pass
    try:
        content_ratings.remove(None)
    except KeyError:
        pass
    try:
        actors.remove(None)
    except KeyError:
        pass
    try:
        directors.remove(None)
    except KeyError:
        pass
    try:
        creators.remove(None)
    except KeyError:
        pass

    args = []
    print(len(organizations.keys()))
    count = 0
    for org in organizations:
        args.append(org)
    with ThreadPool(PROCESSES) as pool:
        for result in pool.map(get_organization_name, args):
            pass

    # print(genres)
    # print(content_ratings)
    # print(actors)
    # print(directors)
    # print(creators)
    print(organizations)

    with open("webapp/prediction/categories.pkl", "wb") as file:
        pickle.dump((genres, content_ratings, actors, directors, creators, organizations), file)

