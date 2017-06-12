import awsso
import ssoserver
import threading
import sys

server_thread = threading.Thread(target=ssoserver.serve)
server_thread.start()
awsso.initiate_sso()
