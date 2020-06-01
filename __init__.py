from mycroft import MycroftSkill, intent_file_handler


class Reddit(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('reddit.intent')
    def handle_reddit(self, message):
        self.speak_dialog('reddit')


def create_skill():
    return Reddit()

