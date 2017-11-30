import xmltodict

from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser

class XmlParser(BaseParser):

    media_type = 'application/xml'

    def parse(self, stream, media_type=None, parser_context=None):
        try:
            data = xmltodict.parse(stream)
            data['original'] = xmltodict.unparse(data)
            return data
        except Exception as e:
            raise ParseError('Xml parsing error: ' + e.message)