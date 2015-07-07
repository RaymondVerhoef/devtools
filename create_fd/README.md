# create_fd.py

Utility to easily create any number of freight documents based on given JSON datasets.

## Installation

Checkout this repository to any machine that has python installed.

To be able to use this utility you will need two non-standard python libraries:
* requests
* requests[security]

It is recommended to use pip to install these depencencies, see:
https://pypi.python.org/pypi/pip

Optional:
You can set a static client_secret in the python file by replacing the following variables' value:
```
client_secret = "client_secret_goes_here"
```
You can also pass this value as a command line option.

## Usage

For usage view 

```
> python create_fd.py -h
```
