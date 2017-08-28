"""
    This class moves group object from local domain to global domain, by creating on the global domain new object
    which is similar to the object in the local domain

"""

import sys

import local_object_to_global
from args_container import ArgsContainer
from login_manager import *
from util_functions import UtilFunctions


class LocalServiceGroupToGlobal:
    def __init__(self, args_container_input):
        group = LocalGroupToGlobal(args_container_input, True)
        self.new_obj_uid = group.new_obj_uid


class LocalGroupToGlobal:
    def __init__(self, args_container_input, service=False):

        if args_container_input.initialize is False:
            args_container_input.log("\nThe arguments are not initialize, try to run build function in order "
                                     "to initialize the arguments ", True)
            return

        self.args_container = args_container_input
        # Original network info
        self.group_details = GroupDetails()
        self.group_details.service = service
        # New network Info
        self.utils = UtilFunctions()
        self.members = None
        self.new_obj_uid = []
        self.orig_group_name = None
        login_res = LoginManager(self.args_container)
        try:
            self.run_local_group_to_global()

        finally:
            LogoutManager(self.args_container, login_res.need_to_logout_from)

    def get_info_of_local_group(self):
        """
        This function gets the information of the original object and fill the details for the new object
        :return: False if an error occurred
        """
        command = "show-group"
        if self.group_details.service:
            command = "show-service-group"

        group_res = self.args_container.local_client.api_call(command, {"uid": self.args_container.obj_uid})

        if group_res.success is False:
            self.args_container.log("Couldn't get the group: '{}' data".format(self.args_container.obj_uid))
            return False
        self.orig_group_name = group_res.data["name"]
        self.group_details.name = self.args_container.prefix + "_" + self.orig_group_name
        self.group_details.color = group_res.data["color"]
        self.group_details.comments = group_res.data["comments"]
        self.members = group_res.data["members"]

    def handle_global_domain(self):
        """
        This function creates the new network in the global domain and assign the changes on the local domain
        :return: True on success, otherwise False
        """
        obj_type = "group"
        if self.group_details.service:
            obj_type = "service-group"

        group_uid = self.utils.find_obj_uid_if_exist(self.args_container, obj_type, self.group_details.name)
        # error occurred while executing "show-network"
        if group_uid is False:
            return
        # the network doesn't exist
        elif group_uid is True:
            # create new network
            self.group_details.members = local_object_to_global.Dispatcher(self.args_container, self.members).uids
            pay = self.group_details.to_object

            self.args_container.log("\nCreating new group: " + self.group_details.name, False)
            command = "add-" + obj_type
            add_group_res = self.args_container.global_client.api_call(command, pay)

            if add_group_res.success is False:
                self.utils.error_creating_new_object(self.args_container, self.orig_group_name,
                                                     self.args_container.obj_uid, "Failed to create new group",
                                                     add_group_res)
                return

            publish_res = self.args_container.global_client.api_call("publish")
            if publish_res.success is False:
                self.utils.error_creating_new_object(self.args_container, self.orig_group_name,
                                                     self.args_container.obj_uid, "Publish failed", publish_res)
                return

            self.utils.successful_object_creation(self.args_container, self.orig_group_name,
                                                  self.args_container.obj_uid, self.group_details.name,
                                                  add_group_res.data["uid"])
            # saving the new network uid
            self.new_obj_uid.append(add_group_res.data["uid"])
        else:
            self.args_container.log("\n{} already exist and won't be created again".format(self.orig_group_name), False)
            self.new_obj_uid.append(group_uid)

    def run_local_group_to_global(self):

        # handle global domain
        if self.get_info_of_local_group() is False:
            return
        self.handle_global_domain()


if __name__ == "__main__":
    args = ArgsContainer(sys.argv[1:])
    LocalGroupToGlobal(args)


class GroupDetails:
    def __init__(self):
        self.service = False
        self.name = None
        self.color = None
        self.comments = None
        self.members = []

    @property
    def to_object(self):
        obj = {"name": self.name, "comments": self.comments, "color": self.color, "members": self.members}
        return obj
