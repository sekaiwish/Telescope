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

channel_whitelist = {'Star Miners'}

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
                    if msg['chatType'] == 'FRIENDS' and msg['chatName'] in channel_whitelist:
                        timestamp = int(datetime.datetime.strptime(msg['timestamp'][:19], '%Y-%m-%dT%H:%M:%S').timestamp())
                        body = msg['message']

                        # Thanks to PescalinPax/MordoJay/Mordecaii for RegEx help
                        world_pattern = re.compile('(?:world|w)?\s*(\d{3})')
                        world_match = world_pattern.search(body)
                        tier_pattern = re.compile('(?:tier|t)?\s*(\d{1})\s*(\d{1,3}\%)?')
                        tier_match = tier_pattern.search(body)
                        body = body.replace(world_match.group(0).strip(), '').replace(tier_match.group(0).strip(), '')
                        location_pattern = re.compile('([a-z]{2}.*)')
                        location_match = location_pattern.search(body)

                        if world_match == None or tier_match == None or location_match == None:
                            res.status = falcon.HTTP_400
                            response = {'error': 'not valid scout data'}
                            res.text = json.dumps(response)
                            return

                        # Handle optional percentage tracking
                        if tier_match.group(2):
                            tier = f'{tier_match.group(1)} {tier_match.group(2)}'
                        else:
                            tier = tier_match.group(1)

                        message_entry = Message(
                            msg['id'],
                            timestamp,
                            msg['sender'],
                            world_match.group(1),
                            tier,
                            location_match.group(0)
                        )

                        """
                        print(message_entry.world)
                        print(message_entry.tier)
                        print(message_entry.location)
                        """

                        # check new message against star presences
                        # within algorithm, create OR update star presences
                    else:
                        response = {'error': 'chat channel not in whitelist'}
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