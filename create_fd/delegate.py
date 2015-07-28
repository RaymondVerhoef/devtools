###
# 
# Delegation helper
#
###

import json, pprint, requests, argparse, os, base64


pp = pprint.PrettyPrinter(indent=4)
parser = argparse.ArgumentParser(description="Creates a freight document on a given environment.")

# Client secret - See developer.transfollow.com for information on how to obtain one.
client_secret = "client_secret_goes_here"

parser.add_argument("--env", type=str, default="test", help="The target environment: test, acceptance or partner")
parser.add_argument("--client_secret", type=str, help="The client secret, used to authenticate with the API service")
parser.add_argument("--user", type=str, help="The existing user email address used to create the FD")
parser.add_argument("--password", type=str, help="The existing user password used to create the FD")
parser.add_argument("--role", type=str, help="The role you wish to delegate.")
parser.add_argument("--delegatee_email", type=str, help="The target email address.")
parser.add_argument("--fd_id", type=str, help="The target freight document id.")
args = parser.parse_args()

if args.client_secret:
    client_secret = args.client_secret
env = args.env
env_map = {
    "partner": "https://partner.transfollow.com/api",
    "acceptance": "https://acceptance.transfollow.com/api",
    "test": "https://test.transfollow.com/api",
    "dev": "http://localhost:8080/v1"
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
    def delegate_fd(self, token, fd, role, emailAddressOfDelegatee):
        url = "%s/freightdocuments/%s/delegate" % (env_map[env], fd)
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer "+token
        }

        body = {
            "role": role,
            "emailAddressOfDelegatee": emailAddressOfDelegatee
        }
        return json.loads(
            self.do_request(url=url, data=json.dumps(body), headers=headers)
        )

tf = TransFollow()

login = tf.login(args.user, args.password)
print "User '%s' is now authenticated" % args.user

sm = tf.delegate_fd(token=login["access_token"], fd=args.fd_id, role=args.role, emailAddressOfDelegatee=args.delegatee_email)
print "Delegated document: %s" % sm
