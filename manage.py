import sys


if __name__ == "__main__":
    methods = {
        "create": ...,
        "drop": ...,
        "tests": ...
    }

    arguments = sys.argv
    if 2 > len(arguments) or arguments[1] not in methods:
        commands_list = ',\n'.join(methods.keys())
        sys.exit(f"Commands list:\n{commands_list};\nProcess Finished.")

    methods[arguments[1]](arguments)
