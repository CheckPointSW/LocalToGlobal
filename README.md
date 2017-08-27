# LocalToGlobal
Check Point LocalToGlobal tool enables you to copy object from a local domain to the global domain.

## Instructions
Each object type has a different script 'local_<object type>_to_global.py', responsible for cloning that object.

If the object's type is unknown, use the script 'local_object_to_global.py' with '-o' flag and provide the object's UID value. 

## Development Environment
The tool is developed using Python language version 2.7.9 and Check Point API Python SDK.
