import pickle
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler, normalize
from joblib import load
from .settings import YEAR_LIMIT, DICT_PATH, SCALER_PATH


class OneHotEncoding:
    def __init__(self, data):
        dictionary = dict()
        ind = 0
        for sample in data:
            if type(sample) == list:
                for s in sample:
                    if s not in dictionary:
                        dictionary[s] = ind
                        ind += 1
            else:
                if sample not in dictionary:
                    dictionary[sample] = ind
                    ind += 1
        self.dictionary, self.size = dictionary, ind # dictionary and its size

    def encode(self, data, handle_unknown="ignore"):
        new_data = np.zeros((len(data), self.size))
        for i in range(len(data)):
            sample = data[i]
            if type(sample) == list or np.ndarray:
                for s in sample:
                    if s not in self.dictionary:
                        if handle_unknown == "ignore":
                            continue
                        else:
                            raise NotImplementedError("handle_unknown=%s is not implemented" % handle_unknown)
                    new_data[i][self.dictionary[s]] = 1
            else:
                if sample not in self.dictionary:
                    if handle_unknown == "ignore":
                        continue
                    else:
                        raise NotImplementedError("handle_unknown=%s is not implemented" % handle_unknown)
                new_data[i][self.dictionary[sample]] = 1
        return new_data


def split_str(strings):
    return list(map(lambda x: x.strip().lower(), strings.split(";")))


def preprocess(date, duration, budget, actors, directors, creators, organizations, content_ratings):
    data_test = []
    actors_test = []
    content_ratings_test = []
    directors_test = []
    creators_test = []
    organizations_test = []

    actors_test.append(actors)
    content_ratings_test.append(content_ratings)
    directors_test.append(directors)
    creators_test.append(creators)
    organizations_test.append(organizations)
    data_test.append([date.day, date.month, date.year - YEAR_LIMIT, duration, budget])

    with open(DICT_PATH, "rb") as file:
        enc = pickle.load(file)

    actors_test = enc[0].encode(actors_test)
    content_ratings_test = enc[1].encode(content_ratings_test)
    directors_test = enc[2].encode(directors_test)
    creators_test = enc[3].encode(creators_test)
    organizations_test = enc[4].encode(organizations_test)

    for i in range(len(data_test)):
        data_test[i].extend(list(actors_test[i]))
        data_test[i].extend(list(content_ratings_test[i]))
        data_test[i].extend(list(directors_test[i]))
        data_test[i].extend(list(creators_test[i]))
        data_test[i].extend(list(organizations_test[i]))

    data_test = np.asarray(data_test).astype(np.float64)

    scaler = load(SCALER_PATH)
    X_test = normalize(scaler.transform(data_test))

    return X_test
