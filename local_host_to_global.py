"""
    This class moves host object from local domain to global domain, by creating on the global domain new object
    which is similar to the object in the local domain

"""
import sys

from args_container import ArgsContainer
from login_manager import *
from util_functions import UtilFunctions


# cp_management_api is a package that handles the communication with the Check Point management server.


# A package for reading passwords without displaying them on the console.


class LocalHostToGlobal:
    def __init__(self, args_container_input):

        if args_container_input.initialize is False:
            args_container_input.log("\nThe arguments are not initialize, try to run build function in order "
                                     "to initialize the arguments ", True)
            return

        self.args_container = args_container_input
        # Original host info
        self.host_details = HostDetails()
        # New host Info
        self.new_obj_uid = []
        self.utils = UtilFunctions()
        self.orig_host_name = None
        login_res = LoginManager(self.args_container)
        try:
            self.run_local_host_to_global()

        finally:
            LogoutManager(args_container_input, login_res.need_to_logout_from)

    def get_info_of_local_host(self):
        """
        This function gets the information of the original object and fill the details for the new object
        :return: False if an error occurred
        """
        host_res = self.args_container.local_client.api_call("show-host", {"uid": self.args_container.obj_uid})

        if host_res.success is False:
            self.args_container.log("Couldn't get the host: '{}' data".format(self.args_container.obj_uid))
            return False

        self.orig_host_name = host_res.data["name"]
        self.host_details.name = self.args_container.prefix + "_" + self.orig_host_name
        self.host_details.ipv4_address = host_res.data["ipv4-address"]
        self.host_details.color = host_res.data["color"]
        self.host_details.comments = host_res.data["comments"]
        if "host-servers" in host_res.data:
            self.host_details.host_servers = host_res.data["host-servers"]
        if "ipv4-address" in host_res.data:
            self.host_details.ipv4_address = host_res.data["ipv4-address"]
        if "ipv6-address" in host_res.data:
            self.host_details.ipv6_address = host_res.data["ipv6-address"]

    def handle_global_domain(self):
        """
        This function creates the new host in the global domain and assign the changes on the local domain
        :return: True on success, otherwise False
        """

        host_uid = self.utils.find_obj_uid_if_exist(self.args_container, "host", self.host_details.name)
        # error occurred while executing "show-host"
        if host_uid is False:
            return
        # the host doesn't exist
        elif host_uid is True:
            # create new host
            self.args_container.log("\nCreating new host: " + self.host_details.name, False)
            pay = self.host_details.to_object
            add_host_res = self.args_container.global_client.api_call("add-host", pay)

            if add_host_res.success is False:
                self.utils.error_creating_new_object(self.args_container, self.orig_host_name,
                                                     self.args_container.obj_uid, "Failed to create new host",
                                                     add_host_res)
                return

            publish_res = self.args_container.global_client.api_call("publish")
            if publish_res.success is False:
                self.utils.error_creating_new_object(self.args_container, self.orig_host_name,
                                                     self.args_container.obj_uid, "Publish failed", publish_res)
                return

            self.utils.successful_object_creation(self.args_container, self.orig_host_name, self.args_container.obj_uid,
                                                  self.host_details.name, add_host_res.data["uid"])

            # saving the new host uid
            self.new_obj_uid.append(add_host_res.data["uid"])
        else:
            self.args_container.log("\n{} already exist and won't be created again".format(self.orig_host_name), False)
            self.new_obj_uid.append(host_uid)

    def run_local_host_to_global(self):

        # handle global domain
        if self.get_info_of_local_host() is False:
            return
        self.handle_global_domain()


if __name__ == "__main__":
    args = ArgsContainer(sys.argv[1:])
    LocalHostToGlobal(args)


class HostDetails:
    def __init__(self):
        self.name = ""
        self.ipv4_address = ""
        self.ipv6_address = ""
        self.comments = ""
        self.color = ""
        self.host_servers = None
        pass

    @property
    def to_object(self):

        if self.host_servers and "web-server-config" in self.host_servers \
                and "standard-port-number" in self.host_servers["web-server-config"]:
            del self.host_servers["web-server-config"]["standard-port-number"]

        obj = {"name": self.name, "comments": self.comments, "color": self.color}
        if self.host_servers:
            obj.update({"host-servers": self.host_servers})
        if self.ipv4_address:
            obj.update({"ipv4-address": self.ipv4_address})
        if self.ipv6_address:
            obj.update({"ipv6-address": self.ipv6_address})
        return obj
