#!/usr/bin/env python3
import os
import requests
from bs4 import BeautifulSoup
from ebooklib import epub


def parse(book, ch_count):
    headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    }
    chapters_names = ['Prologue'] + ['Chapter_{}'.format(i) for i in range(1, ch_count+1)]
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
        ctnt = '<h2>{}</h2>'.format(chapter)
        ctnt += '\n'.join('<p>{}</p>'.format(t.get_text()) for t in tags)
        chapters.append((chapter, ctnt))
    return chapters


def write_book(bookname, ch_count):
    book = epub.EpubBook()

    # set metadata
    book.set_identifier('id123456')
    book.set_title(bookname)
    book.set_language('en')

    book.add_author('G.R.R. Martin')

    for idx, (chapter, ctnt) in enumerate(parse(book, ch_count)):
        c1 = epub.EpubHtml(title=chapter, file_name=f'{chapter}.xhtml', lang='en')
        c1.content = ctnt
        book.add_item(c1)

    # # define Table Of Contents
    # book.toc = (epub.Link('chap_01.xhtml', 'Introduction', 'intro'),
    #             (epub.Section('Simple book'),
    #              (c1, ))
    #             )

    # add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define CSS style
    style = 'BODY {color: white;}'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

    # add CSS file
    book.add_item(nav_css)

    # basic spine
    book.spine = ['nav', c1]

    # write to the file
    epub.write_epub(f'{bookname}.epub', book, {})


if __name__ == '__main__':
    books = [('A_Game_of_Thrones', 73), ('A_Clash_of_Kings', 70), ('A_Storm_of_Swords', 82), ('A_Feast_for_Crows', 46)
             , ('A_Dance_with_Dragons', 73)]
    for book, ch_count in books:
        write_book(book, ch_count)
