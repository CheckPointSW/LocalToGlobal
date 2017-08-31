"""
    This class moves network object from local domain to global domain, by creating on the global domain new object
     which is similar to the object in the local domain

"""
import sys

from args_container import ArgsContainer
from login_manager import *
from util_functions import UtilFunctions


class LocalNetworkToGlobal:
    def __init__(self, args_container_input):

        if args_container_input.initialize is False:
            args_container_input.log("\nThe arguments are not initialize, try to run build function in order "
                                     "to initialize the arguments ", True)
            return

        self.args_container = args_container_input
        # Original network info
        self.net_details = NetworkDetails()
        # New network Info
        self.utils = UtilFunctions()
        self.new_obj_uid = []
        self.orig_net_name = None
        login_res = LoginManager(self.args_container)
        try:
            self.run_local_network_to_global()

        finally:
            LogoutManager(self.args_container, login_res.need_to_logout_from)

    def get_info_of_local_network(self):
        """
        This function gets the information of the original object and fill the details for the new object
        :return: False if an error occurred
        """
        net_res = self.args_container.local_client.api_call("show-network", {"uid": self.args_container.obj_uid})

        if net_res.success is False:
            self.args_container.log("Couldn't get the network: '{}' data".format(self.args_container.obj_uid))
            return False
        self.orig_net_name = net_res.data["name"]
        self.net_details.name = self.args_container.prefix + "_" + self.orig_net_name
        self.net_details.broadcast = net_res.data["broadcast"]
        self.net_details.color = net_res.data["color"]
        self.net_details.comments = net_res.data["comments"]

        if "subnet" in net_res.data:
            self.net_details.subnet = net_res.data["subnet"]
        if "subnet4" in net_res.data:
            self.net_details.subnet4 = net_res.data["subnet4"]
        if "subnet6" in net_res.data:
            self.net_details.subnet6 = net_res.data["subnet6"]
        if "mask-length" in net_res.data:
            self.net_details.mask_length = net_res.data["mask-length"]
        if "mask-length4" in net_res.data:
            self.net_details.mask_length4 = net_res.data["mask-length4"]
        if "mask-length6" in net_res.data:
            self.net_details.mask_length6 = net_res.data["mask-length6"]
            # if "subnet-mask" in net_res.data:
            #     self.net_details.subnet_mask = net_res.data["subnet-mask"]

    def handle_global_domain(self):
        """
        This function creates the new network in the global domain and assign the changes on the local domain
        :return: True on success, otherwise False
        """

        net_uid = self.utils.find_obj_uid_if_exist(self.args_container, "network", self.net_details.name)
        # error occurred while executing "show-network"
        if net_uid is False:
            return
        # the network doesn't exist
        elif net_uid is True:
            # create new network
            self.args_container.log("\nCreating new network: " + self.net_details.name, False)
            pay = self.net_details.to_object
            add_net_res = self.args_container.global_client.api_call("add-network", pay)

            if add_net_res.success is False:
                self.utils.error_creating_new_object(self.args_container, self.orig_net_name,
                                                     self.args_container.obj_uid, "Failed to create new network",
                                                     add_net_res)
                return

            publish_res = self.args_container.global_client.api_call("publish")
            if publish_res.success is False:
                self.utils.error_creating_new_object(self.args_container, self.orig_net_name,
                                                     self.args_container.obj_uid, "Publish failed", publish_res)
                return

            self.utils.successful_object_creation(self.args_container, self.orig_net_name, self.args_container.obj_uid,
                                                  self.net_details.name, add_net_res.data["uid"])
            # saving the new network uid
            self.new_obj_uid.append(add_net_res.data["uid"])

        else:
            self.args_container.log("\n{} already exist and won't be created again".format(self.orig_net_name), False)
            self.new_obj_uid.append(net_uid)

    def run_local_network_to_global(self):

        # handle global domain
        if self.get_info_of_local_network() is False:
            return
        self.handle_global_domain()


if __name__ == "__main__":
    args = ArgsContainer(sys.argv[1:])
    LocalNetworkToGlobal(args)


class NetworkDetails:
    def __init__(self):
        self.name = ""
        self.subnet = ""
        self.subnet4 = ""
        self.subnet6 = ""
        self.mask_length = ""
        self.mask_length4 = ""
        self.mask_length6 = ""
        self.subnet_mask = ""
        self.broadcast = ""
        self.color = ""
        self.comments = ""
        pass

    @property
    def to_object(self):

        obj = {"name": self.name, "comments": self.comments, "color": self.color, "broadcast": self.broadcast}
        if self.subnet:
            obj.update({"subnet": self.subnet})
        if self.subnet4:
            obj.update({"subnet4": self.subnet4})
        if self.subnet6:
            obj.update({"subnet6": self.subnet6})
        if self.mask_length:
            obj.update({"mask-length": self.mask_length})
        if self.mask_length4:
            obj.update({"mask-length4": self.mask_length4})
        if self.mask_length6:
            obj.update({"mask-length6": self.mask_length6})
        # if self.subnet_mask:
        #     obj.update({"subnet-mask": self.subnet_mask})

        return obj
