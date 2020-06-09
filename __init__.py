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

    def initialize(self) -> None:
        self.register_entity_file("data.entity")
        self.register_intent_file("reddit_download.intent", self.handle_reddit_download)
        self.register_intent_file("reddit_show.intent", self.handle_reddit_show)
        self.settings_change_callback = self.on_settings_changed
        self.on_settings_changed()

    def on_settings_changed(self):
        self.download_folder = self.settings.get('download_folder')
        self.max_nr_videos = self.settings.get("maximum_amount_videos", 10)
        self.max_nr_images = self.settings.get("maximum_amount_images", 10)
        self.reddit_client_id = self.settings.get("reddit_client_id")
        self.reddit_client_secret = self.settings.get("reddit_client_secret")
        self.reddit_user_agent = self.settings.get("reddit_user_agent")

    def handle_reddit_show(self, message) -> None:
        show_data_type = message.data.get("data")
        show_data_community = message.data.get("community")
        if show_data_type is None:
            self.speak(f"I don't understand what kind of data do you want to see. Videos or Movies?")
            return

        if show_data_community is None:
            self.speak(f"I need at least one community to display {show_data_type}")
            return

        data_type = get_data_type(show_data_type)
        self.speak_dialog("reddit_show")
        self.speak(f"you want to display {show_data_type} from {show_data_community}")


    def handle_reddit_download(self, message) -> None:
        show_data_type = message.data.get("data")
        show_data_community = message.data.get("community")
        if show_data_type is None:
            self.speak(f"I don't understand what kind of data do you want to download. Images or Movies?")
            return

        if show_data_community is None:
            self.speak(f"I need at least one community to download {show_data_type}")
            return

        self.speak_dialog("reddit_show")

        data_type = get_data_type(show_data_type)
        downloader = reddit.Reddit(
            mycroft=self,
            client_id=self.reddit_client_id,
            client_secret=self.reddit_client_secret,
            user_agent=self.reddit_user_agent
        )

        self.speak("Downloading everything")
        downloader.download_all(data_type, [show_data_community])

    def stop(self) -> None:
        self.stop_beeping()

def create_skill() -> RedditSkill:
    return RedditSkill()

