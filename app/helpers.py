# -*- coding: utf-8 -*-
"""
    app.helpers
    ~~~~~~~~~~~~

    Set of used utility functions

"""

import re
from collections import namedtuple

#Interesting mail headers by categories in the descending order
#from the point of view of more strict correspondence of
#requirements.
SNDR_HDRS = ['From:', 'Sender:', 'Originator:', 'Return-Path:']
SUBJ_HDRS = ['Subject:', 'Keywords:', 'Comments:', 'Summary:']
DATE_HDRS = ['Date:', 'Delivery-Date:', 'Received:']

def _parse_header(header, keys):
    """Internal helper function for parse_header() call"""
    for entry in header:
        regexes = [ re.compile(pattern + " *(.*$)") for pattern in keys ]
        for regex in regexes:
            match = regex.search(entry)
            if match:
                return match.group(1)

def parse_header(msgid, header, odd):
    """Helper function, which return named tuple of three fields,
    ('sender', 'subject', 'date'), from received header.
    """
    _sender = _parse_header(header, SNDR_HDRS)
    _subject = _parse_header(header, SUBJ_HDRS)
    _date = _parse_header(header, DATE_HDRS)
    regex = re.compile("\(.*\); *(.*$)")
    _found = regex.search(_date)
    if _found and _found.group(1):
        _date = _found.group(1)

    _headinfo = namedtuple('_headinfo', 'msgid, odd, sender, subject, date')
    return _headinfo(msgid=msgid, odd=odd,sender=_sender,
                     subject=_subject, date=_date)


PINFO_APP_ERROR = 1001
PINFO_APP_VALIDATOR_ERROR = 1002
PINFO_APP_RECORD_ERROR = 1003
PINFO_DOES_NOT_EXIST = 1004
PINFO_ALREADY_EXISTS = 1005
PINFO_FIELD_TOO_LONG = 1006
PINFO_USER_NOT_SET = 1008
PINFO_PASS_NOT_SET = 1009
PINFO_HOST_NOT_SET = 1010

STATUS_DESC = {
    PINFO_APP_ERROR: "Contact information base error",
    PINFO_APP_VALIDATOR_ERROR: "Contact information validation error",
    PINFO_APP_RECORD_ERROR: "Contact information retrieving error",
    PINFO_DOES_NOT_EXIST: "Contact information is absent",
    PINFO_ALREADY_EXISTS: "Such entry already exists",
    PINFO_FIELD_TOO_LONG: "Set field is too long",
    PINFO_USER_NOT_SET: "Obligatory LIMIT parameter is absent in request",
    PINFO_PASS_NOT_SET: "Obligatory NAME parameter is absent in request",
    PINFO_HOST_NOT_SET: "Obligatory SURNAME parameter is absent in request",
}


class PInfoBaseError(Exception):
    """Base class for all custom application errors."""
    code = PINFO_APP_ERROR


class PInfoValidationError(PInfoBaseError):
    """Contact information validation error"""
    code = PINFO_APP_VALIDATOR_ERROR


class AccountRecordError(PInfoBaseError):
    """POP3 account information retrieving error"""
    code = PINFO_APP_RECORD_ERROR


class AccountDoesNotExist(AccountRecordError):
    """POP3 account information is absent"""
    code = PINFO_DOES_NOT_EXIST


class AccountAlreadyExists(AccountRecordError):
    """Such entry already exists"""
    code = PINFO_ALREADY_EXISTS


class AccountFieldIsTooLong(AccountRecordError):
    """POP3 account information sield is too long"""
    code = PINFO_FIELD_TOO_LONG


class PinfoLimitNotSet(PInfoValidationError):
    """Obligatory LIMIT parameter is absent in request"""
    code = PINFO_USER_NOT_SET


class PinfoNameNotSet(PInfoValidationError):
    """Obligatory NAME parameter is absent in request"""
    code = PINFO_PASS_NOT_SET


class PinfoSurnameNotSet(PInfoValidationError):
    """Obligatory SURNAME parameter is absent in request"""
    code = PINFO_HOST_NOT_SET
