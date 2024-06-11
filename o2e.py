#!/usr/bin/env python
"""
So this simple sciprt relies on the following python packages:

- loguru
- omnivoreq
- mkepub

You also need to have an Omnivore API key (saved in an `API.key` file)
in the same directory as the script itself, and a `cover.jpg` file too.

**NOTE**
The generated EPUB file is not always accepted by Amazon's send to kindle
service, because there might be some validation errors.
"""
import sys
import datetime
from loguru import logger
from omnivoreql import OmnivoreQL
import mkepub

LF = "{time:YYYY-MM-DD HH:mm:ss} {level} {file:<20} {line:4} {message} "

logger.add("o2e.log", rotation="2 days", compression="zip", format=LF)


@logger.catch(onerror=lambda _: sys.exit(1))
def main():
    """
    This is the business part.
    """
    with open('API.key', 'r', encoding='utf-8') as k:
        token = k.read().strip()

    logger.debug("API key found")

    book = mkepub.Book(title='OmniVore saved articles')

    oclient = OmnivoreQL(token)
    profile = oclient.get_profile()
    user=profile['me']['profile']['username']

    # limit: number of articles
    # query: newest by the bellow setting, can be changed to saved asc
    articles = oclient.get_articles(limit=20, query='sort:saved-desc')

    for item in articles['search']['edges']:
        article = oclient.get_article(username=user, slug=item['node']['slug'])
        if article['article']['article']['isArchived'] is False:

            content = ''
            clabel  = ''
            aid     = article['article']['article']['id']
            labels  = article['article']['article']['labels']

            logger.debug("ID: " + aid)

            if labels and 'name' in labels[0]:
                clabel = ', '.join(['#' + str(e) +
                                    ' ' for e in [dict['name']
                                                  for dict in labels]])

            if article['article']['article']['author']:
                content += '<h3>' + article['article']['article']['author'] + '</h3>'
            else:
                content += '<h3><i>Author missing</i></h3>'

            if article['article']['article']['title'].replace('&','&amp;'):
                content += '<h2>'
                content += article['article']['article']['title'].replace('&','&amp;')
                content += '</h2>'
            else:
                content += '<h2><i>Title missing</i></h2>'

            if article['article']['article']['url']:
                content += '<h6>' + article['article']['article']['url'] + '</h6>'

            if clabel:
                content += '<h6>' + clabel + '</h6>'

            content += article['article']['article']['content']

            book.add_page(article['article']['article']['title'].replace('&','&amp;'),
                          content)

            oclient.archive_article(aid)

    with open('cover.jpg', 'rb', encoding='utf-8') as file:
        book.set_cover(file.read())

    with open('base.css', encoding='utf-8') as file:
        book.set_stylesheet(file.read())


    book.save('Omnivore-newest-' +
              datetime.datetime.now().strftime("%Y-%m-%d") +
              '.epub')

if __name__ == "__main__":
    main()
