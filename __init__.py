from mycroft import MycroftSkill, intent_file_handler
from . import reddit
from typing import Any
from pathlib import Path

def get_data_type(data_type: str) -> Any:
    if data_type in ["video", "videos", "film", "films", "movie", "movies"]:
        return reddit.Reddit.DataTypes.VIDEO
    elif data_type in ["image", "images", "photo", "photos", "picture", "pictures"]:
        return reddit.Reddit.DataTypes.IMAGES
    else:
        return reddit.Reddit.DataTypes.ALL

class RedditSkill(MycroftSkill):
    def __init__(self) -> None:
        MycroftSkill.__init__(self)
        self.download_folder = Path.home()
        self.max_nr_videos = 0
        self.max_nr_images = 0
        self.reddit_client_id = ""
        self.reddit_client_secret = ""
        self.reddit_user_agent = ""
    #

    def initialize(self) -> None:
        self.register_entity_file("data.entity")
        self.register_intent_file("reddit_download.intent", self.handle_reddit_download)
        self.register_intent_file("reddit_show.intent", self.handle_reddit_show)
        self.register_intent_file("reddit_play.intent", self.handle_reddit_video)

        self.settings_change_callback = self.on_settings_changed

        self.gui.register_handler('reddit.video.next', self.play_next_video)
        self.gui.register_handler('reddit.video.prev', self.play_previous_video)

        self.on_settings_changed()
        self.createRedditController()
    #

    def on_settings_changed(self):
        self.download_folder = self.settings.get('download_folder')
        self.max_nr_videos = self.settings.get("maximum_amount_videos", 10)
        self.max_nr_images = self.settings.get("maximum_amount_images", 10)
        self.reddit_client_id = self.settings.get("reddit_client_id")
        self.reddit_client_secret = self.settings.get("reddit_client_secret")
        self.reddit_user_agent = self.settings.get("reddit_user_agent")
    #

    def createRedditController(self) -> None:
        self.redditController = reddit.Reddit(
            mycroft=self,
            client_id=self.reddit_client_id,
            client_secret=self.reddit_client_secret,
            user_agent=self.reddit_user_agent
        )
    #


    def handle_reddit_show(self, message) -> None:
        show_data_type = message.data.get("data")
        show_data_community = message.data.get("community")

        if show_data_community is None:
            self.speak(f"I need at least one community to show {show_data_type}")
            return

        images = self.redditController.image_list(
            community=show_data_community,
            max_images=self.max_nr_images
        )

        if not images:
            self.speak("No images returned to show")
            return

        for image in images:
            self.log.info(f"{image['Title']}, {image['Image']}")

        self.gui["images"] = images
        self.gui.show_page("show_images.qml")
    #

    def handle_reddit_video(self, message) -> None:
        show_data_type = message.data.get("data")
        show_data_community = message.data.get("community")
        self.speak(f"Looking for videos on the {show_data_community} subreddit")

        if show_data_community is None:
            self.speak(f"I need at least one community to show {show_data_type}")
            return


        videos = self.redditController.video_list(
            community=show_data_community,
            max_videos=self.max_nr_videos
        )

        if not videos:
            self.speak("No videos returned to play")
            return

        for video in videos:
            self.log.info(f"{video['Title']}, {video['Video']}")

        self.videos = videos
        self.currentVideoIndex = -1
        self.play_next_video()
    #

    def play_next_video(self) -> None:
        self.currentVideoIndex = len(self.videos) % self.currentVideoIndex + 1
        self.log.info(f"Playing video {self.currentVideoIndex}")
        self.play_current_video()
    #

    def play_previous_video(self) -> None:
        self.currentVideoIndex -= 1
        if self.currentVideoIndex < 0:
            self.currentVideoIndex = len(self.videos) - 1
        #
        self.play_current_video()
    #

    def play_current_video(self) -> None:
        self.log.info(f"Playing video {self.currentVideoIndex}")

        self.log.info("Saving video")
        local_url = self.redditController.save_to_temp(self.videos[self.currentVideoIndex]['Video'])
        if not local_url:
            self.speak("Could not save the video in a temporary folder for playing.")
            self.log.info("Could not save the video in a temporary folder for playing.")
        #

        self.log.info(f"Video found, starting to play {local_url}")
        self.gui["videoTitle"] = self.videos[self.currentVideoIndex]['Title']
        self.gui["videoUrl"] = local_url
        self.gui.show_page("show_videos.qml")
    #

    def handle_reddit_download(self, message) -> None:
        show_data_type = message.data.get("data")
        show_data_community = message.data.get("community")
        if show_data_type is None:
            self.speak(f"I don't understand what kind of data do you want to download. Images or Movies?")
            return
        #

        if show_data_community is None:
            self.speak(f"I need at least one community to download {show_data_type}")
            return
        #

        self.speak_dialog("reddit_show")

        data_type = get_data_type(show_data_type)

        self.redditController.download(
            data_type=data_type,
            communities=[show_data_community],
            download_folder=self.download_folder,
            max_images=self.max_nr_images,
            max_videos=self.max_nr_videos
        )
    #


def create_skill() -> RedditSkill:
    return RedditSkill()
#
