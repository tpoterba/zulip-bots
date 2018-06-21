import re
import requests
import sys

GIST_REGEX=r"""((?:(?:http|https)\://)?gist\.github\.com/[a-z\d-]+/[a-f\d]+)"""

MAX_LINE_LEN = 100
LINES_PER_FILE = 10

def encoding(enc):
    if enc.startswith('text'):
        return ''
    elif enc == 'application/x-python':
        return 'python'
    else:
        return None

class GistExpanderHandler(object):
    '''
    Expand GitHub gists.
    '''

    def usage(self):
        return '''Expand GitHub gists.'''

    def handle_message(self, message, bot_handler):
        gists = re.findall(GIST_REGEX, message['content'])
        if gists:
            reply = []
            for gist in set(gists):
                reply.append(f'Gist: {gist}')
                r = requests.get(f"https://api.github.com/gists/{gist.split('/')[-1]}")
                if r.status_code != 200:
                    reply.append(f'Error! HTTP status code {r.status_code}')
                    continue

                r = r.json()

                date, time = r['updated_at'].split('T')
                reply.append(f"Owned by {r['owner']['login']}, last updated at {time[:-1]} on {date}")
                file_word = 'file' if len(r['files']) == 1 else 'files'

                reply.append(f"{len(r['files'])} {file_word}.")

                for gist_file in r['files'].values():
                    reply.append(f"File `{gist_file['filename']}`:")
                    enc = encoding(gist_file['type'])
                    if enc is None:
                        reply.append(f"<not text: {gist_file['type']}>")
                    else:
                        contents = gist_file['content'].split('\n')
                        reply.append(f'```{enc}')
                        for line in contents[:LINES_PER_FILE]:
                            if len(line) > MAX_LINE_LEN:
                                reply.append(line[:MAX_LINE_LEN] + '...')
                            else:
                                reply.append(line)
                        reply.append('```')
                    reply.append('')

                reply.append('')

            bot_handler.send_reply(message, '\n'.join(reply).strip())

handler_class = GistExpanderHandler
