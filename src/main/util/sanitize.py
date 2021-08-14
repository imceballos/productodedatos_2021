import re
from html import escape as escap


def escape():
    pass #TODO

def stripWhitespace(string):
    a = re.compile(r'\s+')
    result = a.sub(' ', string)
    return result

def stripImages(string):
    im1 = re.compile(r'(<a[^>]*>)(<img[^>]+alt=")([^"]*)("[^>]*>)(<\/a>)')
    im2 = re.compile(r'(<img[^>]+alt=")([^"]*)("[^>]*>)')
    im3 = re.compile(r'<img[^>]*>')

    string = im1.sub(r'\1\3\5<br />', string) 
    string = im2.sub(r'\2<br />', string)  
    string = im3.sub(r'', string)  
    return string


def stripScripts(string):
    sc1 = re.compile(r'(<link[^>]+rel="[^"]*stylesheet"[^>]*>|<img[^>]*>|style="[^"]*")|<script[^>]*>.*?<\/script>|<style[^>]*>.*?<\/style>|<!--.*?-->')
    string = sc1.sub(r'', string)
    return string


def stripAll(string):
    string = stripWhitespace(string)
    string = stripImages(string)
    string = stripScripts(string)
    return string


def stripTags(string, *argv):
    for arg in argv:
        tg1 = re.compile(r'<'+ arg + r'[^>]*>')
        tg2 = re.compile(r'<\/'+ arg + r'[^>]*>')
        string = tg1.sub('', string)
        string = tg2.sub('', string)
    return string

def htmlentities(data, charset, quotes = 'ENT_QUOTES'):
    quotes_values = {
                        'ENT_QUOTES': True,
                        'ENT_COMPAT': False,
                        'ENT_NOQUOTES': False
                    }
    quote = quotes_values[quotes]
    if charset and charset !='utf-8':
        data = data.decode(charset, 'ignore')
    if quote:
        data = escap(data, quote)
    if quotes == 'ENT_COMPAT':
        data = data.replace('"', "&quot;")
    return data


def html(string, **kwargs):
    defaultCharset = None
    if not defaultCharset:
        defaultCharset = 'utf-8'
    default = {
                'remove' : False,
                'charset': defaultCharset,
                'quotes': 'ENT_QUOTES',
                'double': True
                }
    options = {**default, **kwargs}
    if options['remove']:
        string = re.sub(r'<[^>]*?>', '', string)
    return htmlentities(string, options['charset'], options['quotes'])


def clean(data, options = {}):
    if not data:
        return data
    if isinstance(options, str):
        options = {'connection': options}
    elif not isinstance(options, dict):
        options = {}

    default_options = {
        'connection' : 'default',
        'odd_spaces' : True,
        'remove_html': False,
        'encode': True,
        'dollar': True,
        'carriage': True,
        'unicode': True,
        'escape': True,
        'backslash': True
                            }
    options = {**default_options, **options}

    if isinstance(data, list):
        for val in range(len(data)):
            data[val] = clean(val, options)
        return data

    elif isinstance(data, dict):
        for key, value in data.items():
            data[key] = clean(value, options)
        return data
    else:
        if options['odd_spaces']:
            data = data.replace(chr(0xCA), "")
        if options['encode']:
            data = html(data, remove = options['remove_html'])
        if options['dollar']:
            data = data.replace("\\$", "$")
        if options['carriage']:
            data = data.replace("\r", "")
        if options['unicode']:
            uni = re.compile(r'&amp;#([0-9]+);')
            data = uni.sub(r'&#\\1;', data)
        if options['backslash']:
            bac = re.compile(r'\\(?!&amp;#|\?#)')
            data = bac.sub(r'\\', data)
        return data
