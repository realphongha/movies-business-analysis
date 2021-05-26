import datetime
from django.shortcuts import render
from .forms import *
from .preprocess import *
from .settings import *
from .model import get_model
from .utils import *


def predict(request):
    if request.method == "POST":
        form = PredictionForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data["release_date"]
            duration = form.cleaned_data["duration"]
            budget = form.cleaned_data["budget"]
            actors = split_str(form.cleaned_data["actors"])
            directors = split_str(form.cleaned_data["directors"])
            creators = split_str(form.cleaned_data["creators"])
            organizations = split_str(form.cleaned_data["organizations"])
            genres = [x.lower() for x in form.cleaned_data["genres"]]
            content_ratings = form.cleaned_data["content_ratings"].strip().lower()
            actors = [get_best_result(ACTORS, x) for x in actors]
            directors = [get_best_result(DIRECTORS, x) for x in directors]
            creators = [get_best_result(CREATORS, x) for x in creators]
            organizations = [get_best_result(ORGANIZATIONS, x) for x in organizations]

            actors = [x for x in actors if x]
            directors = [x for x in directors if x]
            creators = [x for x in creators if x]
            organizations = [x for x in organizations if x]

            data = preprocess(date, duration, budget, actors, directors, creators, organizations,
                              genres, content_ratings)

            model = get_model(data.shape[1])
            result = model.predict(data)
            rating = round(result[0][0], 1)
            return render(request, 'prediction/predict.html', {'form': form,
                    'rating': rating, 'actors': ", ".join(actors), 
                    'directors': ", ".join(directors),
                    'creators': ", ".join(creators), 
                    'organizations': ", ".join([ORGANIZATIONS[x] for x in organizations])
                })
    else:
        form = PredictionForm()
        return render(request, 'prediction/predict.html', {'form': form})
