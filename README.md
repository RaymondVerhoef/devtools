# devtools

Repository containing several tools for developers creating applications to integrate with the TransFollow.org platform.

## Installation

Checkout this repository to any machine that has python installed.

To be able to use this utility you will need two non-standard python libraries:
* requests
* requests[security]

It is recommended to use pip to install these depencencies, see:
https://pypi.python.org/pypi/pip

Commonly you would end up running these 3 commands:

```
> sudo easy_install pip
> sudo pip install requests
> sudo pip install requests[security]

```

## Configuration
Global configuration from the tools is read from the ~/.tfdevtools.ini file, which has the following format:

```
[settings]
# The environment the tools communicate with
env = acceptance|test|partner|develop
# The client-id & -secret used in oauth; see developer.transfollow.com for information on how to obtain one.
client_secret = id:secret
# Default user credentials for the create_* commands:
user = dummy@user.nl
password = password
```

All of these options can be overridden with their corresponding command line arguments, and should be provided that way if not entered in the configuration file.

## Help?!

If you have any questions or suggestions (or run into a bug) feel free to create an issue on GitHub. Any pull requests/patches are also very welcome.
