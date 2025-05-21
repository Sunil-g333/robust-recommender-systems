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

# ---- Generate predictions for all userId (1-100) and all movieIds ----
movie_ids = ratings['movieId'].unique()
predictions = []

for uid in range(1, 101):  # User IDs from 1 to 100
    for iid in movie_ids:
        pred = model.predict(uid, iid)
        predictions.append({
            'userId': uid,
            'movieId': iid,
            'rating_pred': pred.est
        })

# Save to CSV
pred_df = pd.DataFrame(predictions)
pred_df.to_csv('svd_preds.csv', index=False)
print("✅ svd_preds.csv has been generated.")