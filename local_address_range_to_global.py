"""
    This class moves address-range object from local domain to global domain, by creating on the global domain new
    object which is similar to the object in the local domain

"""
import sys

from args_container import ArgsContainer
from login_manager import *
from util_functions import UtilFunctions


class LocalAddressRangeToGlobal:
    def __init__(self, args_container_input):

        if args_container_input.initialize is False:
            self.args_container.log("\nThe arguments are not initialize, try to run build function in order "
                                    "to initialize the arguments ", True)
            return

        self.args_container = args_container_input
        # Original address-range info
        self.add_range_details = AddressDetails()
        self.utils = UtilFunctions()
        self.new_obj_uid = []
        self.orig_add_range_name = None
        login_res = LoginManager(self.args_container)
        try:
            self.run_local_add_range_to_global()

        finally:
            LogoutManager(self.args_container, login_res.need_to_logout_from)

    def get_info_of_local_address_range(self):
        """
        This function gets the information of the original object and fill the details for the new object
        :return: False if an error occurred
        """
        add_res = self.args_container.local_client.api_call("show-address-range", {"uid": self.args_container.obj_uid})

        if add_res.success is False:
            self.args_container.log("Couldn't get the address-range: '{}' data".format(self.args_container.obj_uid))
            return False
        self.orig_add_range_name = add_res.data["name"]
        self.add_range_details.name = self.args_container.prefix + "_" + self.orig_add_range_name
        self.add_range_details.color = add_res.data["color"]
        self.add_range_details.comments = add_res.data["comments"]

        if "ip-address-first" in add_res.data:
            self.add_range_details.ip_address_first = add_res.data["ip-address-first"]
        if "ipv4-address-first" in add_res.data:
            self.add_range_details.ipv4_address_first = add_res.data["ipv4-address-first"]
        if "ipv6-address-first" in add_res.data:
            self.add_range_details.ipv6_address_first = add_res.data["ipv6-address-first"]
        if "ip-address-last" in add_res.data:
            self.add_range_details.ip_address_last = add_res.data["ip-address-last"]
        if "ipv4-address-last" in add_res.data:
            self.add_range_details.ipv4_address_last = add_res.data["ipv4-address-last"]
        if "ipv6-address-last" in add_res.data:
            self.add_range_details.ipv6_address_last = add_res.data["ipv6-address-last"]

    def handle_global_domain(self):
        """
        This function creates the new address-range in the global domain and assign the changes on the local domain
        :return: True on success, otherwise False
        """

        add_uid = self.utils.find_obj_uid_if_exist(self.args_container, "address-range", self.add_range_details.name)
        # error occurred while executing "show-address-range"
        if add_uid is False:
            return
        # the address-range doesn't exist
        elif add_uid is True:
            # create new address-range
            self.args_container.log("\nCreating new address-range: " + self.add_range_details.name, False)
            pay = self.add_range_details.to_object
            add_add_res = self.args_container.global_client.api_call("add-address-range", pay)

            if add_add_res.success is False:
                self.utils.error_creating_new_object(self.args_container, self.orig_add_range_name,
                                                     self.args_container.obj_uid, "Failed to create new address-range",
                                                     add_add_res)
                return

            publish_res = self.args_container.global_client.api_call("publish")
            if publish_res.success is False:
                self.utils.error_creating_new_object(self.args_container, self.orig_add_range_name,
                                                     self.args_container.obj_uid, "Publish failed", publish_res)
                return

            self.utils.successful_object_creation(self.args_container, self.orig_add_range_name,
                                                  self.args_container.obj_uid, self.add_range_details.name,
                                                  add_add_res.data["uid"])
            # saving the new address-range uid
            self.new_obj_uid.append(add_add_res.data["uid"])
        else:
            self.args_container.log("\n{} already exist and won't be created again".format(self.orig_add_range_name),
                                    False)
            self.new_obj_uid.append(add_uid)

    def run_local_add_range_to_global(self):

        # handle global domain
        if self.get_info_of_local_address_range() is False:
            return
        self.handle_global_domain()


if __name__ == "__main__":
    args = ArgsContainer(sys.argv[1:])
    LocalAddressRangeToGlobal(args)


class AddressDetails:
    def __init__(self):
        self.name = None
        self.ip_address_first = None
        self.ipv4_address_first = None
        self.ipv6_address_first = None
        self.ip_address_last = None
        self.ipv4_address_last = None
        self.ipv6_address_last = None
        self.color = None
        self.comments = None

    @property
    def to_object(self):
        obj = {"name": self.name, "comments": self.comments, "color": self.color}
        if self.ip_address_first:
            obj.update({"ip-address-first": self.ip_address_first})
        if self.ipv4_address_first:
            obj.update({"ipv4-address-first": self.ipv4_address_first})
        if self.ipv6_address_first:
            obj.update({"ipv6-address-first": self.ipv6_address_first})
        if self.ip_address_last:
            obj.update({"ip-address-last": self.ip_address_last})
        if self.ipv4_address_last:
            obj.update({"ipv4-address-last": self.ipv4_address_last})
        if self.ipv6_address_last:
            obj.update({"ipv6-address-last": self.ipv6_address_last})

        return obj
