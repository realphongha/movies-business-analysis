import pickle


YEAR_LIMIT = 2000
MAX_YEAR = 2021
DICT_PATH = "prediction/model_checkpoint/dict.pkl"

CHECKPOINT_PATH = "prediction/model_checkpoint/checkpoint/imdb.ckpt"

SCALER_PATH = "prediction/model_checkpoint/scaler.joblib"

GENRES, CONTENT_RATINGS, ACTORS, DIRECTORS, CREATORS, ORGANIZATIONS = \
    pickle.load(open("prediction/model_checkpoint/categories.pkl", "rb"))

CONTENT_RATINGS_CHOICES = [(x, x) for x in CONTENT_RATINGS]
