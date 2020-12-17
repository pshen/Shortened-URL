import json
from datetime import datetime
from pathlib import Path

import falcon
import gunicorn.glogging
import validators
from falcon_cors import CORS
from threading import Lock

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

    def __init__(self):
        super().__init__()
        self.lock = Lock()
        self.id = 1000000
        self.url2id = {}
        self.id2url = {}
        self.logger = gunicorn.glogging.Logger
        # url2id
        self.url2id_path = Path('url2id.json')
        if self.url2id_path.exists():
            self.url2id = json.loads(self.url2id_path.read_text())
            self.id = self.url2id['id']
        # id2url
        self.id2url_path = Path('id2url.json')
        if self.id2url_path.exists():
            self.id2url = json.loads(self.id2url_path.read_text())

    def sync2disk(self):
        # sync the data to disk -> save
        with self.lock:
            self.url2id['id'] = self.id
            self.url2id_path.write_text(json.dumps(self.url2id))
            self.id2url_path.write_text(json.dumps(self.id2url))

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

    def on_get(self, req, resp):
        # https://stackoverflow.com/questions/34821974/how-to-serve-a-static-webpage-from-falcon-application
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'
        resp.body = f'''
        {HTML_PAGE_HEADER}
        {HTML_PAGE_FOOTER}
        '''

    def on_post(self, req, resp):
        print(req.params)
        orig_url = req.params['url']
        # validate url
        if not validators.url(orig_url):
            # Bad request
            resp.status = falcon.HTTP_400
            resp.content_type = 'text/html'
            resp.body = f'''
            {HTML_PAGE_HEADER}
            <p>Bad Request: inputted {orig_url} is an invalid URL</p> 
            {HTML_PAGE_FOOTER}
'''
        else:
            if orig_url in self.url2id:
                unencoded_id = self.url2id[orig_url]
                encoded_id = self.encode(unencoded_id)
            else:
                self.url2id[orig_url] = self.id
                encoded_id = self.encode(self.id)
                self.id2url[encoded_id] = {'url': orig_url, 'views': 0, 'accessed_time': datetime.now().isoformat()}
                self.id += 1
                # save to disk
                self.sync2disk()

            resp.status = falcon.HTTP_ACCEPTED
            resp.content_type = 'text/html'
            resp.body = f''' 
            {HTML_PAGE_HEADER}
                <p> {orig_url} </p>
                <p> shortened to -> </p>
                <p> <a href="http://localhost:8000/{encoded_id}">http://localhost:8000/{encoded_id}</a> </p>
            {HTML_PAGE_FOOTER}
            '''


class Redirect:
    def __init__(self):
        self.id2url = {}
        self.id2url_path = Path('id2url.json')
        if self.id2url_path.exists():
            self.id2url = json.loads(self.id2url_path.read_text())

    def refresh(self):
        if self.id2url_path.exists():
            self.id2url = json.loads(self.id2url_path.read_text())

    def sync2disk(self):
        self.id2url_path.write_text(json.dumps(self.id2url))

    def on_get(self, req, resp, encoded_id):
        self.refresh()
        if encoded_id not in self.id2url:
            raise falcon.HTTPBadRequest(f'Bad request: the {encoded_id} is not a valid id')
        else:
            self.id2url[encoded_id]['views'] += 1
            self.id2url[encoded_id]['accessed_time'] = datetime.now().isoformat()
            # write the change to disk
            self.sync2disk()
            raise falcon.HTTPMovedPermanently(self.id2url[encoded_id]['url'])


def create_app():
    cors = CORS(allow_all_origins=True, allow_methods_list=['GET'])
    api = falcon.API(middleware=[cors.middleware])
    # https://stackoverflow.com/questions/34618619/data-passing-app-in-falcon-python
    api.req_options.auto_parse_form_urlencoded = True
    api.add_route('/', ShortenedURL())
    api.add_route('/{encoded_id}', Redirect())
    return api


def get_app():
    return create_app()