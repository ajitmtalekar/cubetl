

import getopt
import logging
import os
import pprint
import sys
import traceback
import yaml

from cubetl import APP_NAME_VERSION
from cubetl.core import ContextProperties
from cubetl.core.context import Context
import cubetl


# Get an instance of a logger
logger = logging.getLogger(__name__)


class Bootstrap:

    def configure_logging(self, ctx):

        # In absence of file config
        default_level = logging.INFO if ctx.debug == False else logging.DEBUG
        #logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=default_level)
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=default_level)
        #logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

        #logging.basicConfig(
        #    level=logging.DEBUG,
        #    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        #    datefmt="%H:%M:%S", stream=sys.stdout)

        # With file config:
        #logging.config.fileConfig('logging.conf')

    def usage(self):
        print("cubetl [-dd] [-q] [-h] [-r filename] [-p property=value] [-i attribute=value] [config.yaml ...] <start-node>")
        print("")
        print("    -p   set a context property")
        print("    -i   set an attribute for the start item")
        print("    -d   debug mode (can be used twice for extra debug)")
        print("    -q   quiet mode (bypass print nodes)")
        print("    -r   profile execution writing results to filename")
        print("    -l   list config nodes ('cubetl.config.list' as start-node)")
        print("    -h   show this help and exit")
        print("    -v   print version and exit")
        print("")
        print("  Builtin entry points: ")
        print("      cubetl.config.list  Loads and prints configuration.")
        print("")

    def _split_keyvalue(self, text):
        """Return key=value pair, or key=None if format is incorrect
        """
        if (text.find('=') < 0):
            return (None, text)
        else:
            return (text[ : text.find('=')], text[text.find('=') + 1 : ])

    def parse_args(self, ctx):

        try:
            opts, arguments = getopt.gnu_getopt(ctx.argv, "p:m:r:dqhvl", [ "help", "version"])
        except getopt.GetoptError as err:
            print(str(err))
            self.usage()
            sys.exit(2)

        for o, a in opts:
            if o in ("-h", "--help"):
                self.usage()
                sys.exit(0)
            if o in ("-v", "--version"):
                print(APP_NAME_VERSION)
                sys.exit(0)
            if o == "-d":
                if (ctx.debug):
                    ctx.debug2 = True
                else:
                    ctx.debug = True
            elif o == "-q":
                ctx.quiet = True
            elif o == "-r":
                ctx.profile = a
            elif o == "-l":
                ctx.start_node = "cubetl.config.list"
            elif o == "-p":
                (key, value) = self._split_keyvalue(a)
                if (key == None):
                    print("Invalid property key=value definition (%s)" % (value))
                    self.usage()
                    sys.exit(2)
                logger.debug("Setting context property from command line: %s = %s" % (key, value))
                ctx.props[key] = value
            elif o == "-m":
                (key, value) = self._split_keyvalue(a)
                if (key == None):
                    print("Invalid attribute key=value definition (%s)" % (value))
                    self.usage()
                    sys.exit(2)
                logger.debug("Setting item attribute from command line: %s = %s" % (key, value))
                ctx.start_item[key] = value

        for argument in arguments:
            if (argument.endswith('.yaml')):
                ctx.config_files.append(argument)
            else:
                if (ctx.start_node == None):
                    ctx.start_node = argument
                else:
                    print("Only one start node can be specified (found: '%s', '%s')" % (ctx.start_node, argument))
                    self.usage()
                    sys.exit(2)

        if (ctx.start_node == None):
            print("One starting node must be specified, but none found.")
            self.usage()
            sys.exit(2)


    def init(self, argv=None, cli=False, debug=False):

        # Set up context
        ctx = Context()
        ctx.argv = argv
        ctx.cli = cli

        if not ctx.cli:
            ctx.argv = []
            ctx.start_node = "_dummy"

        # Set library dir
        # FIXME: Fix this so it works with setup.py/others installatiob
        base_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../../")
        ctx.props['dir_lib'] = base_dir + "/library"

        # Parse arguments
        self.parse_args(ctx)

        ctx.debug = debug

        # Init logging
        self.configure_logging(ctx)
        logger = logging.getLogger(__name__)
        logger.info("Starting %s" % cubetl.APP_NAME_VERSION)
        logger.debug("Debug logging level enabled")

        # TODO: Character encoding considerations? warnings?

        return ctx

    def start(self, argv):

        # Initialize context
        ctx = self.init(argv, cli=True)

        # Run
        ctx.run()

