from os.path import dirname
import re

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

import requests
from bs4 import BeautifulSoup

__author__ = 'sm1th'

LOGGER = getLogger(__name__)

# Set this to your preferred uttered bible version
# A list of valid bible versions is available at:
# www.biblegateway.com/versions/index.php
# Ex: RVR1960, EVR-AR, LSG, etc
BIBLE_VERSION = 'ESV'

BASE_URL = 'https://www.biblegateway.com/'
PASSAGE_URL = 'passage/'


def get_verse_of_the_day(version=BIBLE_VERSION):
    data = requests.get(BASE_URL)
    soup = BeautifulSoup(data.content, 'html.parser')
    votd_ref = soup.find(class_='votd-box').a.text
    return get_passage(votd_ref, version)


def get_passage(passage, version=BIBLE_VERSION, vnums=False, vnum_brackets=''):
    data = requests.get(BASE_URL + PASSAGE_URL, {'search': passage,
                                                 'version': version})
    soup = BeautifulSoup(data.content, 'html.parser')
    result = ''

    for passage in soup.find_all('div', class_='passage-content'):
        passage = passage.div
        for p in passage.find_all('p'):

            # Remove line breaks
            for br in p.find_all('br'):
                br.replace_with(' ')

            # Remove chapter numbers. The chapter number is replaced with verse
            # 1 number if verse numbers are wanted
            for chapter_number in p.find_all('span', class_='chapternum'):
                if vnums:
                    chapter_number.replace_with(vnum_brackets[0] + '1' +
                                                vnum_brackets[1] + ' ')
                else:
                    chapter_number.decompose()

            # Deal with verse numbers
            for verse_number in p.find_all('sup', class_='versenum'):
                if not vnums:
                    verse_number.decompose()
                elif vnums and vnum_brackets:  # Enclose in provided brackets
                    if len(vnum_brackets) == 1:
                        # One bracket provided to go on right side of number
                        num_string = (verse_number.text.strip() +
                                      vnum_brackets[0] + ' ')
                    elif len(vnum_brackets) >= 2:
                        # Two brackets provided to go on either side of number
                        num_string = (vnum_brackets[0] +
                                      verse_number.text.strip() +
                                      vnum_brackets[1] + ' ')
                    verse_number.replace_with(num_string)
                else:  # If no brackets provided, leave how it was
                    pass

            # Remove footnotes, crossrefs, etc
            for junk in p.find_all('sup', class_=['footnote',
                                                  'crossreference']):
                junk.decompose()

            # Remove weird and/or multiple whitespace characters
            result += re.sub('\s+', ' ', p.text) + ' '

        clean_reference = passage.h1.span.text
        result += '\n{} {}\n\n'.format(clean_reference, version)

    return result.strip()


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
        verse, reference = pyblegateway.get_verse_of_the_day(BIBLE_VERSION).\
            split('\n')
        self.speak_dialog("votd", data={"verse": verse,
                                        "reference": reference})

    def stop(self):
        pass


def create_skill():
    return BibleSkill()
