# -*- coding: utf-8 -*-
# @Date:   2017-12-08 13:44:34
# @Last Modified time: 2017-12-08 13:44:35
import six
import flask_restful
from flask import current_app
from flask_restful.reqparse import Namespace, Argument, RequestParser


class SsoArgument(Argument):

    def handle_validation_error(self, error, bundle_errors):
        """Called when an error is raised while parsing. Aborts the request
        with a 400 status and an error message

        :param error: the error that was raised
        :param bundle_errors: do not abort when first error occurs, return a
            dict with the name of the argument and the error message to be
            bundled
        """
        error_str = six.text_type(error)
        error_msg = self.help.format(error_msg=error_str) if self.help else error_str

        msg = {self.name: error_msg}

        if current_app.config.get("BUNDLE_ERRORS", False) or bundle_errors:
            return error, msg
        # TODO  modify this line
        # flask_restful.abort(400, message=msg)
        flask_restful.abort(400, msg=error_msg, status=0)


class SsoRequestParser(RequestParser):

    def __init__(self, trim=False, bundle_errors=False):
        super(SsoRequestParser, self).__init__(
            argument_class=SsoArgument,
            namespace_class=Namespace,
            trim=trim,
            bundle_errors=bundle_errors
        )
