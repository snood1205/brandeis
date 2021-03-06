# -*- coding: utf-8  -*-
# Brandeis - A tool to convert plaintext court cases (from the lochner
# tool: http://gitorious.org/lochner/) to wikitext.
# 
# Copyright (C) 2013 Molly White
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from bot.botparser import BotParser
from bot.scan import *


class Bot(object):
    """

    """

    def __init__(self, inputfile, output, metadict):
        self.inputfile = inputfile
        self.output = output
        self.metadict = metadict
        self.parser = BotParser(self.inputfile, self.output, self.metadict)

    def prepare(self):
        """Prepare file so the bot can upload it."""
        self.parser.prepare()
        if 'pdf' in self.metadict:
            self.metadict['pdf_filename'] = get_scan(self.inputfile, self.metadict['pdf'])
