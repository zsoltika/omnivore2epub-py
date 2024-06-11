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

today = datetime.datetime.now().strftime("%Y-%m-%d")
LF    = "{time:YYYY-MM-DD HH:mm:ss} {level} {file:<20} {line:4} {message} "

logger.add("o2e.log", rotation="2 days", compression="zip", format=LF)


@logger.catch(onerror=lambda _: sys.exit(1))
def main():
    """
    This is the business part.
    """
    token = open('API.key', 'r').read().strip()
    logger.debug("API key found")

    book = mkepub.Book(title='OmniVore saved articles')

    oc = OmnivoreQL(token)
    profile = oc.get_profile()
    user=profile['me']['profile']['username']

    # limit: number of articles
    # query: newest by the bellow setting, can be changed to saved asc
    articles = oc.get_articles(limit=20, query='sort:saved-desc')

    for a in articles['search']['edges']:
        article = oc.get_article(username=user, slug=a['node']['slug'])
        if article['article']['article']['isArchived'] is False:

            content = ''
            title   = article['article']['article']['title'].replace('&','&amp;')
            aid     = article['article']['article']['id']
            url     = article['article']['article']['url']
            author  = article['article']['article']['author']
            labels  = article['article']['article']['labels']
            if not author: author = "No author"
            if not title: author = "No title"
            if not url: author = "No URL"

            logger.debug("Title: " + title)
            logger.debug("ID: " + aid)

            if labels and 'name' in labels[0]:
                clabel = ', '.join(['#' + str(e) + ' ' for e in [dict['name'] for dict in labels]])

            if author:
                content += '<h3>' + author + '</h3>'

            if title:
                content += '<h2>' + title + '</h2>'

            if url:
                content += '<h6>' + url + '</h6>'

            if clabel:
                content += '<h6>' + clabel + '</h6>'

            content += article['article']['article']['content']

            book.add_page(title,content)

            oc.archive_article(aid)

    with open('cover.jpg', 'rb') as file:
        book.set_cover(file.read())

    with open('base.css') as file:
        book.set_stylesheet(file.read())


    book.save('Omnivore-newest-' + today + '.epub')

if __name__ == "__main__":
    main()
