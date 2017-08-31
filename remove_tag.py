from login_manager import *
from util_functions import UtilFunctions


class RemoveTag:
    """
    This class delete a given tag from the local domain management server
    """

    def __init__(self, tag, args):
        """
        :param tag: tag name which will be deleted
        :param args: the arguments contains parameter about the connection
        """
        login_res = LoginManager(args)
        try:
            # delete the given tag from the local domain
            show_tag_res = args.local_client.api_call("delete-tag", {"name": tag})
            if show_tag_res.success is False:
                UtilFunctions.discard_write_to_log_file(args, args.local_client, "Error: Couldn't delete tag")
            else:
                args.local_client.api_call("publish")

        finally:
            LogoutManager(args, login_res.need_to_logout_from)
