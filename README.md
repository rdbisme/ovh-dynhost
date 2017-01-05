# ovh-dynhost
This script sets the DynHost service (that must be created before, check https://www.ovh.com/us/g2024.hosting_dynhost) with your current public IP that is retrieved from ipify.org API (default, can be overriden). 

## Usage
Give execution rights to the script
```
chmod +x ovh-dynhost
```

- Sets the `home.mydomain.com` host to your current public IP retrieved from (SSL) ipify.org using `myusername` and `mypassword` as credentials.
```
ovh-dynhost home.mydomain.com myusername mypassword
```
- Sets the `0.0.0.0` IP instead of the current public IP
```
ovh-dynhost --ip=0.0.0.0 home.mydomain.com myusername mypassword
```
- Use the (unencrypted, check the `http://` instead of `https://`) API from whatismyipaddress.com
```
ovh-dynhost --pub-ip-source=http://bot.whatismyipaddress.com home.mydomain.com myusername mypassword
```
- Same as first but logging also into `ovh.log` file
```
ovh-dynhost --log-file=ovh.log home.mydomain.com myusername mypassword
```
