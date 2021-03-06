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

from caseparser import Parser
from bexceptions import *
import unittest


class TestParser(unittest.TestCase):
    """Test tokenizer module."""

    def setUp(self):
        self.test_dict = {'respondent': 'Person 2',
                          'abbr': 'U.S.',
                          'petitioner': 'Person 1',
                          'volume': '111',
                          'number': '1 U.S. 111',
                          'page': '111',
                          'title': 'Person One v. Person Two',
                          'date': '2000',
                          'full_title': 'Person One v. Person Two - 1 U.S. 111 (2000)'}
        self.parser = Parser(self.test_dict)

    def testGoodLink(self):
        token = ('href="/cases/federal/us/531/98/"', 'Syllabus')
        self.assertEqual(self.parser.link(token), 'Syllabus',
                         'Parser failed to extract text from a good link.')

    def testBadLink(self):
        token = ('href="http://addthis.com/"', 'Spam')
        self.assertEqual(self.parser.link(token), '',
                         'Parser did not return empty string for a bad link.')

    def testGoodEntity(self):
        content = 'quot'
        self.assertEqual(self.parser.html_entity(content), '"', 'HTML entity gave incorrect value.')

    def testBadEntity(self):
        content = 'foo'
        self.assertRaises(EntityError, self.parser.html_entity, content)

    def testSmallCaps(self):
        content = "FOO"
        self.assertEqual(self.parser.smallcaps(content), "{{sc|Foo}}",
                         "Incorrect value returned from small caps parser.")


if __name__ == '__main__':
    unittest.main()
