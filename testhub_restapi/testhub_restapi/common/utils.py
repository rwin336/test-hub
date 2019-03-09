import crypt
import json
import logging
import os
import pecan
import re
import yaml

import constants
import exception

logginr = logging.getLogger(__name__)



def _get_err(error_type, op_name, err_msg=""):
    """
    This function is for Raising Exception for REST API.
    It has 2 error_type:
       - raise: Used when REST API is exposed as wsme_pecan.wsexpose
       - json: Used when REST API is exposed as pecan.expose('json')
    """
    if not err_msg:
        err_msg = "{} Operation is already in progress. Please try " \
                  "after sometime.".format(op_name)

    logging.error(err_msg)
    if error_type == "raise":
        restapi_exception = exception.RestApiException()
        restapi_exception.message = err_msg
        restapi_exception.code = 409
        raise restapi_exception
    else:
        error_json = {"debuginfo": "", "faultcode": "Client",
                      "faultstring": err_msg}
        return pecan.Response(json.dumps(error_json), 409,
                              content_type='application/json')

