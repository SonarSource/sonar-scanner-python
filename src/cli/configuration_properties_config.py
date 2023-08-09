import argparse
import sys

from cli.context import Context


class ConfigurationPropertiesConfig:
    def setup(self, ctx: Context):
        """ This is executed when run from the command line """
        parser = argparse.ArgumentParser()

        # Required positional argument
        parser.add_argument("arg", help="Required positional argument")

        # Optional argument flag which defaults to False
        parser.add_argument("-f", "--flag", action="store_true", default=False)

        # Optional argument which requires a parameter (eg. -d test)
        parser.add_argument("-n", "--name", action="store", dest="name")

        # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
        parser.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=0,
            help="Verbosity (-v, -vv, etc)")

        # Specify output of "--version"
        # parser.add_argument(
        #     "--version",
        #     action="version",
        #     version="%(prog)s (version {version})".format(version=__version__))

        # args = parser.parse_args()

        ctx.sonar_scanner_version = '4.6.2.2472'
        ctx.sonar_scanner_path = '.scanner'

        scan_arguments = []
        for arg in sys.argv:
            if arg.startswith("-D"):
                scan_arguments.append(arg)
        ctx.scan_arguments = scan_arguments
