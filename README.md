# devtools
Repository containing several tools for developers creating applications to integrate with the TransFollow.org platform.

## Configuration
Global configuration from the tools is read from the ~/.tfdevtools.ini file, which has the following format:

'''
[settings]
# The environment the tools communicate with
env = acceptance|test|partner|develop
# The client-id & -secret used in oauth; see developer.transfollow.com for information on how to obtain one.
client_secret = id:secret
# Default user credentials for the create_* commands:
user = dummy@user.nl
password = password
'''

All of these options can be overridden with their corresponding command line arguments, and should be provided that way if not entered in the configuration file.

## Help?!

If you have any questions or suggestions (or run into a bug) feel free to create an issue on GitHub. Any pull requests/patches are also very welcome.
