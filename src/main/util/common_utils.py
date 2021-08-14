import locale
import re


def number_format(num, places=0):
    locale.setlocale(locale.LC_NUMERIC, "")
    return locale.format("%.*f", (places, num), True)


def isset(variable):
    return variable in locals() or variable in globals()


def empty(variable):
    if not variable:
        return True
    return False


def recursive_trim(data):
    if isinstance(data, dict):
        for d in data:
            d = recursive_trim(d)
        return data

    return data.strip()


def check_email_address(email):
    # First, we check that there's one @ symbol,
    # and that the lengths are right.
    search = re.search("^[^@]{1,64}@[^@]{1,255}$", email)

    if not search:
        return False

    email_array = email.split("@")
    local_array = email_array[0].split(".")

    for part in local_array:
        search = re.search(
            r'^(([A-Za-z0-9!#$%&\'*+/=?^_`{|}~-][A-Za-z0-9!#$%&\'*+/=?^_`{|}~\.-]{0,63})|("[^(\\|")]{0,62}"))$',
            part,
        )
        if not search:
            return False

    # Check if domain is IP. If not,
    # it should be valid domain name
    search = re.search(r"^\[?[0-9\.]+\]?$", email_array[1])
    if not search:
        domain_array = email_array[1].split(".")
        if len(domain_array) < 2:
            return False

        for part in domain_array:
            search = re.search(
                r"^(([A-Za-z0-9][A-Za-z0-9-]{0,61}[A-Za-z0-9])|([A-Za-z0-9]+))$", part
            )
            if not search:
                return False

    return True


def str_split(string, split_length=1):
    return filter(None, re.split("(.{1,%d})" % split_length, string))


def substr(string, start, length=None):
    if start < 0:
        start = start + len(string)
    if not length:
        return string[start:]
    elif length > 0:
        return string[start : start + length]
    else:
        return string[start:length]


def datetime_to_str(dictionary, type_item="dict"):
    if type_item == "list":
        for item_list in dictionary:
            for item in item_list:
                if type(item_list[item]).__name__ == "datetime":
                    item_list[item] = str(item_list[item])
    else:
        for item in dictionary:
            if type(dictionary[item]).__name__ == "datetime":
                dictionary[item] = str(dictionary[item])

    return dictionary


"""Data Sanitization."""
"""Removal of alphanumeric characters, SQL-safe slash-added strings,"""
"""HTML-friendly strings, and all of the above on arrays."""


def paranoid(text, allowed):
    allow = ""
    if len(allowed) > 0:
        for char in allowed:
            allow += char
    cleaned = {}
    if isinstance(text, list):
        for key in text:
            cleaned[key] = re.sub("/[^{allow}a-zA-Z0-9]/", "", key)
    else:
        cleaned = re.sub("/[^{allow}a-zA-Z0-9]/", "", str(text))
    return cleaned


def convertRowProxy(data, type_item="dict"):
    d, a = {}, []
    for rowproxy in data:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)

    return d if type_item == "dict" else a


def plugin_split(name, dot_append=False, plugin=None):
    if "." in name:
        parts = name.split(".", 2)
        if dot_append:
            parts[0] = "."
        return parts
    return [plugin, name]
