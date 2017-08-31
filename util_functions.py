class UtilFunctions:
    failed_objects = set([])

    def __init__(self):
        pass

    @staticmethod
    def discard_write_to_log_file(args_container, api_client, message):
        """
        This method discards the changes for a given api client and save message to the log file
        :param args_container:
        :param api_client: Api client of the domain
        :param message: message that will be written to log file
        """
        api_client.api_call("discard", {})
        args_container.log(message)

    @staticmethod
    def error_creating_new_object(args_container, original_obj_name, original_obj_uid, message, response):
        if original_obj_uid in UtilFunctions.failed_objects:
            return

        args_container.write_to_csv_file(original_obj_name, original_obj_uid, "", "")
        UtilFunctions.discard_write_to_log_file(args_container, args_container.global_client,
                                                "Object name: {} uid: {} won't be created in the global domain"
                                                .format(original_obj_name, original_obj_uid))
        if "code" in response.data:
            message += "\nCode: {}".format(response.data["code"])
        if "message" in response.data:
            message += "\nMessage: {}".format(response.data["message"])
        if "warnings" in response.data:
            message += "\nWarnings: "
            for mess in response.data["warnings"]:
                message += "\n\t{}".format(mess["message"])
        if "errors" in response.data:
            message += "\nErrors: "
            for mess in response.data["errors"]:
                message += "\n\t{}".format(mess["message"])

        args_container.log(message, False)
        UtilFunctions.failed_objects.add(original_obj_uid)

    @staticmethod
    def successful_object_creation(args_container, original_obj_name, original_obj_uid, new_obj_name, new_obj_uid):
        args_container.write_to_csv_file(original_obj_name, original_obj_uid, new_obj_name, new_obj_uid)
        args_container.write_to_json_file(original_obj_uid, new_obj_uid)

    @staticmethod
    def find_obj_uid_if_exist(args_container, obj_type, name):
        """
          This method checks if the new object is already exists, if so the method returns false
          :return: True, if the address-range doesn't exist
                   False, if error occurred or the address-range exist
        """
        command = "show-" + obj_type
        res = args_container.global_client.api_call(command, {"name": name})

        if res.success is False:
            if "code" in res.data and "generic_err_object_not_found" == res.data["code"]:
                return True

            message = "Operation failed: {}. Aborting all changes.".format(res.error_message)
            UtilFunctions.discard_write_to_log_file(args_container, args_container.global_client, message)
            return False

        return res.data["uid"]

    @staticmethod
    def unsupported_type_find_name_and_write_to_file(args_container):
        """
        :param args_container:
        """
        uid = args_container.obj_uid
        res_show_obj = args_container.local_client.api_call("show-object", {"uid": uid})
        if res_show_obj.success is False:
            args_container.write_to_csv_file("", uid, "", "")
            args_container.log("\tObject uid: {} won't be created in the global domain".format(uid))
        else:
            if "object" in res_show_obj.data and "name" in res_show_obj.data["object"]:
                name = res_show_obj.data["object"]["name"]
                args_container.write_to_csv_file(name, uid, "", "")
                args_container.log("\tObject name: {} uid: {} won't be created in the global domain".format(name, uid))
            else:
                args_container.write_to_csv_file("", uid, "", "")
                args_container.log("\tObject uid: {} won't be created in the global domain".format(uid))
