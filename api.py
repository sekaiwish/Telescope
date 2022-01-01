#!/usr/bin/python -u
import falcon, falcon.asgi, os, json, datetime, re

def setup_files(*files):
    for file in files:
        if not os.path.isfile(file):
            if os.path.exists(file): raise Exception('Require file exists as dir')
            f = open(file, 'x')
setup_files('.auth_keys')
with open('.auth_keys', 'r+') as fp:
    auth_keys = {line.rstrip() for line in fp}

app = falcon.asgi.App()

class Message:
    def __init__(self, id, timestamp, sender, world, tier, location):
        self.id = id
        self.timestamp = timestamp
        self.sender = sender
        self.world = world
        self.tier = tier
        self.location = location

class Star:
    def __init__(self, finder, timestamp, region, location):
        self.finder = finder
        self.timestamp = timestamp
        self.region = region
        self.location = [location]
    def add_location(self, location):
        if len(self.location) < 3:
            self.location.append(location)

class Tests:
    async def on_get(self, req, res):
        res.content_type = falcon.MEDIA_JSON
        if req.get_header('Authorization'):
            res.status = falcon.HTTP_200
            response = {'key': req.get_header('Authorization'), 'method': 'get'}
            res.text = json.dumps(response)
        else:
            res.status = falcon.HTTP_401
    async def on_post(self, req, res):
        res.content_type = falcon.MEDIA_JSON
        if req.get_header('Authorization'):
            res.status = falcon.HTTP_200
            response = {'key': req.get_header('Authorization'), 'method': 'post'}
            res.text = json.dumps(response)
        else:
            res.status = falcon.HTTP_401

class Messages:
    async def purge():
        pass # purge messages/stars older than ?? minutes
    async def on_post(self, req, res):
        # await purge()
        res.content_type = falcon.MEDIA_JSON
        if req.get_header('Authorization'):
            auth_key = req.get_header('Authorization')
            if auth_key in auth_keys:
                res.status = falcon.HTTP_200
                content = json.loads(await req.stream.read())
                for msg in content:
                    if msg['chatType'] == 'FRIENDS' and msg['chatName'] == 'Star Miners':
                        timestamp = int(datetime.datetime.strptime(msg['timestamp'][:19], '%Y-%m-%dT%H:%M:%S').timestamp())
                        # regex match world, tier and location separately
                        # if all 3 contain at least one match, generate new message
                        # check new message against star presences
                        # within algorithm, create OR update star presences
                    else:
                        response = {'error': 'invalid message'}
                        res.text = json.dumps(response)
            else:
                res.status = falcon.HTTP_401
        else:
            res.status = falcon.HTTP_401
    async def on_get(self, req, res):
        pass # handle returning new messages after given timestamp

tests = Tests()
app.add_route('/', tests)
messages = Messages()
app.add_route('/messages', messages)