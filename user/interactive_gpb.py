#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""
Talk with a model using a web UI.
"""


from http.server import BaseHTTPRequestHandler, HTTPServer
from parlai.scripts.interactive import setup_args
from parlai.core.agents import create_agent
from parlai.core.worlds import create_task
from typing import Dict, Any
from parlai.scripts.script import ParlaiScript
import parlai.utils.logging as logging

from user.weather import weather
import json
from collections import OrderedDict
import time
import os.path
from geotext import GeoText

file_name = "user/log.csv" #"../../../../log.log"
global f, n
n = 0
flag = False

HOST_NAME = 'localhost'
PORT = 8080

SHARED: Dict[Any, Any] = {}
STYLE_SHEET = "https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.4/css/bulma.css"
FONT_AWESOME = "https://use.fontawesome.com/releases/v5.3.1/js/all.js"
WEB_HTML = """
<html>
    <link rel="stylesheet" href={} />
    <script defer src={}></script>
    <head><title> Goodbye Pittsburgh bot </title></head>
    <body>
        <div class="columns" style="height: 100%">
            <div class="column is-three-fifths is-offset-one-fifth">
              <section class="hero is-info is-large has-background-light has-text-grey-dark" style="height: 100%">
                <div id="parent" class="hero-body" style="overflow: auto; height: calc(100% - 76px); padding-top: 1em; padding-bottom: 0;">
                    <article class="media">
                      <div class="media-content">
                        <div class="content">
                          <p>
                            <strong>Talk with Goodbye Pittsburgh Bot (GPB)</strong>
                            <br>
                            Presented by Team5. Enter a message, and the model will respond interactively.
                          </p>
                        </div>
                      </div>
                    </article>
                </div>
                <div class="hero-foot column is-three-fifths is-offset-one-fifth" style="height: 76px">
                  <form id = "interact">
                      <div class="field is-grouped">
                        <p class="control is-expanded">
                          <input class="input" type="text" id="userIn" placeholder="Type in a message">
                        </p>
                        <p class="control">
                          <button id="respond" type="submit" class="button has-text-white-ter has-background-grey-dark">
                            Submit
                          </button>
                        </p>
                        <p class="control">
                          <button id="restart" type="reset" class="button has-text-white-ter has-background-grey-dark">
                            Reset
                          </button>
                        </p>
                      </div>
                  </form>
                </div>
              </section>
            </div>
        </div>

        <script>
            function createChatRow(agent, text, stamp) {{
                var article = document.createElement("article");
                article.className = "media"

                var figure = document.createElement("figure");
                figure.className = "media-left";

                var span = document.createElement("span");
                span.className = "icon is-large";

                var icon = document.createElement("i");
                icon.className = "fas fas fa-2x" + (agent === "YOU" ? " fa-user " : agent === "GPB" ? " fa-robot" : "");

                var media = document.createElement("div");
                media.className = "media-content";

                var content = document.createElement("div");
                content.className = "content";

                var para = document.createElement("p");
                var paraText = document.createTextNode(text);

                var strong = document.createElement("strong");
                strong.innerHTML = agent;
                var br = document.createElement("br");

                para.appendChild(strong);
                para.appendChild(stamp);
                para.appendChild(br);
                para.appendChild(paraText);
                content.appendChild(para);
                media.appendChild(content);

                span.appendChild(icon);
                figure.appendChild(span);

                if (agent !== "Talk with Goodbye Pittsburgh Bot (GPB)") {{
                    article.appendChild(figure);
                }};

                article.appendChild(media);

                return article;
            }}
            document.getElementById("interact").addEventListener("submit", function(event){{
                event.preventDefault()
                var text = document.getElementById("userIn").value;
                document.getElementById('userIn').value = "";
                var stamp_in = document.createElement("stamp")
                stamp_in.innerHTML = "  (" + new Date().toLocaleDateString() + ", "   + new Date().toTimeString() + ")";

                fetch('/interact', {{
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    method: 'POST',
                    body: text
                }}).then(response=>response.json()).then(data=>{{
                    var parDiv = document.getElementById("parent");

                    parDiv.append(createChatRow("YOU", text, stamp_in));

                    // Change info for Model response
                    var stamp_out = document.createElement("stamp")
                    stamp_out.innerHTML = "  (" + new Date().toLocaleDateString() + ", " + new Date().toTimeString() + ")";
                    parDiv.append(createChatRow("GPB", data.text, stamp_out));
                    parDiv.scrollTo(0, parDiv.scrollHeight);
                }})
            }});
            document.getElementById("interact").addEventListener("reset", function(event){{
                event.preventDefault()
                var text = document.getElementById("userIn").value;
                document.getElementById('userIn').value = "";

                fetch('/reset', {{
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    method: 'POST',
                }}).then(response=>response.json()).then(data=>{{
                    var parDiv = document.getElementById("parent");
                    parDiv.innerHTML = '';
                    var stamp_in = document.createElement("stamp")
                    stamp_in.innerHTML = ""
                    parDiv.append(createChatRow("Talk with Goodbye Pittsburgh Bot (GPB)", "Presented by Team5. Enter a message, and the model will respond interactively.", stamp_in));
                    parDiv.scrollTo(0, parDiv.scrollHeight);
                }})
            }});
        </script>

    </body>
</html>
"""  # noqa: E501


class MyHandler(BaseHTTPRequestHandler):
    """
    Handle HTTP requests.
    """

    def _interactive_running(self, opt, reply_text):
        global flag
        reply = {'episode_done': False, 'text': reply_text}
        SHARED['agent'].observe(reply)
        model_res = SHARED['agent'].act()
        
        if 'weather' in reply_text:
            places = GeoText(reply_text)
            
            if places.cities:
                temp = weather(places.cities[0])
                text = 'Load weather in ' + places.cities[0] + '... ' + temp
            elif places.countries and places.countries != 'South Korea':
                temp = weather(places.countries[0])
                text = 'Load weather in ' + places.countries[0] + '... ' + temp
            elif 'usa' in reply_text.lower() or 'us' in reply_text.lower() or 'america' in reply_text.lower():
                text = 'Load weather in USA... ' + weather('USA')
            elif 'korea' in reply_text.lower():
                text = 'Load weather in Korea... ' + weather('Korea')
            elif 'pitts' in reply_text.lower() or 'pitt' in reply_text.lower():
                text = 'Load weather in Pittsburgh... ' + weather('Pittsburgh')
            else: #default
                text = 'City not found. Load weather in Pittsburgh... ' + weather('Pittsburgh')

            model_res = {'id': model_res['id'], 'episode_done': False, 'text': text}
        elif 'president' in reply_text.lower() and 'north' not in reply_text.lower() and 'south' in reply_text.lower() and 'korea' in reply_text.lower():
            text = 'Moon Jae-in is the president of the South Korea.' 
            model_res = {'id': model_res['id'], 'episode_done': False, 'text': text}
        elif ('joke' in reply_text.lower() and ('know' in reply_text.lower() or 'tell' in reply_text.lower() or 'say' in reply_text.lower())) or 'you\'re fun' in reply_text.lower():
            text = 'Do you know who the Anderw Carnegie is? King of CMU. Man of Steel. Millionaire. Envy him :('
            model_res = {'id': model_res['id'], 'episode_done': False, 'text': text}            
        
        if flag:
            model_res = {'id': model_res['id'], 'episode_done': True, 'text': 'Restart Conversation'}
            flag = False
        elif ' bye' in model_res['text']:
            model_res = {'id': model_res['id'], 'episode_done': True, 'text': model_res['text']}
            flag = True
        return model_res

    def do_HEAD(self):
        """
        Handle HEAD requests.
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        """
        Handle POST request, especially replying to a chat message.
        """
        start = time.time()
        
        if self.path == '/interact':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            model_response = self._interactive_running(
                SHARED.get('opt'), body.decode('utf-8')
            )

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            json_str = json.dumps(model_response)
            self.wfile.write(bytes(json_str, 'utf-8'))
            
            end = time.time()

            file_data1 = "user" + str(n) + '\t' + body.decode('utf-8')  + '\t' + time.strftime('%X',time.localtime(time.time()))
            file_data2 = "chatbot5" + '\t' + model_response['text'] + '\t' +  time.strftime('%X',time.localtime(time.time())) + '\t' + str(round(end-start,3))
            
            with open(file_name, 'a') as f:
                f.write(file_data1 + '\n')
                f.write(file_data2 + '\n')
            
        elif self.path == '/reset':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            SHARED['agent'].reset()
            self.wfile.write(bytes("{}", 'utf-8'))
        else:
            return self._respond({'status': 500})

    def do_GET(self):
        """
        Respond to GET request, especially the initial load.
        """
        paths = {
            '/': {'status': 200},
            '/favicon.ico': {'status': 202},  # Need for chrome
        }
        if self.path in paths:
            self._respond(paths[self.path])
        else:
            self._respond({'status': 500})

    def _handle_http(self, status_code, path, text=None):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content = WEB_HTML.format(STYLE_SHEET, FONT_AWESOME)
        return bytes(content, 'UTF-8')

    def _respond(self, opts):
        response = self._handle_http(opts['status'], self.path)
        self.wfile.write(response)


def setup_interweb_args(shared):
    """
    Build and parse CLI opts.
    """
    parser = setup_args()
    parser.add_argument('--port', type=int, default=PORT, help='Port to listen on.')
    parser.add_argument(
        '--host',
        default=HOST_NAME,
        type=str,
        help='Host from which allow requests, use 0.0.0.0 to allow all IPs',
    )
    return parser


def interactive_web(opt, parser):
    SHARED['opt'] = parser.opt

    SHARED['opt']['task'] = 'parlai.agents.local_human.local_human:LocalHumanAgent'

    # Create model and assign it to the specified task
    agent = create_agent(SHARED.get('opt'), requireModelExists=True)
    SHARED['agent'] = agent
    SHARED['world'] = create_task(SHARED.get('opt'), SHARED['agent'])

    # show args after loading model
    parser.opt = agent.opt
    parser.print_args()
    MyHandler.protocol_version = 'HTTP/1.0'
    httpd = HTTPServer((opt['host'], opt['port']), MyHandler)
    logging.info('http://{}:{}/'.format(opt['host'], opt['port']))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


class InteractiveWeb(ParlaiScript):
    @classmethod
    def setup_args(cls):
        return setup_interweb_args(SHARED)

    def run(self):
        return interactive_web(self.opt, self.parser)


if __name__ == '__main__':
    n = 0
    if os.path.isfile(file_name):
        with open(file_name, 'r') as f:
            lines = f.readlines()
        f.close()

        for i in range(1, len(lines)):
            if "user" in lines[-i]:
                n = int(lines[-i].split('\t')[0].split("user")[1]) + 1
                break
    else:
        with open(file_name, 'w') as f:
            f.write('Source\tData\tTime\tResponse time(sec)\n')
    InteractiveWeb.main()