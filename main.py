#!/usr/bin/env python3

import yaml
import time
import argparse

from discord import Webhook, RequestsWebhookAdapter, File
from twitter import TwitterBot


class HFClient:

    def __init__(self, config_path = "config.yaml"):
        # Inject user config
        with open(config_path) as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader) 
        # Load discord webhooks
        WEBHOOK_ID = self.config["discord"]["WEBHOOK_ID"]
        WEBHOOK_TOKEN = self.config["discord"]["WEBHOOK_TOKEN"]
        self.discord_webhook = Webhook.partial(WEBHOOK_ID, WEBHOOK_TOKEN, adapter=RequestsWebhookAdapter())
        return

    def fetch_hot_follows(self):
        hot_accounts = TwitterBot(self.config["twitter"])
        hot_accounts.df['url'] = hot_accounts.df['hot_acct'].apply(lambda x: "https://twitter.com/%s" % x)
        self.hot_follows_df = hot_accounts.df
        return 

    def publish_to_discord(self):
        for _, row in self.hot_follows_df.iterrows():
            msg_out = f"Hot account: {row['hot_acct']}, counts: {row['counts']}, subscribers: {row['subscribers']} (<{row['url']}>)"
            print(msg_out)
            if self.config["main"]["ENABLE_PRODUCTION"]:
                self.discord_webhook.send(msg_out)
        return

    def orchestrate(self):
        while(True):
            # Fetch and send to discord
            self.fetch_hot_follows()
            self.publish_to_discord()
            # Pause for given time lag
            time.sleep(self.config["main"]["FETCH_LAG"])
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hot follows")
    parser.add_argument("--config", dest="config_file", default="config.yaml", help="Path to configuration yaml file.")
    args = parser.parse_args()
    print("Starting up client.")
    HF = HFClient(config_path = args.config_file)
    HF.orchestrate()

