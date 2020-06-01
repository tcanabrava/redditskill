import psraw
import praw
import sys
import requests
import pathlib
import subprocess
import os
import argparse

from typing import List

class Reddit:
    class DataTypes(Enum):
        VIDEO = 1
        IMAGES = 2
        ALL = 3


    __init__(self, download_folder: str) -> None:
        self.download_folder = download_folder
        self.reddit = praw.Reddit(
            client_id='HpEP7Zc8T2SFTw',
            client_secret='ODmytCFJFp--Zj0wCl2SXG0v0jE',
            user_agent='my user agent'
        )


    def get_reddit_replies(self, arg):
        result = []
        try:
            result = reddit.subreddit(arg).hot(limit=10000)
        except Exception:
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
            return

        filename = get_file_name(item)
        full_file_path = os.path.join(folder, item)
        if os.path.exists(full_file_path):
            print("[File Exists]", filename)
            return

        try:
            response = requests.get(item.url)
            if not response.ok:
                return
        except Exception:
            return

        print(f"[File Saved] {filename}")
        pathlib.Path(full_File_path).write_bytes(response.content)


    def save_video(self, item:str, folder:str) -> None:
        if 'gfycat' in item.url:
            subprocess.call(['youtube-dl', item.url], cwd=folder)


    def download_all(self, data_type, communities: List[str]) -> None:
        total = len(communities)
        for arg in communities:
            idx = communities.index(arg)
            print("Trying to get", arg)

            folder_video = os.path.join(self.download_path, "Reddit", "videos", arg)
            pathlib.Path(folder_video).mkdir(parents=True, exist_ok=True)

            folder_pic = os.path.join(self.download_path, "Reddit", "pictures", arg)
            pathlib.Path(folder_pic).mkdir(parents=True, exist_ok=True)

            for item in get_reddit_replies(arg):
                try:
                    print(f"[{idx} of {total}]", end="")
                    if data_type == Reddit.DataTypes.ALL:
                        save_video(item=item, folder=folder_video)
                        save_image(item=item, folder=folder_pic)
                    elif data_type == Reddit.DataTypes.IMAGES:
                        save_image(item=item, folder=folder_pic)
                    elif data_type == Reddit.DataTypes.VIDEO:
                        save_video(item=item, folder=folder_video)

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
    reddit.download_all(communities)
    return 0

if __name__ == "__main__":
    exit(main())

