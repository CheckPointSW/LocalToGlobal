# LocalToGlobal
Check Point LocalToGlobal tool enables you to copy objects from a local domain to the global domain.

## Instructions
For copying an object, which type is known, run the script:

'local_[object type]_to_global.py' -o [object uid]

For copying an object, which type is unknown, run the script:

'local_object_to_global.py' -o [object uid]

For copying multiple objects, these objects need to be tagged using Check Point SmartConsole application or 'add-tag' Check Point Management CLI command, and then run the script:

'local_to_global_by_tag.py' [tag name]

### Additional Flags
The following flags are mandatory:

-d [local domain name] : the local domain name that contains the object that needs to be copied

-n [prefix] : the new global object name will be created in the following format - prefix_[local_object_name]

If the scripts are not run on Check Point Management server, the following flags are mandatory:

-s [server IP address] : the IP address or name of Check Point Management server

-u [user name] : for authentication

The following flags are optional:

-p [port number] : the default value is 443

-g [global domain name] : the default value is 'Global'

### The scripts create the following output files:
1. json_objects.json - contains a list of {[original object uid] : [cloned global object uid]}

2. csv_file.csv - contains a list of {[original object uid], [original object name], [cloned global object name], [cloned global object uid]}

If a global object is not created, the [cloned global object name] [cloned global object uid] will remain empty.

### Notes
1. Here is the list of 'known' object types - host, network, address range, network group, tcp service, udp service, service group.

2. If a group object is copied, the script will also copy all group member objects.

3. If an object contains a 'nat-settings' field, this field is not copied.

## Development Environment
The tool is developed using Python language version 2.7.9 and [Check Point API Python SDK.](https://github.com/CheckPoint-APIs-Team/cpapi-python-sdk)
