#!/usr/local/bin/python3

import argparse
from os import path
from glob import iglob

#from enum import Enum

# class DirectiveType(Enum):
#     SERVERROOT = auto()
#     LISTEN = auto()
#     LOADMODULE = auto()
#     USER = auto()
#     GROUP = auto()
#     SERVERADMIN = auto()
#     SERVERNAME = auto()
#     DIRECTORY = auto()
#     DOCUMENTROOT = auto()
#     IFMODULE = auto()
#     FILES = auto()
#     ERRORLOG = auto()
#     LOGLEVEL = auto()
#     ADDDEFAULTCHARSET = auto()

# class DirectiveSubType(Enum):
#     ALLOWOVERRIDE = auto()
#     REQUIRE = auto()

INCLUDE = "INCLUDE"

class Directive:
    source_file = ""
    directive = ""
    directive_args = []
    parent = None

    def __init__(self, source_file, line, parent=None):
        self.source_file = source_file
        (self.directive, self.directive_args) = line.split(None, 1) # Split once to get directive and args (none means to use default whitespace delimiter)
        self.parent = parent

def read_config(config_dir, server_config_file):
    config = path.join(config_dir, server_config_file)
    if server_config_file.startswith("/"):
        # Absolute path
        config = server_config_file

    config_lines = []

    for fpath in iglob(config):
        try:
            with open(fpath, 'r') as f:
                for line in f.readlines():
                    line_stripped = line.strip()
                    if line_stripped.startswith('#') or len(line_stripped) == 0:
                        # Ignore lines that start with a #, like this one :|  Also empty lines. Why are you still reading this?
                        continue
                    else:
                        line_ucase = line_stripped.upper()
                        if line_ucase.startswith(INCLUDE):
                            (directive, args) = line.split(None, 1)
                            args_noquotes = args.strip('"\'')
                            config_path = args_noquotes
                            config_lines.append(read_config(config_dir, config_path))
                        else:
                            config_lines.append(line)

        except IOError:
            print(f"Error reading config file: {config}.")
            return []

                # elif line.strip().startswith('<'):
                #     if line.strip().startswith('</'):
                #         if tag_level < 1:
                #             raise SyntaxError(f"Found close tag when none open ({config}).")
                #         else:
                #             tag_level -= 1
                #             # Close the current directive
                # else:
                #     new_directive = Directive(config, line.strip(), new_directive)

    return config_lines

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_dir", help="location of Apache config dir (default: HTTPD_ROOT=/etc/httpd)", default="/etc/httpd", type=str)
    parser.add_argument("--server_config_file", help="relative path to Apache config file (default: SERVER_CONFIG_FILE=conf/httd.conf)", default="conf/httpd.conf", type=str)
    args = parser.parse_args()

    read_config(args.config_dir, args.server_config_file)




if __name__ == '__main__':
    main()