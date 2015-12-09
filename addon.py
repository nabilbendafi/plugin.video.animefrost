import os
import sys

import xbmcswift2
from xbmcswift2 import xbmcgui as xbmcgui
from fileinput import filename

__addon_name__ = 'Anime Frost'
__addon_id__ = 'plugin.video.animefrost'

plugin = xbmcswift2.Plugin(__addon_name__, __addon_id__, __file__)
addon = plugin.addon

if xbmcswift2.CLI_MODE:
    __addon_path__ = os.getcwd()
else:
    __addon_path__ = addon.getAddonInfo('path')

# append lib directory
sys.path.append(os.path.join(__addon_path__, 'resources', 'lib'))
from animefrost import API as animefrost
api = animefrost()


@plugin.route('/')
def index():
    """Display plugin main menu items."""
    entries = {'A-Z': 'get_all',
               'Categories': 'get_categories',
               'FAQ': 'show_faq'}

    items = [{'label': entry,
              'path': plugin.url_for(entries[entry]),
              'is_playable': False
              } for entry in entries]

    return plugin.finish(items)


@plugin.route('/all/')
def get_all():
    """Display the list of all available animes."""
    items = api.get_all()

    items = [{'label': item['label'],
              'path': plugin.url_for('get_anime',
                                     anime=item['path']),
              'thumbnail': item['thumbnail'],
              'is_playable': False
              } for item in items]

    return items


@plugin.cached_route('/categories/')
def get_categories():
    """Display the list of categories."""
    items = api.get_categories()
    print(items)

    items = [{'label': item['label'],
              'path': plugin.url_for('get_category',
                                     category=item['path']),
              'is_playable': False
              } for item in items]

    return items


@plugin.cached_route('/category/<category>')
def get_category(category):
    """
    Display the list of anime for the requested category.

    :param category: category name.
    """
    items = api.get_category(page=1, category=category)

    items = [{'label': item['label'],
              'path': plugin.url_for('get_anime',
                                     anime=item['path']),
              'thumbnail': item['thumbnail'],
              'is_playable': False
              } for item in items]

    return items


@plugin.cached_route('/anime/<anime>')
def get_anime(anime):
    """
    Display the list of episodes for the requested anime.

    :param anime: anime name.
    """
    items = api.get_anime(anime=anime)

    items = [{'label': item['label'],
              'path': plugin.url_for('get_episode',
                                     anime=anime,
                                     episode=item['episode']),
              'is_playable': False
              } for index, item in enumerate(items)]

    return items


@plugin.route('/anime/<anime>/episode/<episode>')
def get_episode(anime, episode='1'):
    """Display the video for the requested anime and episode.

    :param anime:   anime name.
    :param episode: episode number.
    """
    episode = api.get_episode(anime, episode)

    item = {'label': anime,
            'path': plugin.url_for('play',
                                   url=episode),
            'is_playable': True}

    return [item]


@plugin.route('/search/')
def video_search():
    """Display the provided video."""

    search_string = plugin.keyboard()
    if search_string:
        plugin.log.debug('video_search gots a string: "%s"' % search_string)
        url = plugin.url_for('video_search_result',
                             search_string=search_string)
        # immediatly call video_search_result function
        plugin.redirect(url)


@plugin.route('/search/<search_string>/')
def video_search_result(search_string):
    """Display the requested anime.

    :param search_string: anime to look for.
    """
    items = api.search(search_string)

    if not items:
        msg = 'Sorry, no match found for: ' % search_string
        plugin.log.debug(msg)
        dialog = Dialog()
        dialog.notification(__addon_name__, msg)

    items = [{'label': item['label'],
              'path': plugin.url_for('get_anime',
                                     anime=item['url']),
              'thumbnail': item['thumbnail']
              } for item in items]

    return items


@plugin.route('/play/<url>')
def play(url):
    """Play the video.

    :param url: playable video URL
    """
    plugin.log.info('Playing url: %s' % url)
    return plugin.set_resolved_url(url)


@plugin.route('/faq/')
def show_faq():
    """Simply show a popup window, with some information."""
    dialog = xbmcgui.Dialog()
    filename = os.path.join(__addon_path__, 'faq')
    try:
        faq = open(filename)
        dialog.ok("FAQ", faq.read())
    except IOError:
        pass
    finally:
        faq.close()


if __name__ == '__main__':
    try:
        remote_debugger = addon.getSetting('remote_debugger')
        # default false
        remote_debugger_host = addon.getSetting('remote_debugger_host')
        # default '127.0.0.1'
        remote_debugger_port = addon.getSetting('remote_debugger_port')
        # default 5678

        # append pydev remote debugger
        if remote_debugger == 'true':
            import pydevd
            # stdoutToServer and stderrToServer redirect stdout and stderr
            # to eclipse console
            pydevd.settrace(remote_debugger_host, port=remote_debugger_port,
                            stdoutToServer=True, stderrToServer=True)
    except ImportError:
        plugin.log.error("Error: make sure pydevd is installed !")
        sys.exit(1)
    except:
        pass

    # Rock'n'Roll
    try:
        plugin.run()
    except Exception, e:
        plugin.notify(msg=e)
