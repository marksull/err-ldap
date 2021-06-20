err-ldap
=====

This is a package that works with err (http://errbot.io) to limit a bot command to a specific LDAP group or groups. In the following example the command ```this_is_a_command``` will only be executed if the user that issued the command belongs to the LDAP group ```group1``` or ```group2```.

```python
@ldap_verify(["group1", "group2"])
@botcmd
def this_is_a_command(self, msg, args):
    yield "This command was allowed after LDAP was checked"
```


## Status

This package is currently under development.


## Installation

```bash
git clone https://github.com/marksull/err-ldap.git
```

## Bot Configuration

To your errbot config.py file add the following:

```python
LDAP_URL = 'ldaps://server.domain'
LDAP_USERNAME = 'CN=<username>,OU=<ou>,OU=<ou>,DC=<domain>,DC=com'
LDAP_PASSWORD = 'xxxx'
LDAP_SEARCH_BASE = 'OU=<ou>,OU=<ou>,DC=<domain>,DC=com'
```

##  Usage

Each bot command that should only be accessible to a specific group should be decorated with ```@ldap_verify()```.

```@ldap_verify()``` accepts either a ```str``` if you only want to validate against a single group, else a ```list``` if the command should be made accessible to multiple groups.

In the example below, the err command ```tryme``` is decorated with the ```ldap_verify``` method. This method was initialised with a list that contains the LDAP group names of  ```group1``` and ```group2```.

When a user issues the command ```tryme``` the user ID will be checked to see if it is a member of ```group1``` OR ```group2```. If the user isn't found in any of the listed groups then a message will be displayed to the user, and the command ```tryme``` will NOT be actioned.

```python
from errbot import BotPlugin, botcmd
from errldap import ldap_verify

class Example(BotPlugin):

    @ldap_verify(["group1", "group2"])
    @botcmd 
    def tryme(self, msg, args): 
        yield "It *works* !"
```


### Custom User ID Determination

How the user ID is determined can be specific to installed backend or how the userid should be formatted to suit your specific LDAP directory could vary. To cater for these situations, a custom method can override the ```determine_user``` method. For example:

```python
    import errldap

    def custom_user_id(msg):
        return f"{msg.frm.userid}@.domain.com"

    errldap.determine_user = custom_user_id
```


### Custom LDAP Connection

If you want to override the LDAP connection sequence, override ```errldap.connect```. For example:

```python
    import ldap
    import errldap

    def custom_connect(bot):
            con = ldap.initialize(bot.bot_config.LDAP_URL)
            con.do_something_special()
            return con

    errldap.connect = custom_connect
```


### Custom LDAP Search

If you want to override the LDAP group search, override ```errldap.is_member```. For example:

```python
    
    import errldap

    def custom_is_member(connection, bot, user, group):
            if <is member>:
                return True
            else:
                return False

    errldap.is_member = custom_is_member
```


### Custom Fail Message

When the LDAP verify fails, you can provide a custom message by overriding ```errldap.fail_message```. For example:

```python
    import errldap

    def custom_fail_message(user, msg, groups):
            return "You shall not pass!"

    errldap.fail_message = custom_fail_message
```


## Contributing

Happy to accept Pull Requests
