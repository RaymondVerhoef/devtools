#!/usr/bin/python
###
#
# Create User
#
###

import json, pprint, requests, argparse, os, base64, ConfigParser


pp = pprint.PrettyPrinter(indent=4)
parser = argparse.ArgumentParser(description="Creates a freight document on a given environment.")

parser.add_argument("--env", type=str, help="The target environment: test, acceptance or partner")
parser.add_argument("--user", type=str, help="The existing user email address used to create the FD")
parser.add_argument("--password", type=str, help="The existing user password used to create the FD")
parser.add_argument("--name", type=str, help="Optional name for the user; the email-address is used if not supplied")
args = parser.parse_args()

config = ConfigParser.RawConfigParser({'env': 'test'})
config.add_section("settings")
config.read([os.path.expanduser('~/.tfdevtools.ini')])

env = config.get("settings", "env")
if args.env:
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

    # Creates a new Freight Document
    def create_user(self, email, name, password):
        url = "%s/test/accounts/users" % env_map[env]
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": "Basic dGVzdC1jbGllbnQ6ZVJnUmgiLzJfUg=="
        }

        json_data = {
            "password": password,
            "phoneNumber": "0306997020",
            "email": email,
            "name": name,
            "acceptTermsAndConditions": "true"
        }

        return json.loads(
            self.do_request(url=url, data=json.dumps(json_data), headers=headers)
        )


tf = TransFollow()

user = tf.create_user(name=args.name if args.name else args.user, email=args.user, password=args.password)
pprint.pprint(user)
