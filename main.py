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

FILE_INCLUDE_HEADER = "# INCLUDED FROM"
INCLUDE = "INCLUDE"

class Directive:
    instances = 0
    source_file = ""
    directive = ""
    directive_args = []
    parent = None

    def __init__(self, source_file, line, parent=None):
        self.source_file = source_file
        (self.directive, self.directive_args) = line.split(None, 1) # Split once to get directive and args (none means to use default whitespace delimiter)
        self.parent = parent

    def __str__(self):
        return self.directive
    
def read_config(config_dir, server_config_file):
    config = path.join(config_dir, server_config_file)
    if server_config_file.startswith("/"):
        # Absolute path
        config = server_config_file

    config_lines = []

    for fpath in iglob(config):
        config_lines.append(f"{FILE_INCLUDE_HEADER}: {fpath}")
        try:
            with open(fpath, 'r') as f:
                for line in f.readlines():
                    line_stripped = line.strip().rstrip('\n')
                    if line_stripped.startswith('#') or len(line_stripped) == 0:
                        # Ignore lines that start with a #, like this one :|  Also empty lines. Why are you still reading this?
                        continue
                    else:
                        line_stripped_ucase = line_stripped.upper()
                        if line_stripped_ucase.startswith(INCLUDE):
                            (directive, args) = line_stripped.split(None, 1)
                            args_noquotes = args.strip('"\'')
                            config_path = args_noquotes
                            config_lines.extend(read_config(config_dir, config_path))
                        else:
                            config_lines.append(line_stripped)

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

def parse_config(config_list):
    from_file = ""
    parent = None
    d = None
    directives = []
    
    # Iterate over each line from the parsed config
    for line in config_list:
        # Grep our custom file include directive so we know which file this came from
        if line.startswith(FILE_INCLUDE_HEADER):
            # We want to split on ':' for this line, only have 1 match, and strip leading/trailing spaces
            (_, from_file) = line.split(':', 1)
            # Then set from_file so we can use it when parsing subsequent directives
            from_file = from_file.strip()
            # Then move on to the next line, no more parsing needed
            continue
        elif line.startswith("<"):
            if line.startswith("</"):
                # This is a closing directive, it should match parent's directive
                # Yo dawg....
                parent = parent.parent
            else:
                # This is a new parent
                d = Directive(from_file, line.strip("<>"), parent)
                # Update reference to current parent
                parent = d
                # Stop processing and move on
                #continue
        else:
            # Parse this line, and assign it to parent (if any)
            d = Directive(from_file, line, parent)
        
        # Add the directive to the list....?
        directives.append(d)
    
    return directives

def main():
    # This script assumes the config is syntactically correct, though doesn't cover every single nuance (e.g. line-continuations with '\')
    #   If you want to know if the config's syntax is correct, run apachectl -t. I could do it for you, but I'm not gonna. Unless you ask nicely. With Bitcoin.
    # You might have noticed I'm using recursion to parse Include directives. If you have a circular include, there are no brakes.
    #   Seriously, check syntax before you begin. Or send more Bitcoin.

    parser = argparse.ArgumentParser()
    parser.add_argument("--config_dir", help="location of Apache config dir (default: HTTPD_ROOT=/etc/httpd)", default="/etc/httpd", type=str)
    parser.add_argument("--server_config_file", help="relative path to Apache config file (default: SERVER_CONFIG_FILE=conf/httd.conf)", default="conf/httpd.conf", type=str)
    args = parser.parse_args()

    lines = read_config(args.config_dir, args.server_config_file)

    #print('\n'.join(lines))

    directives = parse_config(lines)

    return 0

if __name__ == '__main__':
    main()