"""
This class is used as a dispatcher, calls the relevant function according to the type object
"""

import sys

from args_container import ArgsContainer
from local_address_range_to_global import LocalAddressRangeToGlobal
from local_group_to_global import LocalGroupToGlobal
from local_group_to_global import LocalServiceGroupToGlobal
from local_host_to_global import LocalHostToGlobal
from local_network_to_global import LocalNetworkToGlobal
from local_tcp_udp_service_to_global import LocalTcpToGlobal
from local_tcp_udp_service_to_global import LocalUdpToGlobal
from login_manager import *
from util_functions import UtilFunctions


class Dispatcher:
    unsupported = set([])

    def __init__(self, args_container, objects_info=None):
        """
        This class responsible to call the relevant class to handle the objects according to the object type
        :param args_container: arguments which contains the information about the API client and the objects
        :param objects_info: objects info which should include the objects uid
        """
        self.uids = []

        if args_container.initialize is False:
            args_container.log("\nThe arguments are not initialize, try to run build function in order "
                               "to initialize the arguments ", True)
            return

        login_res = LoginManager(args_container)
        try:
            if objects_info is None:
                if args_container.obj_uid is None:
                    UtilFunctions.discard_write_to_log_file(args_container, args_container.local_client,
                                                            "Object uid Doesnt exist")

                type_obj = self.get_obj_type(args_container.obj_uid, args_container)
                if type_obj is None:
                    return
                obj = self.call_relevant_func(type_obj, args_container)
                self.uids += obj.new_obj_uid
            else:
                # the user passed a objects info
                obj_uid = args_container.obj_uid

                # go over all the objects
                for object_info in objects_info:
                    obj = self.handle_object(object_info, args_container)
                    # collects the uid of the new objects
                    if obj is not None:
                        self.uids += obj.new_obj_uid

                args_container.obj_uid = obj_uid
        finally:
            LogoutManager(args_container, login_res.need_to_logout_from)

    @staticmethod
    def get_obj_type(uid, args_container):
        """
        This function the type of a given object
        :param uid: object uid
        :param args_container: arguments which contains the information about the API client and the objects
        :return: type object
        """
        show_res = args_container.local_client.api_call("show-object", {"uid": uid})
        if show_res.success is False:
            args_container.log("Couldn't get Object uid: {} data, object won't be cloned", uid)
            args_container.write_to_csv_file("", uid, "", "")
            return None

        return show_res.data["object"]["type"]

    @staticmethod
    def call_relevant_func(type_obj, args_container):
        """
        This function calls the relevant class to handle the object according to his type
        :param type_obj: object type
        :param args_container: arguments which contains the information about the API client and the objects
        :return the result of the move action
        """
        switcher = {
            "host": LocalHostToGlobal,
            "group": LocalGroupToGlobal,
            "network": LocalNetworkToGlobal,
            "service-tcp": LocalTcpToGlobal,
            "service-udp": LocalUdpToGlobal,
            "service-group": LocalServiceGroupToGlobal,
            "address-range": LocalAddressRangeToGlobal
        }
        if type_obj not in switcher:
            if args_container.obj_uid in Dispatcher.unsupported:
                return
            args_container.log("\nObject of type {} is unsupported".format(type_obj))
            UtilFunctions.unsupported_type_find_name_and_write_to_file(args_container)
            Dispatcher.unsupported.add(args_container.obj_uid)
            return

        return switcher[type_obj](args_container)

    def handle_object(self, object_info, args_container):
        """
        This function gets the type of a given objects and sends it to relevant
        :param object_info:
        :param args_container:
        :return:
        """
        if object_info["type"] is None:
            if object_info["uid"]:
                type_obj = self.get_obj_type(object_info["uid"], args_container)
                if type_obj is None:
                    return None
                args_container.obj_uid = object_info["uid"]
            else:
                args_container.log("Couldn't get Object, object won't be cloned")
                return None

        elif object_info["uid"]:
            type_obj = object_info["type"]
            args_container.obj_uid = object_info["uid"]
        else:
            args_container.log("Couldn't get Object, object won't be cloned")
            return None

        return self.call_relevant_func(type_obj, args_container)


if __name__ == "__main__":
    args = ArgsContainer(sys.argv[1:])
    Dispatcher(args)
