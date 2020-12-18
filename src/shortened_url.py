import json
from datetime import datetime
from pathlib import Path

import falcon
import gunicorn.glogging
import validators
from falcon_cors import CORS

HTML_PAGE_HEADER = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>URL shortener</title>
</head>
<body>
    <form action="http://127.0.0.1:8000" method="post">
        <input type="text" name="url">
        <button type="submit" name="btn">Submit</button>
    </form>
'''

HTML_PAGE_FOOTER = f'''
        </body>
        </html>
'''


class ShortenedURL:
    """
    URL: foobar.com
    """

    # class members
    id = 1000000
    url2id = {}
    id2url = {}
    url2id_path = Path('url2id.json')
    id2url_path = Path('id2url.json')

    def __init__(self):
        super().__init__()
        self.logger = gunicorn.glogging.Logger
        # url2id
        if ShortenedURL.url2id_path.exists():
            ShortenedURL.url2id = json.loads(ShortenedURL.url2id_path.read_text())
            ShortenedURL.id = ShortenedURL.url2id['id']
        # id2url
        if ShortenedURL.id2url_path.exists():
            ShortenedURL.id2url = json.loads(ShortenedURL.id2url_path.read_text())

    def sync2disk(self):
        # sync the data to disk -> save
        ShortenedURL.url2id['id'] = ShortenedURL.id
        ShortenedURL.url2id_path.write_text(json.dumps(ShortenedURL.url2id))
        ShortenedURL.id2url_path.write_text(json.dumps(ShortenedURL.id2url))

    def encode(self, id):
        # https://github.com/minsuk-heo/coding_interview/blob/master/shorten_url.ipynb

        # base 62 characters
        characters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        base = len(characters)
        ret = []

        # convert base10 id into base62 id for having alphanumeric shorten url
        while id > 0:
            val = id % base
            ret.append(characters[val])
            id = id // base

        # reverse the order of list
        return "".join(ret[::-1])

    def refresh(self):
        if ShortenedURL.id2url_path.exists():
            ShortenedURL.id2url = json.loads(ShortenedURL.id2url_path.read_text())

    def on_get(self, req, resp):
        # https://stackoverflow.com/questions/34821974/how-to-serve-a-static-webpage-from-falcon-application
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'
        resp.body = f'''
        {HTML_PAGE_HEADER}
        {HTML_PAGE_FOOTER}
        '''

    def on_get_stats(self, req, resp, encoded_id):
        # add more on_get functions
        self.refresh()
        resp.content_type = 'text/html'
        if encoded_id not in ShortenedURL.id2url:
            # Bad request
            resp.status = falcon.HTTP_400
            resp.body = f'''
            {HTML_PAGE_HEADER}
            <p> Bad Request: {encoded_id} does not exist </p>
            {HTML_PAGE_FOOTER}
            '''
        else:
            resp.status = falcon.HTTP_200
            orig_url = ShortenedURL.id2url[encoded_id]['url']
            views = ShortenedURL.id2url[encoded_id]['views']
            accessed_time = ShortenedURL.id2url[encoded_id]['accessed_time']
            resp.body = f'''
            {HTML_PAGE_HEADER}
            <p> shortened url : http://localhost:8000/{encoded_id} </p>
            <p> original url : {orig_url} </p>
            <p> views : {views} </p>
            <p> last accessed time : {accessed_time} </p>
            {HTML_PAGE_FOOTER}
            '''

    def on_get_redirect(self, req, resp, encoded_id):
        self.refresh()
        if encoded_id not in ShortenedURL.id2url:
            # Bad request
            resp.status = falcon.HTTP_400
            resp.content_type = 'text/html'
            resp.body = f'''
            {HTML_PAGE_HEADER}
            <p> Bad Request: {encoded_id} does not exist </p>
            {HTML_PAGE_FOOTER}
            '''
        else:
            ShortenedURL.id2url[encoded_id]['views'] += 1
            ShortenedURL.id2url[encoded_id]['accessed_time'] = datetime.now().isoformat()
            # write the change to disk
            self.sync2disk()
            raise falcon.HTTPMovedPermanently(ShortenedURL.id2url[encoded_id]['url'])

    def on_post(self, req, resp):
        orig_url = req.params['url']
        resp.content_type = 'text/html'

        # validate url
        if not validators.url(orig_url):
            # Bad request
            resp.status = falcon.HTTP_400
            resp.body = f'''
            {HTML_PAGE_HEADER}
            <p> Bad Request: {orig_url} is an invalid URL </p> 
            {HTML_PAGE_FOOTER}
'''
        else:
            if orig_url in ShortenedURL.url2id:
                unencoded_id = ShortenedURL.url2id[orig_url]
                encoded_id = self.encode(unencoded_id)
            else:
                ShortenedURL.url2id[orig_url] = ShortenedURL.id
                encoded_id = self.encode(ShortenedURL.id)
                ShortenedURL.id2url[encoded_id] = {'url': orig_url, 'views': 0, 'accessed_time': datetime.now().isoformat()}
                ShortenedURL.id += 1
                # save to disk
                self.sync2disk()

            resp.status = falcon.HTTP_ACCEPTED
            resp.body = f''' 
            {HTML_PAGE_HEADER}
                <p> {orig_url} </p>
                <p> shortened to -> </p>
                <p> <a href="http://localhost:8000/{encoded_id}">http://localhost:8000/{encoded_id}</a> </p>
            {HTML_PAGE_FOOTER}
            '''


def create_app():
    cors = CORS(allow_all_origins=True, allow_methods_list=['GET'])
    api = falcon.API(middleware=[cors.middleware])
    # https://stackoverflow.com/questions/34618619/data-passing-app-in-falcon-python
    api.req_options.auto_parse_form_urlencoded = True
    api.add_route('/', ShortenedURL())
    api.add_route('/{encoded_id}', ShortenedURL(), suffix='redirect')
    api.add_route('/{encoded_id}/stats', ShortenedURL(), suffix='stats')
    return api


def get_app():
    return create_app()