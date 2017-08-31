"""
This class is responsible cloning udp and tcp services
"""
import sys

from args_container import ArgsContainer
from login_manager import *
from util_functions import UtilFunctions


class LocalTcpToGlobal:
    """
        This class moves tcp service object from local domain to global domain, by creating on the global domain new
        object which is similar to the object in the local domain

    """

    def __init__(self, args_container_input):
        tcp = LocalTcpUdpToGlobal(args_container_input, "tcp")
        self.new_obj_uid = tcp.new_obj_uid


class LocalUdpToGlobal:
    """
        This class moves udp service object from local domain to global domain, by creating on the global domain new
         object which is similar to the object in the local domain

    """

    def __init__(self, args_container_input):
        udp = LocalTcpUdpToGlobal(args_container_input, "udp")
        self.new_obj_uid = udp.new_obj_uid


class LocalTcpUdpToGlobal:
    def __init__(self, args_container_input, service_type):

        if args_container_input.initialize is False:
            args_container_input.log("\nThe arguments are not initialize, try to run build function in order "
                                     "to initialize the arguments ", True)
            return

        self.args_container = args_container_input
        # Original tcp service info
        self.tcp_udp_details = TcpUdpDetails()
        if service_type == "udp":
            self.tcp_udp_details.udp = True
        # service_type == "tcp":
        else:
            self.tcp_udp_details.udp = False
        self.utils = UtilFunctions()
        self.new_obj_uid = []
        self.orig_tcp_udp_service_name = None
        login_res = LoginManager(self.args_container)
        try:
            self.run_local_tcp_service_to_global()

        finally:
            LogoutManager(args_container_input, login_res.need_to_logout_from)

    def get_info_of_local_tcp_udp_service(self):
        """
        This function gets the information of the original object and fill the details for the new object
        :return: False if an error occurred
        """
        command = "show-service-tcp"
        if self.tcp_udp_details.udp:
            command = "show-service-udp"

        tcp_res = self.args_container.local_client.api_call(command, {"uid": self.args_container.obj_uid})

        if tcp_res.success is False:
            self.args_container.log("Couldn't get the tcp service: '{}' data".format(self.args_container.obj_uid))
            return False
        self.orig_tcp_udp_service_name = tcp_res.data["name"]
        self.tcp_udp_details.name = self.args_container.prefix + "_" + self.orig_tcp_udp_service_name
        self.tcp_udp_details.port = tcp_res.data["port"]
        self.tcp_udp_details.color = tcp_res.data["color"]
        self.tcp_udp_details.comments = tcp_res.data["comments"]
        self.tcp_udp_details.aggressive_aging = tcp_res.data["aggressive-aging"]
        self.tcp_udp_details.keep_connections_open_after_policy_installation = \
            tcp_res.data["keep-connections-open-after-policy-installation"]
        self.tcp_udp_details.match_by_protocol_signature = tcp_res.data["match-by-protocol-signature"]
        self.tcp_udp_details.match_for_any = tcp_res.data["match-for-any"]
        self.tcp_udp_details.session_timeout = tcp_res.data["session-timeout"]
        self.tcp_udp_details.sync_connections_on_cluster = tcp_res.data["sync-connections-on-cluster"]
        if "protocol" in tcp_res.data and tcp_res.data["protocol"]:
            self.tcp_udp_details.protocol = tcp_res.data["protocol"]
        if "source-port" in tcp_res.data and tcp_res.data["source-port"]:
            self.tcp_udp_details.source_port = tcp_res.data["source-port"]
        if self.tcp_udp_details.udp:
            self.tcp_udp_details.accept_replies = tcp_res.data["accept-replies"]

    def handle_global_domain(self):
        """
        This function creates the new tcp service in the global domain and assign the changes on the local domain
        :return: True on success, otherwise False
        """

        type_obj = "service-tcp"
        if self.tcp_udp_details.udp:
            type_obj = "service-udp"

        tcp_uid = self.utils.find_obj_uid_if_exist(self.args_container, type_obj, self.tcp_udp_details.name)
        # error occurred while executing "show-tcp service"
        if tcp_uid is False:
            return
        # the tcp service doesn't exist
        elif tcp_uid is True:
            # create new tcp service
            self.args_container.log("\nCreating new service service: " + self.tcp_udp_details.name, False)
            pay = self.tcp_udp_details.to_object
            command = "add-" + type_obj
            add_service_res = self.args_container.global_client.api_call(command, pay)

            if add_service_res.success is False:
                self.utils.error_creating_new_object(self.args_container, self.orig_tcp_udp_service_name,
                                                     self.args_container.obj_uid, "Failed to create new service",
                                                     add_service_res)
                return

            publish_res = self.args_container.global_client.api_call("publish")
            if publish_res.success is False:
                self.utils.error_creating_new_object(self.args_container, self.orig_tcp_udp_service_name,
                                                     self.args_container.obj_uid, "Publish failed", publish_res)
                return

            self.utils.successful_object_creation(self.args_container, self.orig_tcp_udp_service_name,
                                                  self.args_container.obj_uid, self.tcp_udp_details.name,
                                                  add_service_res.data["uid"])

            # saving the new tcp service uid
            self.new_obj_uid.append(add_service_res.data["uid"])

        else:
            self.args_container.log(
                "\n{} already exist and won't be created again".format(self.orig_tcp_udp_service_name), False)
            self.new_obj_uid.append(tcp_uid)

    def run_local_tcp_service_to_global(self):

        # handle global domain
        if self.get_info_of_local_tcp_udp_service() is False:
            return
        self.handle_global_domain()


if __name__ == "__main__":
    args = ArgsContainer(sys.argv[2:])
    LocalTcpUdpToGlobal(args, sys.argv[1])


class TcpUdpDetails:
    def __init__(self):
        self.udp = True
        self.accept_replies = None
        self.name = ""
        self.aggressive_aging = None
        self.keep_connections_open_after_policy_installation = None
        self.match_by_protocol_signature = None
        self.match_for_any = None
        self.port = ""
        self.protocol = ""
        self.session_timeout = ""
        self.source_port = ""
        self.sync_connections_on_cluster = None
        self.comments = ""
        self.color = ""
        pass

    @property
    def to_object(self):

        obj = {"name": self.name, "comments": self.comments, "color": self.color, "port": self.port,
               "aggressive-aging": self.aggressive_aging, "keep-connections-open-after-policy-installation":
                   self.keep_connections_open_after_policy_installation, "match-by-protocol-signature":
                   self.match_by_protocol_signature, "match-for-any": self.match_for_any, "session-timeout":
                   self.session_timeout, "sync-connections-on-cluster": self.sync_connections_on_cluster}
        if self.protocol:
            obj.update({"protocol": self.protocol})
        if self.source_port:
            obj.update({"source-port": self.source_port})
        if self.udp and self.accept_replies:
            obj.update({"accept-replies": self.accept_replies})
        return obj
