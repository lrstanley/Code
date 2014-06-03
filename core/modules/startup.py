import threading
import time
from util import output
from util.hook import *


# def setup(code):
#     code.data = {}
#     refresh_delay = 300.0

#     if hasattr(code.config, 'refresh_delay'):
#         try:
#             refresh_delay = float(code.config.refresh_delay)
#         except:
#             pass

#         def close():
#             output.error("Nobody PONGed our PING, restarting")
#             code.handle_close()

#         def pingloop():
#             timer = threading.Timer(refresh_delay, close, ())
#             code.data['startup.setup.timer'] = timer
#             code.data['startup.setup.timer'].start()
# print "PING!"
#             code.write(('PING', code.config.host))
#         code.data['startup.setup.pingloop'] = pingloop

#         def pong(code, input):
#             try:
# print "PONG!"
#                 code.data['startup.setup.timer'].cancel()
#                 time.sleep(refresh_delay + 60.0)
#                 pingloop()
#             except:
#                 pass
#         pong.event = 'PONG'
#         pong.thread = True
#         pong.rule = r'.*'
#         code.variables['pong'] = pong

# Need to wrap handle_connect to start the loop.
#         inner_handle_connect = code.handle_connect

#         def outer_handle_connect():
#             inner_handle_connect()
#             if code.data.get('startup.setup.pingloop'):
#                 code.data['startup.setup.pingloop']()

#         code.handle_connect = outer_handle_connect


@hook(rule=r'.*', event='251', priority='low')
def startup(code, input):
    if code.config('nickserv_password'):
        if code.config('nickserv_username'):
            args = code.config('nickserv_username') + ' ' + \
                code.config('nickserv_password')
        else:
            args = code.config('nickserv_password')
        code.write(['PRIVMSG', 'NickServ'], 'IDENTIFY %s' % args, output=False)
        time.sleep(5)

    for channel in code.channels:
        code.join(channel)
        time.sleep(0.5)
