#!/usr/bin/python

###
#
# Create Freight document helper
#
# See README.md in this directory for installation instructions.
#
###

import json, pprint, requests, argparse, os, base64, ConfigParser, datetime


pp = pprint.PrettyPrinter(indent=4)
parser = argparse.ArgumentParser(description="Creates a freight document on a given environment.")

config = ConfigParser.RawConfigParser({'env': 'test', 'client_secret': 'Please set a secret'})
config.add_section("settings")
config.read([os.path.expanduser('~/.tfdevtools.ini')])

# Client secret - See developer.transfollow.com for information on how to obtain one.
client_secret = config.get("settings", "client_secret")
env = config.get("settings", "env")


# There can only be one JSON source, a single file or a group of files
json_source = parser.add_mutually_exclusive_group(required=True)
json_source.add_argument("--json_file", type=str, help="The JSON file to use for FD posting")
json_source.add_argument("--json_dir", type=str, help="A directory containing JSON freight document files")

parser.add_argument("--env", type=str, help="The target environment: test, acceptance or partner")
parser.add_argument("--client_secret", type=str, help="The client secret, used to authenticate with the API service")
parser.add_argument("--user", type=str, help="The existing user email address used to create the FD")
parser.add_argument("--password", type=str, help="The existing user password used to create the FD")
parser.add_argument("--one_user", action="store_true", help="Sets all the role email addresses to the user used for authentication, overriding the JSON addresses")
parser.add_argument("--sign_fd", action="store_true", help="Signs the freight document. Note that the user needs to have signing permission. Generally this means the carrier.")
parser.add_argument("--attachment", type=str, help="Optional attachment for the freight document")
parser.add_argument("--today", action="store_true", help="Set all dates to today")

args = parser.parse_args()

if args.client_secret:
    client_secret = args.client_secret
if args.env:
    env = args.env

env_map = {
    "partner": {
        'api': "https://partner.transfollow.com/api",
        'portal':"https://partner.transfollow.com/portal"
    },
    "acceptance": {
        'api': "https://acceptance.transfollow.com/api",
        'portal':"https://acceptance.transfollow.com/portal"
    },
    "test": {
        'api': "https://test.transfollow.com/api",
        'portal':"https://test.transfollow.com/portal"
    },
    "develop":  {
        'api': "http://localhost:8080/v1",
        'portal':"http://localhost:9091"
    },
}

class TransFollow:
    # Generic (POST) request handler
    def do_request(self, url, headers, data):
        try:
            r = requests.post(url, data=data, headers=headers)
            if r.status_code not in (200, 201):
                raise Exception("Unexpected HTTP status: %s\nURL: %s\n\nResponse body:\n%s" % (r.status_code, url, r.text))
            return r.text
        except requests.exceptions.RequestException as e:
            print e
            print e.read()

    # Authenticates a given username and password
    def login(self, user, password):
        url = "%s/oauth/token" % env_map[env]['api']
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": "Basic "+base64.b64encode(client_secret)
        }
        data = {
            "username": user, "password": password, "grant_type": "password", "scope": "transfollow"
        }
        return json.loads(
            self.do_request(url=url, data=data, headers=headers)
        )

    # Creates a new Freight Document
    def create_fd(self, token, user, json_data):
        url = "%s/freightdocuments" % env_map[env]['api']
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer "+token
        }

        if args.one_user:
            json_data["consignor"]["submittedAccountEmailAddress"] = user
            json_data["consignee"]["submittedAccountEmailAddress"] = user
            json_data["carrier"]["submittedAccountEmailAddress"] = user
            
        if args.attachment:
	    attachment = open(args.attachment).read()
	    json_data["attachments"] = [{
		"originalFileName": os.path.basename(args.attachment),
		"content": base64.b64encode(attachment),
		"sealed": False,
		"type": "GENERAL"
	    }]
	    
	if args.today:
	    today = datetime.date.today().isoformat()
	    json_data["agreedDateOfTakingOver"]=json_data["establishedDate"] = today
	    now = datetime.datetime.now().isoformat('T')
	    json_data["estimatedDateTimeOfDelivery"] = now
    	    earlier = (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat('T')
	    json_data["estimatedDateTimeOfTakingOver"] = earlier
	  
	      

        return json.loads(
            self.do_request(url=url, data=json.dumps(json_data), headers=headers)
        )

    # Creates a signing moment
    def sign_fd(self, token, fd_id, user):
        url = "%s/freightdocuments/%s/submitmyapproval" % (env_map[env]['api'], fd_id)
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer "+token
        }
        data = {
            "location": {
                "latitude": "34.00",
                "longitude": "33.00"
            },
            "place":"city name",
            "previousCommits": [],
            "action": "COLLECTION",
            "ownRole": "CARRIER",
            "secondsSinceCreation": 99,
            "declined": True
        }
        return json.loads(
            self.do_request(url=url, data=json.dumps(data), headers=headers)
        )

# Class to easily load all JSON as python hashes/arrays
class JsonLoader:
    def load_file(self, path):
        try:
            json_data = open(path).read()
            return json.loads(json_data)
        except ValueError as e:
            print "Ran into issue parsing %s: %s" % (path, e)
        except Exception as e:
            print "Unhandled exception: %s" % (e)

    def load(self, json_dir, json_file):
        json_files = []
        if json_dir:
            for path in os.listdir(json_dir):
                if path.endswith(".json"):
                    json_files.append(self.load_file(json_dir+path))
        elif json_file:
            json_files.append(self.load_file(args.json_file))

        return json_files

tf = TransFollow()
jl = JsonLoader()

json_files = jl.load(json_dir=args.json_dir, json_file=args.json_file)

if json_files:
    user = password = None
    if config.has_option("settings", "user"):
        user = config.get("settings", "user")
    if args.user:
        user = args.user
    if config.has_option("settings", "password"):
        password = config.get("settings", "password")
    if args.password:
        password = args.password

    login = tf.login(user, password)
    print "User '%s' is now authenticated" % user

    for json_data in json_files:
        fd = tf.create_fd(token=login["access_token"], user=user, json_data=json_data)
        fd_view_url = "%s/#home,viewFreightDocument&id=" % env_map[env]['portal']
        print "Created new FD: %s%s" % (fd_view_url, fd["freightDocumentId"])

        if args.sign_fd:
            sm = tf.sign_fd(token=login["access_token"], fd_id=fd["freightDocumentId"], user=user)
            print "Signed document: %s" % sm
elif not json_files and args.json_file:
    print "JSON file %s could not be loaded" % args.json_file
elif not json_files and args.json_dir:
    print "No JSON files could be found or loaded from %s" % args.json_dir
