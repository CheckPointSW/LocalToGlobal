from args_container import ArgsContainer
from local_to_global_by_tag import LocalToGlobalByTag


def main():
    tag_name = "toGlobal"
    args = ArgsContainer()
    args.build(server="172.23.78.47", username="aa", local_domain="domain1", prefix="pre", global_domain="Global")
    LocalToGlobalByTag(tag_name, args)


if __name__ == "__main__":
    main()
