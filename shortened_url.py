import falcon
import json
import yaml
import validators
import gunicorn.glogging
from falcon_cors import CORS
from pathlib import Path


class ShortenedURL:
    """
    URL: foobar.com
    """

    def __init__(self):
        super().__init__()
        self.id = 1000000
        self.url2id = {}
        self.logger = gunicorn.glogging.Logger
        self.store_path = Path('url2id.json')
        if self.store_path.exists():
            self.url2id = json.loads(self.store_path.read_text())
            self.id = self.url2id['id']

    def sync2disk(self):
        # sync the data to disk -> save
        self.url2id['id'] = self.id
        self.store_path.write_text(json.dumps(self.url2id))

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

    def on_post(self, req, resp):
        req_data = json.load(req.bounded_stream)
        orig_url = req_data['url']

        # validate url
        if not validators.url(orig_url):
            raise falcon.HTTPBadRequest(f'Bad Request: inputted {orig_url} is invalid')

        if orig_url in self.url2id:
            id = self.url2id[orig_url]
            shortened_url = self.encode(id)
        else:
            self.url2id[orig_url] = self.id
            shortened_url = self.encode(self.id)
            self.id += 1
            # save to disk
            self.sync2disk()

        resp.media = {"shortened url": f'foobar.com/{shortened_url}'}
        resp.status = falcon.HTTP_ACCEPTED


def create_app():
    cors = CORS(allow_all_origins=True, allow_methods_list=['GET'])
    api = falcon.API(middleware=[cors.middleware])
    api.add_route('/', ShortenedURL())
    return api


def get_app():
    return create_app()
