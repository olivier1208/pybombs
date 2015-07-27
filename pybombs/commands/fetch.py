#
# Copyright 2015 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#
""" PyBOMBS command: fetch """

from pybombs.commands import CommandBase
from pybombs import fetch
from pybombs import recipe

class Fetch(CommandBase):
    """ Fetch a package """
    cmds = {
        'fetch': 'Download a packages source code into the current prefixes source directory.',
        'refetch': 'Get a fresh download of a previously downloaded package',
    }

    @staticmethod
    def setup_subparser(parser, cmd=None):
        """
        Set up a subparser for a specific command
        """
        parser.add_argument(
                'packages',
                help="List of packages to fetch",
                action='append',
                default=[],
                nargs='*'
        )
        parser.add_argument(
                '-a', '--all',
                help="Fetch all packages. Warning: May take a while, and consume some considerable disk space",
                action='store_true',
        )
        parser.add_argument(
                '--deps',
                help="Also fetch dependencies of packages",
                action='store_true',
        )

    def __init__(self, cmd, args):
        CommandBase.__init__(self,
                cmd, args,
                load_recipes=True,
                require_prefix=True,
                require_inventory=True
        )
        self.args.packages = args.packages[0] # wat?
        if len(self.args.packages) == 0 and not args.all:
            self.log.error("No packages specified.")
            exit(1)
        if self.args.all:
            self.args.deps = False

    def run(self):
        """ Go, go, go! """
        recipe_list = []
        if self.args.all:
            self.log.debug("Loading all recipes!")
            self.args.packages = self.recipe_manager.list_all()
        try:
            self.log.debug("Getting recipes for: {}".format(self.args.packages))
            recipe_list = [recipe.Recipe(self.recipe_manager.get_recipe_filename(x)) for x in self.args.packages if len(x)]
        except KeyError as e:
            self.log.error("Unknown recipe: {}".format(e))
            exit(1)
        for r in recipe_list:
            if not len(r.srcs):
                self.log.debug("Package {} has no sources listed.".format(r.id))
                continue
            self.log.debug("Downloading {}".format(r.srcs[0]))
            fetcher = fetch.make_fetcher(r, r.srcs[0])
            fetcher.fetch(r, r.srcs[0])
            fetcher.get_version(r, r.srcs[0])
            self.inventory.set_state(r.id, 'fetch')
        self.inventory.save()
