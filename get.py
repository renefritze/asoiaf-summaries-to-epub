#!/usr/bin/env python3
import os
import requests
from bs4 import BeautifulSoup
import pypub


def parse(book, ch_count):
    headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    }
    chapters_names = ['Prologue'] + ['Chapter_{}'.format(i) for i in range(ch_count)]
    domain = 'https://awoiaf.westeros.org'

    chapters = []
    last_h2 = None
    for chapter in chapters_names:
        tags = []
        url = '{}/index.php/{}-{}'.format(domain, book, chapter)
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find('div', id='mw-content-text')
        for tag in content_div.children:
            if tag.name == 'h2':
                last_h2 = tag.text
                continue
            if tag.name == 'p' and last_h2 == 'Synopsis':
                tags.append(tag)
        ctnt = '\n'.join('<p>{}</p>'.format(t.get_text()) for t in tags)
        chapters.append(pypub.create_chapter_from_string(ctnt, title=chapter))
    return chapters


if __name__ == '__main__':
    book = 'A_Game_of_Thrones'
    ch_count = 2  # 72
    epub = pypub.Epub(title=book)
    for chapter in parse(book, ch_count):
        epub.add_chapter(chapter)
    epub.create_epub(os.getcwd())