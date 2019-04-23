#!/usr/bin/env python3
from requests_html import HTMLSession
from ebooklib import epub


def parse(book, ch_count):
    chapters_names = ['Prologue'] + ['Chapter_{}'.format(i) for i in range(1, ch_count+1)]
    domain = 'https://awoiaf.westeros.org'

    chapters = []
    session = HTMLSession()
    for chapter in chapters_names:
        tags = []
        url = f'{domain}/index.php/{book}-{chapter}'
        print(url)
        r = session.get(url)
        content_div = r.html.find('#mw-content-text', first=True)
        for i, tag in enumerate(content_div.find('p')):
            if i == 0:
                continue
            if 'appearing:' == tag.text.lower():
                break
            tags.append(tag.text)
        ctnt = '<h2>{}</h2>'.format(chapter)
        ctnt += '\n'.join(tags)
        chapters.append((chapter, ctnt))
    return chapters


def write_book(bookname, ch_count):
    book = epub.EpubBook()

    # set metadata
    book.set_identifier('id123456')
    book.set_title(bookname)
    book.set_language('en')

    book.add_author('G.R.R. Martin')

    chapterlist = []
    for idx, (chapter, ctnt) in enumerate(parse(bookname, ch_count)):
        c1 = epub.EpubHtml(title=chapter, file_name=f'{chapter}.xhtml', lang='en')
        c1.content = ctnt
        book.add_item(c1)
        chapterlist.append(c1)

    book.toc = ((epub.Section(bookname), tuple(chapterlist)),)

    # add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define CSS style
    style = 'BODY {color: white;}'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

    # add CSS file
    book.add_item(nav_css)

    # basic spine
    book.spine = ['nav']
    book.spine.extend(chapterlist)

    # write to the file
    epub.write_epub(f'{bookname}.epub', book, {})


if __name__ == '__main__':
    books = [('A_Game_of_Thrones', 73), ('A_Clash_of_Kings', 70), ('A_Storm_of_Swords', 82), ('A_Feast_for_Crows', 46)
             , ('A_Dance_with_Dragons', 73)]
    for book, ch_count in books:
        write_book(book, ch_count)
