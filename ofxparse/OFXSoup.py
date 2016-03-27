#-------------------------------------------------------------------------------
# Name:        OFXSoup
# Purpose:
#
# Author:      rdsteed
#
# Created:     01/02/2016
# Copyright:   (c) rdsteed 2016
# Licence:     MIT
#-------------------------------------------------------------------------------
import bs4 as _bs4
from bs4 import BeautifulSoup
# Extends Beautiful Soup's builder for the built in htmlparser
# by adding/spoofing omitted closing tags in OFX/QFX files.
# OFX/QFX files are downloadable financial files for Quicken & other financial
# software.
# Based on the observation that the tags with optional closing all contain data.
# Alternative would be to try to extract them from the OFX DTD.
# This seems to work though.
# Note:  White space only in a tag is not data.

class _BeautifulSoupOFXParser(_bs4.builder._htmlparser.BeautifulSoupHTMLParser):

  def handle_starttag(self, name, attrs):
    # If not root & there is data in the current tag, want to spoof an end tag
    if ((self.soup.currentTag.name != '[document]') and
              u''.join(self.soup.current_data).strip()):
        self.handle_endtag(self.soup.currentTag.name)
    # Then pass along start tag to parent handler
    _bs4.builder._htmlparser.BeautifulSoupHTMLParser.handle_starttag(self, name, attrs)

  def handle_endtag(self,name):
    # If the endtag does not match current tag, want to spoof an end tag
    if self.soup.currentTag.name != name:
        self.handle_endtag(self.soup.currentTag.name)
    # Then pass along end tag to parent handler
    _bs4.builder._htmlparser.BeautifulSoupHTMLParser.handle_endtag(self, name)


class OFXParserTreeBuilder(_bs4.builder._htmlparser.HTMLParserTreeBuilder):
    def feed(self, markup):
        args, kwargs = self.parser_args
        # builder must use OFX parser
        parser = _BeautifulSoupOFXParser(*args, **kwargs)
        parser.soup = self.soup
        parser.feed(markup)
