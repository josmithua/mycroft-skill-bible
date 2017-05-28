from os.path import dirname

import feedparser
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

import pyblegateway

# Set this to your preferred uttered bible version
BIBLE_VERSION = 'KJV'

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
        verse, reference = pyblegateway.get_verse_of_the_day(BIBLE_VERSION).split('\n')
        self.speak_dialog("votd", data={"verse": verse, "reference": reference})

    def stop(self):
        pass


def create_skill():
    return BibleSkill()
