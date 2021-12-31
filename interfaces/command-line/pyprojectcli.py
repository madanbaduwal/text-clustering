import fire


class SSECLI:
    def __init__(self):
        pass

    def add(self, a, b):
        print(f"receive {a} {b} from command line and sum is {a+b}")

    def sub(self, a, b):
        print(f"receive {a} {b} from command line and sub is {a-b}")

def main(): # IN entry point we only have to point function so we need to make function
    fire.Fire(SSECLI)


if __name__ == "__main__":
    main()

# Use
## From the root of project $ python -m interfaces.command-line.pyprojectcli add 2 2