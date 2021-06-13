import ldap
import functools


def determine_user(msg):
    """
    Determine the used id used for the LDAP searches

    Override this method if you want to custom build the used ID

    Args:
        msg (errbot.backends.base.Message): The message from the bot that triggered the LDAP lookup

    Returns:
        str: The user ID that will be used to search LDAP
    """
    return user_email(msg)


def user_email(msg):
    """
    Use the email from the msg as the user search criteria

    Args:
        msg (errbot.backends.base.Message): The message from the bot that triggered the LDAP lookup

    Returns:
        str: The user ID that will be used to search LDAP

    Raises:
        ValueError: When user from email address can not be determined
    """

    # This should cater for Webex backend that contains a list of emails for user
    if hasattr(msg.frm, "emails"):
        email = (
            msg.frm.emails[0] if isinstance(msg.frm.emails, list) else msg.frm.emails
        )
        return email.split("@")[0]

    # This should cater for other backends like slack
    if hasattr(msg.frm, "email"):
        return msg.frm.email.split("@")[0]

    # And just in case..don't want to return an empty user that could potentially match
    raise ValueError("Cannot determine user ID from email address")


def user_id(msg):
    """
    Use the userid from the msg as the user search criteria

    Args:
        msg (errbot.backends.base.Message): The message from the bot that triggered the LDAP lookup

    Returns:
        str: The user ID that will be used to search LDAP
    """
    if hasattr(msg.frm, "userid"):
        return msg.frm.userid

    raise ValueError("Cannot determine user ID from msg.userid")


def connect(bot):
    """
    Initialize the LDAP connection

    Override this method if you want a custom initialisation

    Args:
        bot (Errbot): The errbot instance

    Returns:
        ldap.functions.LDAPObject: An initialised LDAP Object
    """
    con = ldap.initialize(bot.bot_config.LDAP_URL)
    con.simple_bind_s(bot.bot_config.LDAP_USERNAME, bot.bot_config.LDAP_PASSWORD)
    return con


def is_member(connection, bot, user, group):
    """
    Determine if the username provided is a member of the group

    Override this method if you want to handle your search in a specific way

    Args:
        connection: (ldap.functions.LDAPObject): The session object for the LDAP connection
        bot (Errbot): The errbot instance
        user (str): The user that is to be search for in LDAP
        group (str): The LDAP search base

    Returns:
        bool: True if the user is a member, else False
    """
    data = connection.search_s(
        bot.bot_config.LDAP_SEARCH_BASE, ldap.SCOPE_SUBTREE, f"(CN={group})",
    )

    # Could not find the group
    if not data:
        return False

    return user in [
        m.decode("utf-8").split(",")[0].split("=")[1] for m in data[0][1]["member"]
    ]


def fail_message(user, msg, groups):
    """
    The message to be displayed to the user when they fail the LDAP validation

    Override this method if you want your own custom message

    Args:
        user (str): The user ID that was used for the LDAP search
        msg (errbot.backends.base.Message): The message from the bot that triggered the LDAP lookup
        groups (list): The list og group(s) in which the user was searched

    Returns:
        str: The formatted failure message

    """
    return f"Sorry, ```{user}``` is not permitted to execute the command ```{msg}``` as you are not a member of ```{','.join(groups)}```"


def ldap_verify(group):
    """"
    Decorator to limit commands to a specific LDAP group or groups. The username will be derived from the person whom
    issued the webex teams chat.

    Notes for using this decorator:
        - Any method using this decorator MUST use YIELD in lieu of RETURN for all bot directed output
        - The decorator must be the outermost decorator (on top of all other decorators) to ensure the ldap
          check is performed prior to the bot command being issued
        - If more than one group is to be validated, then a list of groups should be provided. The first
          occurrence of membership for any of the groups, the user will be considered verified

    Args:
        group (str|list): The LDAP group(s) to which this command should be restricted
    """

    def decorator(func):
        @functools.wraps(func)
        def func_wrapper(self, msg, *args, **kwargs):

            connection = connect(self)
            user = determine_user(msg)
            groups = group if isinstance(group, list) else [group]

            for search_group in groups:
                if is_member(
                    connection=connection, bot=self, user=user, group=search_group
                ):
                    break
            else:
                yield fail_message(user=user, msg=msg, groups=groups)
                return

            for response in func(self, msg, *args, **kwargs):
                yield response

        return func_wrapper

    return decorator
