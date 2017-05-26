from os.path import dirname

import feedparser
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'sm1th'

LOGGER = getLogger(__name__)

class BibleSkill(MycroftSkill):
    def __init__(self):
        super(BibleSkill, self).__init__(name="BibleSkill")

    def initialize(self):
        self.load_data_files(dirname(__file__))

        # Verse of the day intent
        votd_intent = IntentBuilder("VotdIntent").\
            require("VotdKeyword").build()
        self.register_intent(votd_intent, self.handle_votd_intent)

    def handle_votd_intent(self, message):
        votd_url = "https://www.biblegateway.com/usage/votd/rss/votd.rdf"
        data = feedparser.parse(votd_url)
        try:
            verse = str(data['entries'][0]['content'][0]['value'])
            reference = str(data['entries'][0]['title'])
            self.speak_dialog("votd", data={"verse": verse,
                                            "reference": reference})
        except Exception as e:
            self.speak("Sorry, something went wrong.")

    def stop(self):
        pass

def create_skill():
    return BibleSkill()
