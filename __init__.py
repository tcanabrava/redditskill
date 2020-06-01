from mycroft import MycroftSkill, intent_file_handler
from . import reddit

def get_data_type(self, data_type: str) -> Any:
    if data_type in ["video", "videos", "film", "films", "movie", "movies"]:
        return reddit.Reddit.DataTypes.VIDEO
    elif data_type in ["image", "images", "photo", "photos", "picture", "pictures"]:
        return reddit.Reddit.DataTypes.IMAGES
    else:
        return reddit.Reddit.DataTypes.ALL

class RedditSkill(MycroftSkill):
    def __init__(self) -> None:
        MycroftSkill.__init__(self)

    def initialize(self) -> None:
        self.register_entity_file("data.entity")
        self.register_intent_file("reddit_download.intent", self.handle_reddit_download)
        self.register_intent_file("reddit_show.intent", self.handle_reddit_show)


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
            self.speak(f"I don't understand what kind of data do you want to download. Videos or Movies?")
            return

        if show_data_community is None:
            self.speak(f"I need at least one community to download {show_data_type}")
            return

        self.speak_dialog("reddit_show")
        self.speak(f"you want to display {show_data_type} from {show_data_community}")

        data_type = get_data_type(show_data_type)
        downloader = reddit.Reddit()
        downloader.download_all(data_type, [show_data_community])


def create_skill() -> RedditSkill:
    return RedditSkill()

