from __future__ import print_function

"""
This class holds all the arguments which relevant for the moving  object from local domain to global domain
"""
import argparse
import datetime
import getpass
import json
import socket
import sys
import time

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

class ArgsContainer:
    def __init__(self, args=None):

        # server args
        self.server = None
        self.username = None
        self.password = None
        self.port = 443
        self.local_domain = None
        self.global_domain = None

        # details of the object
        self.obj_uid = None
        # prefix for the name of the new object
        self.prefix = None

        # API clients (contains the connection details)
        self.local_client = None
        self.global_client = None

        # check if args initialize
        self.initialize = False
        self.log_file = None
        self.csv_file = None
        self.csv_writer = None
        self.json_file = None
        self.timestamp = None

        self.login_as_root = True

        # insert the args throw flags
        self.parse_args(args)



    def parse_args(self, args):

        parser = argparse.ArgumentParser()
        parser.add_argument("-s", type=str, action="store", help="Server IP address or hostname", dest="server")
        parser.add_argument("-u", type=str, action="store", help="User name", dest="username")
        parser.add_argument("-p", type=int, action="store", help="Port", default=443, dest="port")
        parser.add_argument("-d", type=str, action="store", help="Local domain name ", dest="local_domain")
        parser.add_argument("-g", type=str, action="store", default="Global", help="Global domain name",
                            dest="global_domain")
        parser.add_argument("-o", type=str, action="store", help="Object uid", dest="obj_uid")
        parser.add_argument("-n", type=str, action="store", help="New object prefix", dest="prefix")
        parser.add_argument("--login-as-root", type=str2bool, nargs="?", action="store",
                            help="Whether to login as root on the management server or not.", default=True)

        args = parser.parse_args(args)

        required = ["local_domain", "prefix"]

        for r in required:
            if args.__dict__[r] is None:
                parser.error("parameter '%s' required" % r)

        self.build(local_domain=args.local_domain, prefix=args.prefix, port=args.port, server=args.server, username=args.username,
                   obj_uid=args.obj_uid, global_domain=args.global_domain, login_as_root=args.login_as_root)

    def build(self, local_domain, prefix, port=443, server=None, username=None, obj_uid=None,
              global_domain="Global", local_client=None, global_client=None, login_as_root=None):
        """
        This function initialize the class parameters, and set the initialize flag to true
        """
        password = None
        if server is not None:
            if username is not None:
                if sys.stdin.isatty():
                    password = getpass.getpass("Enter password: ")
                else:
                    print("Attention! Your password will be shown on the screen!")
                    password = raw_input("Enter password: ")
                self.login_as_root = False
            else:
                # username does't exist check that server is local ip
                local_host_ip = ['127.0.0.1', 'localhost', socket.gethostbyname(socket.gethostname())]
                if server not in local_host_ip:
                    # the server is not local and the user name is missing
                    raise Exception("parameter 'user name' required")

        self.server = server
        self.username = username
        self.password = password
        self.port = port
        self.local_domain = local_domain
        self.global_domain = global_domain
        self.obj_uid = obj_uid
        self.prefix = prefix
        self.local_client = local_client
        self.global_client = global_client
        #self.login_as_root = login_as_root
        ts = time.time()
        self.timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')

        # the argument were initialize
        self.initialize = True

    def log(self, message, to_print=True):
        """
        This method writes message to the log file and print it
        :param to_print: If to print to the stderr
        :param message: message that will be written to log file
        """
        if self.log_file is None:
            return
        print(message, file=self.log_file)
        if to_print is True:
            print(message)

    def write_to_csv_file(self, original_obj_name, original_obj_uid, new_obj_name, new_obj_uid):
        self.csv_writer.writerow({'Original_name': original_obj_name, 'Original_uid': original_obj_uid,
                                  'New_name': new_obj_name, 'New_uid': new_obj_uid})

    def write_to_json_file(self, original_obj_uid, new_obj_uid):
        print(json.dumps({original_obj_uid: new_obj_uid}), file=self.log_file)
