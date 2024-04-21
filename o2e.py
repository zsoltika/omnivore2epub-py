#!/usr/bin/env python
import sys, json, datetime
from loguru import logger
from omnivoreql import OmnivoreQL
import mkepub

now   = datetime.datetime.now()
today = now.strftime("%Y-%m-%d")
lf    = "{time:YYYY-MM-DD HH:mm:ss} {level} {file:<20} {line:4} {message} "

logger.add("o2e.log", rotation="2 days", compression="zip", format=lf)


@logger.catch(onerror=lambda _: sys.exit(1))
def main():
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
            title   = article['article']['article']['title']
            title   = title.replace('&','&amp;')
            id      = article['article']['article']['id']
            url     = article['article']['article']['url']
            author  = article['article']['article']['author']
            labels  = article['article']['article']['labels']
            
            if not author: author = "No author" 
            if not title: author = "No title" 
            if not url: author = "No URL" 

            logger.debug("Title: " + title)
            logger.debug("ID: " + id)

            if labels and 'name' in labels[0]:
                labellist = [dict['name'] for dict in labels]
                clabel = ', '.join(['#' + str(e) + ' ' for e in labellist])

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
            
            oc.archive_article(id)

    with open('cover.jpg', 'rb') as file:
        book.set_cover(file.read())

    with open('base.css') as file:
        book.set_stylesheet(file.read())


    efilename = 'Omnivore-newest-' + today + '.epub'
    book.save(efilename)

if __name__ == "__main__":
    main()
