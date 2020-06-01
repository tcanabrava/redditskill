import psraw
import praw
import sys
import requests
import pathlib
import subprocess
import os
import argparse

from typing import List

from enum import Enum

class Reddit:
    class DataTypes(Enum):
        VIDEO = 1
        IMAGES = 2
        ALL = 3

    def __init__(self, mycroft, download_folder, limit):
        self.download_folder = download_folder
        self.limit = limit
        self.mycroft = mycroft
        self.reddit = praw.Reddit(
            client_id='HpEP7Zc8T2SFTw',
            client_secret='ODmytCFJFp--Zj0wCl2SXG0v0jE',
            user_agent='my user agent'
        )


    def get_reddit_replies(self, arg):
        result = []
        try:
            result = self.reddit.subreddit(arg).hot(limit=self.limit)
            self.mycroft.speak(f"Getting replies")
        except Exception as e:
            self.mycroft.speak(f"Got zero replies {e}")
            result = [] 
        finally:
            return result


    def get_file_name(self, item):
        filetype = item.url.split('.')[-1]    
        filename = item.title + '_' + item.id + '.' + filetype
        for char in ['(', ')', ',', '@', '!', '?', '/', ';', '"', "'"]:
            filename = filename.replace(char, '')
        filename = filename.replace(' ', '_')

        asciidata = filename.encode("ascii","ignore").decode("utf-8")
        asciidata = '_'.join(asciidata.split('_'))
        return asciidata


    def save_image(self, item:str, folder: str):
        filetype = item.url.split('.')[-1]    

        if not filetype.lower() in ['jpg', 'png', 'gif', 'jpeg']:
            self.mycroft.log.info(f"File does not have a filetype:{item.url}")
            return

        filename = self.get_file_name(item)
        full_file_path = os.path.join(folder, filename)
        if os.path.exists(full_file_path):
            self.mycroft.log.info("[File Exists]", filename)
            return

        try:
            response = requests.get(item.url)
            if not response.ok:
                self.mycroft.log.info("Error downloading file.")
                return
        except Exception as e:
            self.mycroft.log.info(f"Error downloading path {e}")
            return

        self.mycroft.log.info(f"[File Saved] {filename}")
        pathlib.Path(full_file_path).write_bytes(response.content)


    def save_video(self, item:str, folder:str) -> None:
        if 'gfycat' in item.url:
            subprocess.call(['youtube-dl', item.url], cwd=folder)


    def download_all(self, data_type, communities: List[str]) -> None:
        self.mycroft.speak(f"Inside of the reddit library {data_type}")
        total = len(communities)
        for arg in communities:
            idx = communities.index(arg)
            self.mycroft.speak(f"Trying to get {arg}")

            if data_type in [Reddit.DataTypes.ALL, Reddit.DataTypes.VIDEO]:
                folder_video = os.path.join(self.download_folder, "Reddit", "videos", arg)
                pathlib.Path(folder_video).mkdir(parents=True, exist_ok=True)

            if data_type in [Reddit.DataTypes.ALL, Reddit.DataTypes.IMAGES]:
                folder_pic = os.path.join(self.download_folder, "Reddit", "pictures", arg)
                pathlib.Path(folder_pic).mkdir(parents=True, exist_ok=True)
                self.mycroft.speak(f"[{idx} of {total}]")

            for item in self.get_reddit_replies(arg):
                try:
                    if data_type in [Reddit.DataTypes.ALL, Reddit.DataTypes.VIDEO]:
                        self.save_video(item=item, folder=folder_video)

                    if data_type in [Reddit.DataTypes.ALL, Reddit.DataTypes.IMAGES]:
                        self.save_image(item=item, folder=folder_pic)

                except Exception as e:
                    print(f"Error trying to get {arg}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Download Pictures and videos from a Reddit Repository.')
    parser.add_argument(
        '--reddits', 
        metavar='N', 
        type=str, 
        nargs='+',
        help='list of reddits to download')

    args = parser.parse_args()
    communities = args.reddits if args.reddits else reddit_communities

    reddit = Reddit()
    reddit.download_all('/home/tcanabrava/coiso', communities)
    return 0

if __name__ == "__main__":
    exit(main())

