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


def folder(download_folder: str, subfolder :str, community: str) -> str:
    created_folder = os.path.join(download_folder, "Reddit", subfolder, community)
    pathlib.Path(created_folder).mkdir(parents=True, exist_ok=True)
    return created_folder
#

class Reddit:
    class DataTypes(Enum):
        VIDEO = 1
        IMAGES = 2
        ALL = 3

    def __init__(self, mycroft, client_id: str, client_secret: str, user_agent: str):
        self.mycroft = mycroft
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.limit = 1000
        self.mycroft.log.info(f"{client_id}, {client_secret}, {user_agent}")
    #

    def get_reddit_replies(self, arg):
        result = []
        try:
            result = self.reddit.subreddit(arg).hot(limit=self.limit)
            self.mycroft.log.info(f"Getting replies")
        except Exception as e:
            self.mycroft.log.info(f"Got zero replies {e}")
            result = []
        finally:
            return result
        #
    #


    def get_file_name(self, item):
        filetype = item.url.split('.')[-1]
        filename = item.title + '_' + item.id + '.' + filetype
        for char in ['(', ')', ',', '@', '!', '?', '/', ';', '"', "'"]:
            filename = filename.replace(char, '')
        #

        filename = filename.replace(' ', '_')

        asciidata = filename.encode("ascii","ignore").decode("utf-8")
        asciidata = '_'.join(asciidata.split('_'))
        return asciidata
    #


    def save_image(self, item:str, folder: str) -> bool:
        filetype = item.url.split('.')[-1]

        if not filetype.lower() in ['jpg', 'png', 'gif', 'jpeg']:
            return False
        #

        filename = self.get_file_name(item)
        full_file_path = os.path.join(folder, filename)
        if os.path.exists(full_file_path):
            self.mycroft.log.info(f"[File Exists] {filename}")
            return False
        #

        try:
            response = requests.get(item.url)
            if not response.ok:
                self.mycroft.log.info("Error downloading file.")
                return False
        except Exception as e:
            self.mycroft.log.info(f"Error downloading path {e}")
            return False
        #

        self.mycroft.log.info(f"[File Saved] {filename}")
        pathlib.Path(full_file_path).write_bytes(response.content)

        return True
    #

    def save_video(self, item:str, folder:str) -> bool:
        self.mycroft.log.info(f"[Video] Trying to download {item.url} to {folder}")
        should_download = False
        for accepted_content in ["youtube", "gfycat"]:
            if accepted_content in item.url:
                should_download = True

        if not should_download:
            return False
        #

        return subprocess.call(['youtube-dl', item.url], cwd=folder) == 0
    #

    def download_photos_and_videos(self,
        data_type,
        community: str,
        video_folder:str,
        photos_folder:str,
        max_images:int,
        max_videos:int) -> None:

        current_images = 0
        current_videos = 0

        try:
            community_posts = self.get_reddit_replies(community)
        except Exception as e:
            self.mycroft.speak(f"Unable to reach reddit, verify the reddit skill configuration")
            return
        #

        for item in community_posts:
            try:
                if (data_type in [Reddit.DataTypes.ALL, Reddit.DataTypes.VIDEO]
                    and current_videos < max_videos
                    and self.save_video(item=item, folder=video_folder)
                ):
                    current_videos += 1
                #

                if (data_type in [Reddit.DataTypes.ALL, Reddit.DataTypes.IMAGES]
                    and current_images < max_images
                    and self.save_image(item=item, folder=photos_folder)
                ):
                    current_images += 1
                #
            except Exception as e:
                    self.mycroft.log.info(f"Error trying to get {community}:")
                    self.mycroft.log.info(f"{e}")
            #

            # Break early from the loop if we finished downloading things
            if data_type == Reddit.DataTypes.IMAGES and current_images >= max_images:
                return
            #

            if data_type == Reddit.DataTypes.VIDEO and current_videos >= max_videos:
                return
            #

            if (data_type == Reddit.DataTypes.ALL
                and current_videos >= max_videos
                and current_images >= max_images
            ):
                return
            #
        #
    #


    def download(self,
        data_type,
        communities: List[str],
        download_folder:str,
        max_images:int,
        max_videos:int) -> None:

        self.mycroft.log.info(f"Inside of the reddit library {data_type}")
        total = len(communities)
        for community in communities:
            idx = communities.index(community)
            self.mycroft.log.info(f"Trying to get {community}")

            video_folder = folder(
                download_folder=download_folder,
                subfolder="video",
                community=community)

            photos_folder = folder(
                download_folder=download_folder,
                subfolder="images",
                community=community)

            self.download_photos_and_videos(
                data_type=data_type,
                community=community,
                video_folder=video_folder,
                photos_folder=photos_folder,
                max_images=max_images,
                max_videos=max_videos
            )
        #
    #
#


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
#

if __name__ == "__main__":
    exit(main())
#

