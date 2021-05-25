from django.forms import *

from .settings import *


class PredictionForm(Form):
    release_date = DateField(label="Release date", widget=SelectDateWidget(
        empty_label=("Choose Year", "Choose Month", "Choose Day"), 
        years=range(YEAR_LIMIT, MAX_YEAR+1)), 
    required=True)
    duration = IntegerField(label="Movie length in minutes", min_value=1, required=True)
    budget = IntegerField(label="Movie budget in dollars", min_value=1, required=True)
    actors = CharField(label="Actors (separated by ';')", max_length=200, required=True)
    directors = CharField(label="Directors (separated by ';')", max_length=200, required=True)
    creators = CharField(label="Creators (separated by ';')", max_length=200, required=True)
    organizations = CharField(label="Organizations (separated by ';')", max_length=200, required=True)
    content_ratings = ChoiceField(choices=CONTENT_RATINGS_CHOICES, required=True)
