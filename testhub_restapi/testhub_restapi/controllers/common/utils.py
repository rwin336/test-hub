import crypt
import json
import logging
import os
import pecan
import re
import yaml

import constants
import exception

logging = logging.getLogger(__name__)


class TestInfoDataNotFound(RestApiException):
    code = 404
    message = "TestInfoData data not Found"


class TestRequestDataNotFound(RestApiException):
    code = 404
    message = "TestRequestData data not Found"

