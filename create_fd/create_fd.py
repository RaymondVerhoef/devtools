###
# 
# Create Freight document helper
#
# See README.md in this directory for installation instructions.
#
###

import json, pprint, requests, argparse, os, base64


pp = pprint.PrettyPrinter(indent=4)
parser = argparse.ArgumentParser(description="Creates a freight document on a given environment.")

# Client secret - See developer.transfollow.com for information on how to obtain one.
client_secret = "client_secret_goes_here"

# There can only be one JSON source, a single file or a group of files
json_source = parser.add_mutually_exclusive_group(required=True)
json_source.add_argument("--json_file", type=str, help="The JSON file to use for FD posting")
json_source.add_argument("--json_dir", type=str, help="A directory containing JSON freight document files")

parser.add_argument("--env", type=str, default="test", help="The target environment: test, acceptance or partner")
parser.add_argument("--client_secret", type=str, help="The client secret, used to authenticate with the API service")
parser.add_argument("--user", type=str, help="The existing user email address used to create the FD")
parser.add_argument("--password", type=str, help="The existing user password used to create the FD")
parser.add_argument("--one_user", action="store_true", help="Sets all the role email addresses to the user used for authentication, overriding the JSON addresses")
parser.add_argument("--sign_fd", action="store_true", help="Signs the freight document. Note that the user needs to have signing permission. Generally this means the carrier.")
args = parser.parse_args()

if args.client_secret:
    client_secret = args.client_secret
env = args.env
env_map = {
    "partner": "https://partner.transfollow.com/api",
    "acceptance": "https://acceptance.transfollow.com/api",
    "test": "https://test.transfollow.com/api",
    "develop": "http://localhost:8080/v1"
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
        url = "%s/oauth/token" % env_map[env]
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
        url = "%s/freightdocuments" % env_map[env]
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer "+token
        }

        if args.one_user:
            json_data["consignor"]["submittedAccountEmailAddress"] = user
            json_data["consignee"]["submittedAccountEmailAddress"] = user
            json_data["carrier"]["submittedAccountEmailAddress"] = user

        return json.loads(
            self.do_request(url=url, data=json.dumps(json_data), headers=headers)
        )

    # Creates a signing moment
    def sign_fd(self, token, fd_id, user):
        url = "%s/freightdocuments/%s/submitmyapproval" % (env_map[env], fd_id)
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
            "ownRole": "CONSIGNOR",
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
    login = tf.login(args.user, args.password)
    print "User '%s' is now authenticated" % args.user

    for json_data in json_files:
        fd = tf.create_fd(token=login["access_token"], user=args.user, json_data=json_data)
        fd_view_url = "%s/portal/#home,viewFreightDocument&id=" % env_map[env]
        print "Created new FD: %s%s" % (fd_view_url, fd["freightDocumentId"])

        if args.sign_fd:
            sm = tf.sign_fd(token=login["access_token"], fd_id=fd["freightDocumentId"], user=args.user)
            print "Signed document: %s" % sm
elif not json_files and args.json_file:
    print "JSON file %s could not be loaded" % args.json_file
elif not json_files and args.json_dir:
    print "No JSON files could be found or loaded from %s" % args.json_dir
