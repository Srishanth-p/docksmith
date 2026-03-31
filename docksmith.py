import argparse
import sys

from builder.build_engine import build_image
from image.layer_system import list_images, remove_image
from runtime.container import run_container

# (runtime will be added later)


def interactive_shell():
    print("Docksmith Interactive CLI")
    print("Type 'exit' to quit\n")

    while True:
        cmd = input("docksmith> ").strip()

        if cmd == "exit":
            break

        parts = cmd.split()

        if not parts:
            continue

        command = parts[0]

        if command == "build":
            tag = parts[2]
            context = parts[3]
            build_image(tag, context)

        elif command == "images":
            list_images()

        elif command == "rmi":
            name, tag = parts[1].split(":")
            remove_image(name, tag)

        elif command == "run":
            if len(parts) < 2:
                print("Usage: run <image:tag>")
            elif ":" not in parts[1]:
                print("Error: Image must be in format name:tag")
            else:
                run_container(parts[1])

        else:
            print("Unknown command")

def main():
    import argparse

    parser = argparse.ArgumentParser(prog="docksmith")

    subparsers = parser.add_subparsers(dest="command")

    # BUILD
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("-t", "--tag", required=True)
    build_parser.add_argument("context")

    # IMAGES
    subparsers.add_parser("images")

    # REMOVE IMAGE
    rmi_parser = subparsers.add_parser("rmi")
    rmi_parser.add_argument("image")

    # RUN
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("image")

    args = parser.parse_args()

    # Import here to avoid circular issues
    from builder.build_engine import build_image
    from image.layer_system import list_images, remove_image
    from runtime.container import run_container

    if args.command == "build":
        build_image(args.tag, args.context)

    elif args.command == "images":
        list_images()

    elif args.command == "rmi":
        name, tag = args.image.split(":")
        remove_image(name, tag)

    elif args.command == "run":
        run_container(args.image)

    else:
        parser.print_help()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()              # command mode
    else:
        interactive_shell()  # interactive mode