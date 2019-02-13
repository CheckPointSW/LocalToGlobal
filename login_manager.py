import csv
import os

from cpapi import api_exceptions, mgmt_api


# the path to the current directory
path = os.path.dirname(os.path.abspath(__file__)) + os.sep


class LoginManager:
    def __init__(self, args):
        global path
        self.need_to_logout_from = {"local": False, "global": False, "log_file": False, "csv_file": False,
                                    "json_file": False}

        if args.local_client is None:
            args.local_client = self.init_client_by_login(args, args.local_domain)
            self.need_to_logout_from["local"] = True
            args.local_client.debug_file = path + "api_calls_local.json"

        if args.global_client is None:
            args.global_client = self.init_client_by_login(args, args.global_domain)
            self.need_to_logout_from["global"] = True
            args.global_client.debug_file = path + "api_calls_global.json"

        if args.log_file is None:
            args.log_file = open(path + 'logfile_' + args.timestamp + '.txt', 'w+')
            self.need_to_logout_from["log_file"] = True

        if args.csv_file is None:
            args.csv_file = open(path + 'clone_object_report_' + args.timestamp + '.csv', 'wb')
            fieldnames = ['Original_name', 'Original_uid', 'New_name', 'New_uid']
            args.csv_writer = csv.DictWriter(args.csv_file, fieldnames=fieldnames)
            args.csv_writer.writeheader()
            self.need_to_logout_from["csv_file"] = True

        if args.json_file is None:
            args.json_file = open(path + 'json_objects_' + args.timestamp + '.json', 'w+')
            self.need_to_logout_from["json_file"] = True

    @staticmethod
    def init_client_by_login(args, domain=""):
        client_args = mgmt_api.APIClientArgs(server=args.server, port=args.port)
        client = mgmt_api.APIClient(client_args)
        if args.login_as_root is True:
            try:
                login_response = client.login_as_root(domain=domain)
            except api_exceptions.APIClientException:
                raise Exception("Error: Couldn't login as root to management server. "
                                "Check that the local and global domain names are correct.")
        else:
            login_response = client.login(args.username, args.password, domain=domain)
        if login_response.success is False:
            raise Exception("Error: Couldn't login to server: {}. "
                            "Check that the local and global domain names are correct.".format(args.server))
        return client


class LogoutManager:
    def __init__(self, args, need_to_logout_from=None):

        if args.local_client is not None and (need_to_logout_from is None or need_to_logout_from["local"]):
            args.local_client.api_call("logout")
            args.local_client.save_debug_data()
            args.local_client = None

        if args.global_client is not None and (need_to_logout_from is None or need_to_logout_from["global"]):
            args.global_client.api_call("logout")
            args.global_client.save_debug_data()
            args.global_client = None

        if args.log_file is not None and (need_to_logout_from is None or need_to_logout_from["log_file"]):
            args.log_file.close()
            args.log_file = None

        if args.csv_file is not None and (need_to_logout_from is None or need_to_logout_from["csv_file"]):
            args.csv_file.close()
            args.csv_file = None

        if args.json_file is not None and (need_to_logout_from is None or need_to_logout_from["json_file"]):
            args.json_file.close()
            args.json_file = None
