# movies-business-analysis
Business analysis for movies based on some sources of data: IMDb, boxofficemojo.   
This project includes: crawler for imdb.com and boxofficemojo.com; 
business analysis and deep learning to predict movies' IMDb rating;
a demo webapp to present our experimental results.

# Install requirements:
```pip install -r requirements.txt```

# Run crawler:
```cd crawler```   
```python imdb.py```    
```python boxoffice.py```

# Movies business analysis and deep learning model in movies_business_analysis.ipynb

# Deploy demo webapp:
First download checkpoint and dictionaries (tutorial can be found in webapp/prediction/model_checkpoint)   
Then   
```cd webapp```   
```python manage.py runserver```