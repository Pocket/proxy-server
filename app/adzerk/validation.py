import re


def validate_decision(decision):
    validate_image_url(decision['contents'][0]['data']['ctFullimagepath'])
    return True


def validate_image_url(url):
    if re.match(r'https://(\w+\.)?zkcdn\.net/', url):
        return True
    else:
        raise Exception("Invalid AdZerk image url: {0}".format(url))
