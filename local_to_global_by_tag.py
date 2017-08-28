import sys

from args_container import ArgsContainer
from local_object_to_global import Dispatcher
from login_manager import *
from remove_tag import RemoveTag


class LocalToGlobalByTag:
    def __init__(self, tag, args_container):
        """
        This class moves all the object in the local domain that tagged with a given tag to to global domain
        :param tag: tag name
        :param args_container: arguments that contains Api client and information that relevant for the action
        """

        if args_container.initialize is False:
            args_container.log("\nThe arguments are not initialize, try to run build function in order "
                               "to initialize the arguments ", True)
            return

        login_res = LoginManager(args_container)
        try:
            start_string = "\nStart cloning objects that contains tag: {}, from local domain: {} to " \
                           "global_domain: {}\n".format(tag, args_container.local_domain, args_container.global_domain)
            print(start_string)
            print("-" * len(start_string))
            show_tag_res = args_container.local_client.api_call("show-tag", {"name": tag})
            if show_tag_res.success is False:
                args_container.log("Error: Couldn't get tag data")
                exit()
            tag_objects = self.collect_all_objects(args_container, show_tag_res.data["uid"])
            if tag_objects is False:
                args_container.log("Error: Couldn't get objects that contain the relevant tags")
                exit()
            Dispatcher(args_container, tag_objects)
            RemoveTag(tag, args_container)
        finally:
            LogoutManager(args_container, login_res.need_to_logout_from)
            print ("\nSummary:")
            print ("----------")
            failed_objects, all_objects_count = self.count_how_many_objects_wont_created(args_container)
            num_of_failed_objects = len(failed_objects)
            print("Failed to clone {} objects from total number of {}"
                  " objects".format(num_of_failed_objects, all_objects_count))
            print("The objects that were not cloned: {}".format(failed_objects))

    @staticmethod
    def collect_all_objects(args_container, tag_uid):
        """
        This function collects all the objects that contains the given tag
        :param args_container: contains the api client
        :param tag_uid: the uid of the relevant tag
        :return: list of all the objects
        """
        limit = 50  # each time get no more than 50 objects
        finished = False  # will become true after getting all the data
        all_objects = []  # accumulate all the objects from all the API calls
        iterations = 0
        command = "show-objects"
        container_key = "objects"
        # if given a string, make it a list
        payload = {"in": ["tags", tag_uid], "type": "object"}
        payload.update({"limit": limit, "offset": iterations * limit})
        api_res = args_container.local_client.api_call(command, payload)
        if container_key not in api_res.data or "total" not in api_res.data or api_res.data["total"] == 0:
            return

            # are we done?
        while not finished:
            # make the API call, offset should be increased by 'limit' with each iteration

            if api_res.success is False:
                return False

            total_objects = api_res.data["total"]  # total number of objects
            received_objects = api_res.data["to"]  # number of objects we got so far
            all_objects += api_res.data[container_key]

            # did we get all the objects that we're supposed to get
            if received_objects == total_objects:
                break

            iterations += 1
            payload.update({"limit": limit, "offset": iterations * limit})
            api_res = args_container.local_client.api_call(command, payload)

        return all_objects

    @staticmethod
    def count_how_many_objects_wont_created(args_container):
        """
        This function return list of object that wasn't cloned
        :return: set <List of the object that was't created , number of all the objects>
        """

        path_report = os.path.dirname(os.path.abspath(__file__)) + os.sep

        failed_objects = []
        count_all_objects = 0
        new_uid = 3
        original_name = 0
        is_header = True
        with open(path_report + 'clone_object_report_' + args_container.timestamp + '.csv') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                # skip the header
                if is_header is True:
                    is_header = False
                    continue
                count_all_objects += 1
                if not row[new_uid]:
                    failed_objects.append(row[original_name])

        return failed_objects, count_all_objects


if __name__ == "__main__":
    args = ArgsContainer(sys.argv[2:])
    LocalToGlobalByTag(sys.argv[1], args)
