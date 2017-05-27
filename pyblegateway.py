import re
import requests
from bs4 import BeautifulSoup

# Set this to your preferred default bible version.
BIBLE_VERSION = 'ESV'

BASE_URL = 'https://www.biblegateway.com/'
PASSAGE_URL = 'passage/'


def get_verse_of_the_day(version=BIBLE_VERSION):
    data = requests.get(BASE_URL)
    soup = BeautifulSoup(data.content, 'html.parser')
    votd_ref = soup.find(class_='votd-box').a.text
    return get_passage(votd_ref, version)


def get_passage(passage, version=BIBLE_VERSION, vnums=False, vnum_brackets='[]'):
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
                    chapter_number.replace_with(vnum_brackets[0] + '1'
                                                + vnum_brackets[1] + ' ')
                else:
                    chapter_number.decompose()

            # Deal with verse numbers
            for verse_number in p.find_all('sup', class_='versenum'):
                if vnums:  # If wanted, enclose in defined brackets
                    verse_number.replace_with(vnum_brackets[0] +
                                              verse_number.text.strip() +
                                              vnum_brackets[1] + ' ')
                else:  # If not wanted, remove them
                    verse_number.decompose()

            # Remove footnotes, crossrefs, etc
            for junk in p.find_all('sup', class_=['footnote',
                                                  'crossreference']):
                junk.decompose()

            # Remove weird and/or multiple whitespace characters with a space
            result += re.sub('\s+', ' ', p.text) + ' '

        clean_reference = passage.h1.span.text
        version = passage['class'][0].replace('version-', '')

        result += '\n{} {}\n\n'.format(clean_reference, version)

    return result
