# LocalToGlobal
Check Point LocalToGlobal tool enables you to copy objects from a local domain to the global domain.

## Instructions
For copying an object, which type is known, run the script:

'local_[object type]_to_global.py' -o <object uid>

For copying an object, which type is unknown, run the script:

'local_object_to_global.py' -o <object uid>

For copying multiple objects, these objects need to be tagged using Check Point SmartConsole application or 'add-tag' API command, and then run the script:

'local_global_by_tag.py' <tag name>


Additional Flags

The following flags are mandatory:

-d <local domain name> : the local domain name that contains the object that need to be copied

-n <prefix> : the new global object name will be created in the following format - prefix_<local_object_name>

If the scripts are not run on Check Point Management server, the following flags are mandatory:

-s <server IP address> : the IP address or name of Check Point Management Server

-u <user name>

The following flags are optional:

-p <port number> : the default value is 443

-g <>global domain name> : the default value is 'Global'

## Notes

## Development Environment
The tool is developed using Python language version 2.7.9 and Check Point API Python SDK.
