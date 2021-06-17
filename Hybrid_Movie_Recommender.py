import pandas as pd
pd.set_option('display.max_columns', 20)

### Veri Hazırlama işlemleri ###

movie = pd.read_csv('datasets/movie_lens_dataset/movie.csv')
rating = pd.read_csv('datasets/movie_lens_dataset/rating.csv')
df = movie.merge(rating, how="left", on="movieId")
comment_counts = pd.DataFrame(df["title"].value_counts())
rare_movies = comment_counts[comment_counts["title"] <= 1000].index
common_movies = df[~df["title"].isin(rare_movies)]

user_movie_df = common_movies.pivot_table(index=["userId"], columns=["title"], values="rating")

## Öneri yapılacak kullanıcı ###

user = 108170

### Öneri yapılacak kullanıcının izlediği filmler ###

user_df = user_movie_df[user_movie_df.index == user]

movies_watched = user_df.columns[user_df.notna().any()].tolist()

len(movies_watched)

### Aynı filmleri izleyen diğer kullanıcıların verisi ve idleri ###

movies_watched_df = user_movie_df[movies_watched]

user_movie_count = movies_watched_df.T.notnull().sum()

user_movie_count = user_movie_count.reset_index()

user_movie_count.columns = ["userId", "movie_count"]

perc = len(movies_watched) * 60 / 100
users_same_movies = user_movie_count[user_movie_count["movie_count"] > perc]["userId"]


### Öneri yapılacak kullanıcı ile en benzer kullanıcılar ###
final_df = pd.concat([movies_watched_df[movies_watched_df.index.isin(users_same_movies)],
                      user_df[movies_watched]])

corr_df = final_df.T.corr().unstack().sort_values().drop_duplicates()
corr_df = pd.DataFrame(corr_df, columns=["corr"])
corr_df.index.names = ['user_id_1', 'user_id_2']
corr_df = corr_df.reset_index()

top_users = corr_df[(corr_df["user_id_1"] == user) & (corr_df["corr"] >= 0.70)][
    ["user_id_2", "corr"]].reset_index(drop=True)

top_users = top_users.sort_values(by='corr', ascending=False)

top_users.rename(columns={"user_id_2": "userId"}, inplace=True)

top_users_ratings = top_users.merge(rating[["userId", "movieId", "rating"]], how='inner')
top_users_ratings = top_users_ratings[top_users_ratings["userId"] != user]

### Weighted Average Recommendation Score'un hesaplanması ###

top_users_ratings['weighted_rating'] = top_users_ratings['corr'] * top_users_ratings['rating']

recommendation_df = top_users_ratings.groupby('movieId').agg({"weighted_rating": "mean"})
recommendation_df = recommendation_df.reset_index()

recommendation_df.sort_values(by="weighted_rating", ascending=False)

movies_to_be_recommend = recommendation_df[recommendation_df["weighted_rating"] > 3.55].sort_values("weighted_rating", ascending=False)

### User Based Öneriler ###

movie_recommend_df = movies_to_be_recommend.merge(movie[["movieId", "title"]])["title"].iloc[0:5]

#       Mallrats (1995)
#       Clerks (1994)
#       Exorcist, The (1973)
#       Goonies, The (1985)
#       Dirty Work (1998)


### Kullanıcının izlediği filmlerden en son en yüksek puan verdiği filmin adına göre Item Based öneriler ###

movie_id = rating[(rating["userId"] == user) & (rating["rating"] == 5.0)]. \
    sort_values(by="timestamp", ascending=False)["movieId"][0:1].values[0]

movie_name_5_rate = movie[movie["movieId"] == movie_id]["title"].values[0]
movie_name_5_rate =  user_movie_df[movie_name_5_rate]

movies_from_item_based = user_movie_df.corrwith(movie_name_5_rate).sort_values(ascending=False)

movies_from_item_based[1:6].index

# ['My Science Project (1985)', 'Mediterraneo (1991)',
#       'Old Man and the Sea, The (1958)',
#       'National Lampoon's Senior Trip (1995)', 'Clockwatchers (1997)']














