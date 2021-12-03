import pandas as pd

from dash_modules_generators.engagements import *
from dash_modules_generators.basics import *
from dash_modules_generators.influential_countries import *
from dash_modules_generators.graph_analysis import *

from constants.dash_constants import *
from constants.common import TWEETS_PATH
from constants.country_config import COUNTRY

from pathlib import Path

import warnings
warnings.filterwarnings('ignore')


class DashGenerator():
    def __init__(self):

        Path(DATA_DASH_PATH).mkdir(parents=True, exist_ok=True)

        # load the file containing selected country tweets
        self.tweets = pd.read_csv(TWEETS_PATH)
        # storing min and max date of the data
        self.min_date = self.tweets['tweet_date'].min()
        self.max_date = self.tweets['tweet_date'].max()

        self.retweets = get_retweets(self.tweets)
        self.G = None
        self.G_pruned = None

    def generate_basic(self):
        # create `basics` directory  if not existing
        Path(DATA_DASH_PATH + "basics").mkdir(parents=True, exist_ok=True)

        generate_dash_basic_stats(self.tweets, True)
        generate_dash_daily_tweets(self.tweets, True)

        generate_dash_hashtags(
            self.tweets, self.min_date, self.max_date, True)
        generate_dash_mentions(
            self.tweets, self.min_date, self.max_date, True)
        generate_dash_sentiments(
            self.tweets, self.min_date, self.max_date, True)

        generate_dash_potentially_sensitive_tweets(self.tweets, True)

    def generate_influential_countries(self):
        # create `influencers` directory if not existing
        Path(DATA_DASH_PATH + "influencers").mkdir(parents=True, exist_ok=True)

        top_influential_countries = get_top_influential_countries(
            self.tweets)
        top_influential_countries_df = generate_dash_influential_countries(
            top_influential_countries, True)

        # Saving tweets from the top influential countries for word frequencies analysis
        generate_dash_influential_countries_tweets(
            self.tweets, top_influential_countries_df, True)

    def generate_influential_users(self):
        # create `influencers` directory if not existing
        Path(DATA_DASH_PATH + "influencers").mkdir(parents=True, exist_ok=True)

        all_interacting_users = get_all_interacting_users(self.tweets)
        weighted_interacting_edges = get_weighted_interacting_edges(
            self.tweets)
        self.G = create_weighted_directed_graph(
            all_interacting_users, weighted_interacting_edges)
        top_ranking = get_top_ranked_users(self.G)
        generate_dash_influential_users(self.tweets, top_ranking, True)

    def generate_networking_data(self):
        Path(DATA_DASH_PATH + "networking").mkdir(parents=True, exist_ok=True)

        generate_cytograph_data(self.G_pruned)

    def generate_communities(self):
        Path(DATA_DASH_PATH + "networking").mkdir(parents=True, exist_ok=True)
        self.G_pruned = get_min_degree_graph(self.G, 0)  # 5)
        get_communities(self.G_pruned, self.tweets, True)

    def generate_bursty_quoted(self):
        Path(DATA_DASH_PATH + "quoted").mkdir(parents=True, exist_ok=True)
        quoted_tws = get_quoted_tweets(self.tweets)
        quoted_tws = get_quoted_tweets_by_date(
            quoted_tws, self.min_date, self.max_date)
        bursty_quoted_tws = get_bursty_quoted_tweets(quoted_tws)

        quoted_tws_by_sentiment_spreadrate = get_high_spreadrate_quoted_by_sentiment(
            bursty_quoted_tws)
        generate_dash_bursty_quotes_by_sentiment(
            bursty_quoted_tws, quoted_tws_by_sentiment_spreadrate, True)

    def generate_global_retweets(self):
        Path(DATA_DASH_PATH + "rts/global").mkdir(parents=True, exist_ok=True)

        neg_global_retweet = self.retweets[(self.retweets['tweet_sentiment'] == 'negative') &
                                           (self.retweets['retweeted_tweet_date'].between(self.min_date, self.max_date, inclusive='both'))]

        pos_global_retweet = self.retweets[(self.retweets['tweet_sentiment'] == 'positive') &
                                           (self.retweets['retweeted_tweet_date'].between(self.min_date, self.max_date, inclusive='both'))]

        all_global_retweet = self.retweets[(self.retweets['retweeted_tweet_date'].between(
            self.min_date, self.max_date, inclusive='both'))]

        if COUNTRY:
            # If country specific then global tweets should exclude the country's tweets
            neg_global_retweet = neg_global_retweet[neg_global_retweet['retweeted_user_geo_coding'] != COUNTRY]
            pos_global_retweet = pos_global_retweet[pos_global_retweet['retweeted_user_geo_coding'] != COUNTRY]
            all_global_retweet = all_global_retweet[all_global_retweet['retweeted_user_geo_coding'] != COUNTRY]

        generate_dash_bursty_retweets(
            pos_global_retweet, True, POS_GLOBAL_RTS_TREND_PATH, POS_GLOBAL_RTS_INFO_PATH)
        generate_dash_bursty_retweets(
            neg_global_retweet, True, NEG_GLOBAL_RTS_TREND_PATH, NEG_GLOBAL_RTS_INFO_PATH)
        generate_dash_bursty_retweets(
            all_global_retweet, True, ALL_GLOBAL_RTS_TREND_PATH, ALL_GLOBAL_RTS_INFO_PATH)

    def generate_local_retweets(self):
        Path(DATA_DASH_PATH + "rts/local").mkdir(parents=True, exist_ok=True)
        neg_local_retweet = self.retweets[(self.retweets['tweet_sentiment'] == 'negative') &
                                          (self.retweets['retweeted_user_geo_coding'] == COUNTRY) &
                                          (self.retweets['retweeted_tweet_date'].between(self.min_date, self.max_date, inclusive='both'))]

        pos_local_retweet = self.retweets[(self.retweets['tweet_sentiment'] == 'positive') &
                                          (self.retweets['retweeted_user_geo_coding'] == COUNTRY) &
                                          (self.retweets['retweeted_tweet_date'].between(self.min_date, self.max_date, inclusive='both'))]

        all_local_retweet = self.retweets[(self.retweets['retweeted_user_geo_coding'] == COUNTRY) &
                                          (self.retweets['retweeted_tweet_date'].between(self.min_date, self.max_date, inclusive='both'))]

        generate_dash_bursty_retweets(
            pos_local_retweet, True, POS_LOCAL_RTS_TREND_PATH, POS_LOCAL_RTS_INFO_PATH)
        generate_dash_bursty_retweets(
            neg_local_retweet, True, NEG_LOCAL_RTS_TREND_PATH, NEG_LOCAL_RTS_INFO_PATH)
        generate_dash_bursty_retweets(
            all_local_retweet, True, ALL_LOCAL_RTS_TREND_PATH, ALL_LOCAL_RTS_INFO_PATH)


if __name__ == '__main__':
    dg = DashGenerator()

    # Generates basics stats about the tweets
    dg.generate_basic()
    print("{} 1/8 Basics data generated {}".format('-'*10, '-'*10))

    # Generates global viral tweets
    dg.generate_global_retweets()
    print("{} 2/8 Global viral retweets data generated {}".format('-'*10, '-'*10))

    # Generates local viral tweets
    if COUNTRY:
        dg.generate_local_retweets()
        print("{} 3/8 Local viral retweets data generated {}".format('-'*10, '-'*10))

    # Generates reactive quoted tweets
    dg.generate_bursty_quoted()
    print("{} 4/8 Reactive tweets data generated {}".format('-'*10, '-'*10))

    # Generates list of top influential countries
    dg.generate_influential_countries()
    print("{} 5/8 Influential countries data generated {}".format('-'*10, '-'*10))

    # Generates list of top influential users
    dg.generate_influential_users()
    print("{} 6/8 Influential users data generated {}".format('-'*10, '-'*10))

    # Generates communities/clusters of users
    dg.generate_communities()
    print("{} 7/8 Communities data generated {}".format('-'*10, '-'*10))

    # Generates data for creating networking graphs
    # Tweets by the clusters of users
    dg.generate_networking_data()
    print("{} 8/8 Networking data generated {}".format('-'*10, '-'*10))
