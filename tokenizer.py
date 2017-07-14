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

import logging

import ply.lex as lex
from bexceptions import IllegalCharacter


class Tokenizer(object):
    # ===================================================================================================
    # TOKEN DECLARATIONS
    # ===================================================================================================
    """

    """
    tokens = (
        'IGNORED_TAG_CONTENT',  # For tags where we want to ignore the tags AND the content
        'IGNORED_TAG',  # Various tags we don't need to keep (content is preserved)
        'SOURCE',  # Source link and text added by lochner
        'BLOCKQUOTE',  # <blockquote>
        'E_BLOCKQUOTE',  # </blockquote>
        'SECTION',  # Repeated section name
        'B_PARAGRAPH',  # <p> in blockquote state
        'PARAGRAPH',  # <p>, </p>
        'LINK',  # <a> tags
        'COMMENT',  # <!-- comment -->
        'HEADER',  # <h1>, <h2>, etc.
        'HTML_ENTITY',  # &thing;
        'WHITESPACE',  # Tabs, spaces
        'SUPREMELINKS',  # <ul class="supremelinks">
        'CONSECUTIVE',  # <i></i>
        'ITALICS',  # <i>
        'BOLD',  # <b>
        'B_NEWLINE',  # Newline in blockquote state
        'NEWLINE',  # Newline
        'ABBR',  # Abbreviations that shouldn't be small caps
        'SMALLCAPS',  # ALL CAPS WORDS
        'ORDERED',  # "It is so ordered."
        'WORD',
        'NUMBER',
        'MULTI_APOSTROPHES',  # For '', ''' in the text
        'ASTERISKS',  # ***
        'PUNCTUATION',
        'UNKNOWN',  # For unknown characters that should be skipped
    )

    # ===================================================================================================
    # STATES
    # ===================================================================================================
    states = (
        ('blockquote', 'inclusive'),
    )

    def __init__(self, mdict):
        """Initiate logging, open a file to store tokens, build the lexer."""
        self.token_list = list()
        self.logger = logging.getLogger('brandeis')
        self.metadict = mdict
        self.lexer = lex.lex(module=self)

    # ===============================================================================
    # TOKEN DEFINITIONS
    # ===============================================================================
    @staticmethod
    def t_IGNORED_TAG_CONTENT(token):
        r"""<(script|SCRIPT|div\sclass\="disclaimer"|img)(.*?)>.*?<\/(div|script|SCRIPT|img)>"""
        return token

    @staticmethod
    def t_IGNORED_TAG(token):
        r"""<\/?(?P<tag>div|DIV|span|SPAN|hr|HR|L\=)(.*?)>"""
        token.value = token.lexer.lexmatch.group('tag')
        return token

    @staticmethod
    def t_CONSECUTIVE(token):
        r"""<\/i><i>"""
        return token

    @staticmethod
    def t_SOURCE(token):
        r"""Source\:\s(?P<source>http.*?\.html).*"""
        token.value = token.lexer.lexmatch.group('source')
        return token

    @staticmethod
    def t_BLOCKQUOTE(token):
        r"""<blockquote>"""
        token.lexer.begin('blockquote')  # Begin blockquote state
        return token

    @staticmethod
    def t_blockquote_E_BLOCKQUOTE(token):
        r"""<\/blockquote>"""
        token.lexer.begin('INITIAL')  # End blockquote state
        return token

    @staticmethod
    def t_SECTION(token):
        r"""(?<=<\/A><\/p><p>)(?P<name>Per\sCuriam)(?=<\/p>)"""
        token.value = token.lexer.lexmatch.group('name')
        return token

    @staticmethod
    def t_ORDERED(token):
        r"""<p>(<em>)?(?P<ordered>(?:It\sis\s)?[sS]o\sordered\.)(<\/em>)?<\/p>"""
        token.value = token.lexer.lexmatch.group('ordered')
        return token

    @staticmethod
    def t_blockquote_B_PARAGRAPH(token):
        r"""<(?P<end>\/?)[Pp](?P<info>.*?)>"""
        token.value = token.lexer.lexmatch.group('end', 'info')
        return token

    @staticmethod
    def t_PARAGRAPH(token):
        r"""<(?P<end>\/?)[Pp](?P<info>.*?)>"""
        token.value = token.lexer.lexmatch.group('end', 'info')
        return token

    @staticmethod
    def t_LINK(token):
        r"""\[?<[aA]\s(?P<info>.*?)>(?P<text>.*?)<\/[aA]>\]?"""
        token.value = token.lexer.lexmatch.group('info', 'text')
        return token

    @staticmethod
    def t_COMMENT(token):
        r"""<!--(.*?)-->"""
        return token

    @staticmethod
    def t_HEADER(token):
        r"""<[Hh](?P<level>[1-6])>(?P<content>.*?)<\/[Hh][1-6]>"""
        token.value = token.lexer.lexmatch.group('level', 'content')
        return token

    @staticmethod
    def t_HTML_ENTITY(token):
        r"""&(?P<entity>[a-zA-Z]+|\#[0-9]{3,4});"""
        token.value = token.lexer.lexmatch.group('entity')
        return token

    @staticmethod
    def t_SUPREMELINKS(token):
        r"""<(ul|UL)\s(class|CLASS)\="supremelinks">(?P<content>.*?)<\/(ul|UL)>"""
        token.value = token.lexer.lexmatch.group('content')
        return token

    @staticmethod
    def t_ITALICS(token):
        r"""(<\/?([Ii]|em|EM)>)+"""
        return token

    @staticmethod
    def t_BOLD(token):
        r"""<\/?(B|b|strong|STRONG)>"""
        return token

    @staticmethod
    def t_blockquote_B_NEWLINE(token):
        r"""(<[Bb][Rr]\s?\/?>)"""
        return token

    @staticmethod
    def t_NEWLINE(token):
        r"""(<[Bb][Rr]\s?\/?>)"""
        return token

    @staticmethod
    def t_ABBR(token):
        r"""(?<![A-Z])[A-Z]{1,4}(?![A-Z])"""
        return token

    @staticmethod
    def t_SMALLCAPS(token):
        r"""((?:[A-Z]{2,}\.?\s?)+|[A-Z]+,\s[A-Z]\.)+(?=[\W])"""
        return token

    @staticmethod
    def t_WHITESPACE(token):
        r"""\s"""
        return token

    @staticmethod
    def t_WORD(token):
        r"""[a-zA-z]+"""
        return token

    @staticmethod
    def t_NUMBER(token):
        r"""[0-9]+"""
        return token

    @staticmethod
    def t_MULTI_APOSTROPHES(token):
        r"""'{2,3}"""
        return token

    @staticmethod
    def t_ASTERISKS(token):
        r"""\*{3}"""
        return token

    @staticmethod
    def t_PUNCTUATION(token):
        r"""[!@\#\$\%\^&\*\(\)\-;\+=\[\]\{\}\\\|\:;"',\.\?~°–—/±]"""
        return token

    @staticmethod
    def t_UNKNOWN(token):
        r"""�"""
        return token

    # ===============================================================================
    # ERROR HANDLING
    # ===============================================================================
    @staticmethod
    def t_ANY_error(token):
        """

            :param token:
            """
        token.lexer.skip(1)
        raise IllegalCharacter(token.lexpos)

    def analyze(self, data):
        """Read through the text file and tokenize."""
        self.lexer.input(data)
        with open('tokenout.txt', 'w+', encoding='utf-8') as tokenfile:
            while True:
                token = self.lexer.token()
                # print(token)
                if not token:
                    break  # No more input
                l_token = [token.type, token.value]
                self.token_list.append(l_token)
                tokenfile.write(str(token) + '\n')
        return self.token_list
