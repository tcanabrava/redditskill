from mycroft import MycroftSkill, intent_file_handler


class RedditSkill(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize():
        self.register_entity_file('data.entity')
        self.register_intent_file('reddit_download.intent', self.handle_reddit_download)
        self.register_intent_file('reddit_show.intent', self.handle_reddit_show)


    def handle_reddit_show(self, message):
        self.speak_dialog("reddit_show")

    def handle_reddit_download(self, message):
        self.speak_dialog("reddit_download")

def create_skill():
    return RedditSkill()

