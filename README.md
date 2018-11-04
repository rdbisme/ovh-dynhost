# ovh-dynhost
This script sets the DynHost service (that must be created before, check https://docs.ovh.com/gb/en/domains/hosting_dynhost/) with your current public IP that is retrieved from ipify.org API (default, can be overriden). 

## Installation
Install the script using pip (I strongly suggest to use a virtualenv)

`pip install .`

(The script will be now available in the `PATH`. Reactivate the virtualenv if necessary)

PS: The script is also available directly on PyPI.

`pip install ovh_dynhost`

## Usage

- Sets the `home.mydomain.com` host to your current public IP retrieved from (SSL) [ipify.org](https://www.ipify.org) using `myusername` and `mypassword` as credentials.
```
ovh-dynhost home.mydomain.com myusername mypassword
```
- Sets the `0.0.0.0` IP instead of the current public IP
```
ovh-dynhost --ip=0.0.0.0 home.mydomain.com myusername mypassword
```
- Use the (unencrypted, check the `http://` instead of `https://`) API from [whatismyipaddress.com](http://www.whatismyipaddress.com)
```
ovh-dynhost --pub-ip-source=http://bot.whatismyipaddress.com home.mydomain.com myusername mypassword
```
- Same as first but logging also into `ovh.log` file
```
ovh-dynhost --log-file=ovh.log home.mydomain.com myusername mypassword
```

If your prefer to not show up your username or password in the shell, you can provide a separate JSON configuration file. By default the script will lookup into `$HOME/.ovh-dyndns.conf`, but you can also provide a custom configuration file

```
ovh-dynhost home.mydomain.com --conf-file=/etc/ovh-dyndns/config.json
```
