import json
import tweepy 
from tweepy import OAuthHandler
import pandas as pd
import datetime
from datetime import datetime
from datetime import datetime, timedelta


class TwitterBot(object): 
    def __init__(self, config):
        consumer_key = config['CONSUMER_KEY']
        consumer_secret = config['CONSUMER_SECRET']
        access_token = config['ACCESS_TOKEN']
        access_token_secret = config['ACCESS_TOKEN_SECRET']
  
        try: 
            self.auth = OAuthHandler(consumer_key, consumer_secret) 
            self.auth.set_access_token(access_token, access_token_secret) 
            self.api = tweepy.API(self.auth) 
            print("Connected")
        except: 
            print("Error: Authentication Failed") 
            
        self.alpha_accounts = config['ALPHA_ACCOUNTS']
        self.get_new_follows()
            
    def get_new_follows(self):
        self.new_follows = {}
        self.all_follows = []
        for account in self.alpha_accounts:
            print(f'Checking {account}')
            watchlist = []
            # Check most recent follows and add them to list
            for friend in tweepy.Cursor(self.api.friends,screen_name=account).items(10):
                watchlist.append(friend.screen_name)
                self.all_follows.append(friend.screen_name)
            #self.new_follows[account] = watchlist
        self.df = pd.DataFrame(self.all_follows,columns=['hot_acct'])
        self.df = self.df.groupby(['hot_acct']).size().reset_index(name='counts')
        #self.df.sort_values(by='counts', ascending=False)
        self.set_hot_follows()
        self.get_follower_count()
        self.get_count_delta()
        
    def set_hot_follows(self):
        self.df = self.df[self.df['counts']>1]
        print(self.df)

        
    def get_follower_count(self):
        hot_count =[]
        for hf in self.df['hot_acct']:
            count = self.api.get_user(hf).followers_count
            hot_count.append(count)
        self.df['subscribers'] = hot_count
        
        #add timestamp
        self.df['timestamp']= datetime.today().strftime('%Y-%m-%d')
        self.df.to_csv('twitterReport_'+ datetime.today().strftime('%Y-%m-%d')+'.csv',index=False)
        #self.df.to_csv('twitterReport_Prev.csv',index=False)
        
    def get_count_delta(self):
        priordate = datetime.today() - timedelta(days=1)
        priordate = priordate.strftime('%Y-%m-%d')
        priorcsv = 'twitterReport_'+ priordate+'.csv'
        #priorcsv = 'twitterReport_Prev.csv'
        
        try:
            self.df2 = pd.read_csv(priorcsv)
            self.df2 = self.df2.rename({'subscribers': 'prior_subscribers'}, axis=1)
            self.df2 = pd.merge(self.df, self.df2[['hot_acct','prior_subscribers']], how ='left', left_on= 'hot_acct', right_on='hot_acct')
            self.df2['subscriber delta'] = self.df2['subscribers']- self.df2['prior_subscribers']
            print(self.df2)
            self.df2.to_csv('twitterReportwithcount_'+ datetime.today().strftime('%Y-%m-%d')+'.csv',index=False)
            #self.df2.to_csv('twitterReportwithcount.csv',index=False)
        except: 
            print("Error: The jews took your data") 
            

