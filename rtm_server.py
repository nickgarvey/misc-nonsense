#!/usr/bin/env python3
"""
Turns out they have a desktop app. Definition use it instead of this.
https://www.rememberthemilk.com/services/mac/

Overview:
This is a Python server that will listen on PORT and will create a
RememberTheMilk task when sent requests to task_add.

I made this because I wanted a quick way to make RTM tasks from Chrome.

To make requests:
Add a new search engine to Chrome with http://localhost:8028/task_add?task=%s
as the URL and rtm as the action. Then do rtm<tab>your task here

To auth:
Add your API key & secret to a config.ini then call it with task=frob to get
a frob. Then call it with task=auth to get the auth token

Example config.ini:
key=mykey
secret=mysecret
frob=frobfromcallingtaskfrob
auth=authfromcallingtaskauth
"""


# watchman -- trigger . runserver -- bash -c "pkill -f 'python.*rtm_server.py'"
# while true; do ./rtm_server.py; sleep 1 ; done

import hashlib
import http.server
import json
import re
import urllib.parse
import urllib.request

PORT = 8028


class RememberTheMilkServer(http.server.HTTPServer):
    def __init__(self):
        super().__init__(('', PORT), RememberTheMilkHandler)
        self.config = self.load_config()

    def load_config(self):
        with open('./config.ini') as config:
            config_dict = {}
            for line in config:
                match = re.match('(\w+)=(.*)', line)
                if match:
                    config_dict[match.group(1)] = match.group(2)
            return config_dict


class RememberTheMilkHandler(http.server.BaseHTTPRequestHandler):

    def do_redirect(self, url):
        self.send_response(303)
        self.send_header(
            'Location',
            url,
        )
        self.end_headers()

    def do_content(self, content):
        self.send_response(200)
        to_send = content.encode('utf-8')
        self.send_header('Content-Length', len(to_send))
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(to_send)

    def do_GET(self):
        print(self.requestline)
        _, url, _ = self.requestline.split()

        match = re.match(r'/task_add\?task=(.*)', url)
        task = urllib.parse.unquote_plus(match.group(1)) if match else False
        if not task:
            self.do_redirect('https://www.rememberthemilk.com/')
            return
        elif task == 'frob':
            query_str = self.build_query_str({'perms': 'write'})
            frob_url = (
                'https://api.rememberthemilk.com/services/auth/'
                f'?{query_str}'
            )
            self.do_redirect(frob_url)
            return
        elif task == 'auth':
            self.do_content(self.get_auth())
            return

        timeline = json.loads(self.do_rest({
            'method': 'rtm.timelines.create',
        }))['rsp']['timeline']

        task_add = json.loads(self.do_rest({
            'method': 'rtm.tasks.add',
            'timeline': timeline,
            'name': task,
            'parse': '1',
        }))['rsp']

        list_id = task_add['list']['id']
        task_id = task_add['list']['taskseries'][0]['task'][0]['id']

        self.do_redirect(
            f'https://www.rememberthemilk.com/app/#list/{list_id}/{task_id}'
        )

    def get_auth(self):
        return self.do_rest({
            'method': 'rtm.auth.getToken',
            'frob': self.config('frob'),
        })

    def do_rest(self, params):
        query_str = self.build_query_str(params)
        url = (
            'https://api.rememberthemilk.com/services/rest/'
            f'?{query_str}'
        )
        print(url)
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')

    def calc_sig(self, param_dict):
        to_md5 = (
            self.config('secret') +
            ''.join(k + v for k, v in sorted(param_dict.items()))
        )
        m = hashlib.md5()
        m.update(to_md5.encode('utf-8'))
        return m.hexdigest()

    def config(self, key):
        return self.server.config.get(key, '')

    def build_query_str(self, params):
        new_params = {
            'api_key': self.config('key'),
            'auth_token': self.config('auth'),
            'format': 'json',
        }
        new_params.update(params)
        new_params['api_sig'] = self.calc_sig(new_params)
        return urllib.parse.urlencode(new_params)


if __name__ == "__main__":
    print()
    print('started')
    RememberTheMilkServer().serve_forever()
