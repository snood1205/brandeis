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

import logging, re

class Parser(object):
    '''The parser converts the raw case text from lochner to a dictionary object. This is later
    converted to wikitext to be uploaded.'''
    
    def __init__(self, metadict):
        self.logger = logging.getLogger('brandeis')
        self.output = None
        self.metadict = metadict

    def parse(self, tokens, output_file):
        '''Run the parser functions on the file.'''
        if output_file:
            self.output = output_file
        self.tokens = tokens
        self.dispatch()
        
    def dispatch(self):
        for token in self.tokens:
            self.value = token[1]
            if self.value:
                command = 'self.{0}()'.format(token[0].lower())
                try:
                    exec(command)
                except AttributeError as e:
                    self.logger.error("No command for " + command + ". " + repr(e));
                    break;
                except Exception as e:
                    self.logger.error("Exception while parsing: " + repr(e));
                    break;
                else:
                    self.write(self.value)
    
    def write(self, text):
        if type(text) is str:
            if self.output:
                self.output.write(text)
                
            
#===================================================================================================
# PARSING FUNCTIONS
#===================================================================================================
    def javascript(self, value=None):
        # Don't want any of the JavaScript
        self.value = ''
        return self.value
    
    def ignored_tag(self, value=None):
        # Don't want these tags in the output.
        self.value = ''
        return self.value
        
    def link(self, value=None):
        # Extract necessary information to determine if they should be kept
        value = value if value else self.value
        info = value[0]
        text = value[1]
        m_class = re.search(r'class\="(?P<class>.*?)"', info)
        if m_class:
            link_class = m_class.group('class')
            if link_class == 'page-name':
                self.value = '\nPAGE ' + text + '\n'
                return self.value
        else:
            m_href = re.search(r'href\="(?P<href>.*?)"', info)
            if m_href:
                href = m_href.group('href')
                if '/cases/federal/us/' in href:
                    self.value = text
                    return self.value
        self.value = ''
        return self.value
        
    def comment(self, value=None):
        # Don't want comments in the output.
        self.value = ''
        return self.value
    
    def title(self, value=None):
        # This will be added from the metadict
        self.value = ''
        return self.value
    
    def newline(self, value=None):
        # Newlines should be preserved. Extraneous ones will be removed in post-processing.
        self.value = '\n'
        return self.value
    
    def supremelinks(self, value=None):
        # List of sections. Shouldn't be added to text, but should be preserved in metadict.
        self.metadict['sections'] = []
        content = value if value else self.value
        content = re.sub(r'\s', '', content)
        strings = re.findall(r'(?<=>)(.*?)(?=<)', content)
        for string in strings:
            if len(string) > 0:
                self.metadict['sections'].append(string)
        self.value = ''
        return self.value
    
def strip_extraneous(content):
    match = re.search(r'<article\sid\="maincontent">(?P<content>.*?)<\/article>.*?<\/html>(?P<source>.*)',
                      content, flags = re.DOTALL)
    if (match):
        return match.group('content') + match.group('source')
    else:
        return None
    
def get_metadata(metadict, filename):
    '''Pull the title from the file.'''
    with open(filename, 'r', encoding='utf-8') as file:
        while True:
            first_line = file.readline()
            match = re.match(r'^[\n\s\t\r]+$', first_line, re.MULTILINE)
            if not match:
                break
    title = re.match(r'[\s\t]*<h1>(?P<full>(?P<title>(?P<petitioner>.*?)\sv\.\s(?P<respondent>.*?))\s\-\s(?P<number>(?P<volume>\d{1,3})\s(?P<abbr>U.S.)\s(?P<page>\d{1,3}))\s\((?P<date>\d{4})\))</h1>', first_line)
    metadict["full_title"] = title.group("full")
    metadict["title"] = title.group("title")
    metadict["petitioner"] = title.group("petitioner")
    metadict["respondent"] = title.group("respondent")
    metadict["number"] = title.group("number")
    metadict["volume"] = title.group("volume")
    metadict["title"] = title.group("title")
    metadict["abbr"] = title.group("abbr")
    metadict["page"] = title.group("page")
    metadict["date"] = title.group("date")
