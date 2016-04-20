from PIL import Image, ImageOps, ImageFont, ImageDraw
from io import BytesIO
import textwrap
import requests
import random
import yaml
import json
import os

config = None
with open(os.path.dirname(os.path.realpath(__file__)) + '/config.yaml') as file:
    try:
        config = yaml.load(file)
    except yaml.YAMLError as e:
        print('Could not load config:', str(e))
        exit(1)


def build_image(url, text):
    """
    Downloads the image and creates an image with the given text and saves it in the img folder.
    """
    response = requests.get(url, headers={'User-Agent': config['settings']['user-agent']})

    img = Image.open(BytesIO(response.content))
    img = ImageOps.fit(img, (config['settings']['img-width'], config['settings']['img-height']), Image.ANTIALIAS)
    draw = ImageDraw.Draw(img)
    x, y = img.size
    # The font file should be in the same directory as the script.
    # On Windows the file may also be located in the Windows fonts/ directory.
    font = ImageFont.truetype(os.path.dirname(os.path.realpath(__file__)) +
                              '/{}.ttf'.format(config['settings']['font']),
                              config['settings']['font-size'])

    # Starting height and padding between lines
    cur_h, pad = 50, 10
    wrap = textwrap.wrap(text, width=config['settings']['chars-line'])
    for i, line in enumerate(wrap):
        # Center the text
        w, h = draw.textsize(line, font)
        cur_h += h + pad

        # Draw the text four times with a dark color to create a dark outline
        draw.text(((x - 1 - w) / 2, cur_h - 1), line, font=font, fill=(0, 0, 0))
        draw.text(((x + 1 - w) / 2, cur_h - 1), line, font=font, fill=(0, 0, 0))
        draw.text(((x - 1 - w) / 2, cur_h + 1), line, font=font, fill=(0, 0, 0))
        draw.text(((x + 1 - w) / 2, cur_h + 1), line, font=font, fill=(0, 0, 0))
        draw.text(((x - w) / 2, cur_h), line, font=font, fill=(255, 255, 255))

    d = os.path.dirname(os.path.realpath(__file__)) + '/img/'
    if not os.path.exists(d):
        os.makedirs(d)

    # Overwrite the oldest image if the maximum amount of images has been reached
    files = sorted([d + name for name in os.listdir(d) if os.path.isfile(d + name)], key=os.path.getmtime)
    num = len(files)
    if num >= config['settings']['count']:
        os.remove(files[0])
        img.save(files[0])
        del config['current']['text'][0]
        del config['current']['img'][0]
    else:
        img.save(d + str(num) + '.png')

    # Add the used url and text to the config to stop duplicates from showing up
    config['current']['text'].append(text)
    config['current']['img'].append(url if 'imgur' not in url else url[:-4])


def get_comment(subreddit, params):
    """
    Get a random comment from a random submission in the given subreddit.
    """
    num = random.randint(params.get('min', 0), params.get('max', 10))
    response = requests.get('https://www.reddit.com/r/{}/{}.json?t={}'
                            .format(subreddit, params['sort'], params['time']),
                            headers={'User-Agent': config['settings']['user-agent']})
    r = json.loads(response.text)

    url = 'https://www.reddit.com/{}.json'.format(r['data']['children'][num]['data']['permalink'])
    response = requests.get(url, headers={'User-Agent': config['settings']['user-agent']})
    r = json.loads(response.text)

    r = [s for s in r[1]['data']['children'][params.get('min', 0):params.get('max', 1000)]
         if not s['data']['body'] in config['current']['text']]

    if r:
        comment = random.choice(r)['data']['body']
        return (comment[:250] + '...') if len(comment) > 250 else comment


def get_title(subreddit, params):
    """
    Get the title of a random submission in the given subreddit.
    """
    response = requests.get('https://www.reddit.com/r/{}/{}.json?t={}'
                            .format(subreddit, params['sort'], params['time']),
                            headers={'User-Agent': config['settings']['user-agent']})
    r = json.loads(response.text)

    if not params.get('stickies', False):
        r = [s for s in r['data']['children'][params.get('min', 0):params.get('max', 10)]
             if not s['data']['stickied'] and not s['data']['title'] in config['current']['text']]
    else:
        r = [s for s in r['data']['children'][params.get('min', 0):params.get('max', 10)]
             if not s['data']['title'] in config['current']['text']]

    if r:
        return random.choice(r)['data']['title']


def get_image(subreddit, params):
    """
    Get the url of an image in the given subreddit.
    """
    response = requests.get('https://www.reddit.com/r/{}/{}.json?t={}'
                            .format(subreddit, params['sort'], params['time']),
                            headers={'User-Agent': config['settings']['user-agent']})
    r = json.loads(response.text)

    if not params.get('stickies', False):
        r = [s for s in r['data']['children'][params.get('min', 0):params.get('max', 10)]
             if not s['data']['stickied'] and s['data']['url'] not in config['current']['img'] and
             ('imgur' in s['data']['url'] or any(map(s['data']['url'].endswith, config['settings']['formats'])))]
    else:
        r = [s for s in r['data']['children'][params.get('min', 0):params.get('max', 10)]
             if s['data']['url'] not in config['current']['img'] and
             ('imgur' in s['data']['url'] or any(map(s['data']['url'].endswith, config['settings']['formats'])))]

    if r:
        return random.choice(r)['data']['url']


def weighted_choice(choices):
    """
    Weighted choice of an option from a list of (choice, weight) tuples.
    """
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    for c, w in choices:
        r -= w
        if r <= 0:
            return c


def save_config():
    """
    Save the config file.
    """
    with open(os.path.dirname(os.path.realpath(__file__)) + '/config.yaml', 'w+') as cfg:
        cfg.write(yaml.dump(config, default_flow_style=False))


def main():
    """
    Try to get an image and text and save that image.
    """
    try:
        sub = weighted_choice([(c, config['images'][c].get('weight', 10)) for c in config['images']])
        url = get_image(sub, config['images'][sub])

        sub = weighted_choice([(c, config['text'][c].get('weight', 10)) for c in config['text']])
        if config['text'][sub]['title']:
            text = get_title(sub, config['text'][sub])
        else:
            text = get_comment(sub, config['text'][sub])

        if url is None or text is None:
            print('Could not get an image or text, there might be no unused images or texts left.')
            return False

        if 'imgur' in url:
            build_image(url + '.jpg', text)
        else:
            build_image(url, text)

        return True
    except Exception as exc:
        print('Failed when building image:', str(exc))
        return False


if __name__ == '__main__':
    if config:
        n = 0
        while (not main()) and n <= config['settings']['retries']:
            n += 1
        save_config()
    else:
        print('No config loaded.')
