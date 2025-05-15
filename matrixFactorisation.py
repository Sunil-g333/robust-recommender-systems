from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
import pandas as pd
import pickle

ratings = pd.read_csv('ratings.csv')

reader = Reader(rating_scale=(0.5, 5.0))
data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)

trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

model = SVD()
model.fit(trainset)

with open('svd_model.pkl', 'wb') as f:
    pickle.dump(model, f)


# # Example: Predict for user 1 on unseen movie 100
# prediction = model.predict(uid=1, iid=100)
# print(prediction.est)
