# -*- coding: utf-8 -*-
# @Date:   2018-03-12 15:48:38
# @Last Modified time: 2018-03-12 15:50:36
import re
import time
import random
import datetime
from flask import session, request, current_app
from flask_restful import Resource
from flask_login import current_user, login_user, logout_user
from utils import Password
from patches import json_resp, SsoRequestParser
from common import Mail
from models.sso import User as U


class AuthResource(Resource):

    def __init__(self):
        self.email = None
        self.mobile = None
        self.error_msg = None

    def account_available(self):
        config = current_app.config
        if not self.mobile and not self.email:
            self.error_msg = "empty mobile and email error"
            return False
        if self.email and not re.match(config.get("EMAIL_REGEX"), self.email):
            self.error_msg = "incorrect email format error"
            return False
        if self.mobile and not re.match(config.get("MOBILE_REGEX"), self.mobile):
            self.error_msg = "incorrect mobile format error"
            return False
        return True

    def is_accessible(self):
        if not current_user.is_authenticated:
            self.error_msg = "user has not logged error"
            return False
        return True


class User(AuthResource):

    def __init__(self):
        super(User, self).__init__()
        self.parser = SsoRequestParser()
        self.parser.add_argument(
            "mobile", type=int, default=0, help="mobile error", location=["values", "json"]
        )
        self.parser.add_argument(
            "email", type=str, default="", help="email error", location=["values", "json"]
        )
        self.parser.add_argument(
            "verificationCode", type=int, required=True, help="verificationCode error",
            location=["values", "json"]
        )
        self.parser.add_argument(
            "password", type=str, required=True, help="password error", location=["values", "json"]
        )

    def verify_code(self, verification_code):
        config = current_app.config
        assert self.email or self.mobile

        _email = session.get("email")
        _mobile = session.get("mobile")

        if self.email != _email and self.mobile != _mobile:
            self.error_msg = "user account mismatching error"
            return False

        if time.time() < session.get("last_verification_code_expired"):
            self.error_msg = "verification code expired error"
            return False

        if verification_code != session.get("verification_code"):

            _test_verification_code_failed = int(session.get("test_verification_code_failed"))
            if _test_verification_code_failed < config.get("TEST_VERIFICATION_CODE_FAILED"):
                session.update({"test_verification_code_failed": _test_verification_code_failed + 1})
            else:
                session.update({
                    "test_verification_code_failed": 0,
                    "account_frozen_before": time.time() + config.get("ACCOUNT_FROZEN_BEFORE")
                })

            self.error_msg = "verification code mismatching error"
            return False

        # session.clear()
        return True

    def get(self):
        """
        @api {get} /user  get user info
        @apiVersion 1.0.0
        @apiName User.get
        @apiGroup User

        @apiSuccess  {number}    code          返回码（0：失败，1：成功）
        @apiSuccess  {string}    msg           返回消息
        @apiSuccess  {string}    userInfo      返回数据
        """
        if not self.is_accessible():
            return json_resp(msg=self.error_msg)
        return json_resp(status=1, msg="success", userInfo=current_user.get_dict())

    def put(self):
        """
        @api {put} /user  reset password
        @apiVersion 1.0.0
        @apiName User.put
        @apiGroup User

        @apiParam  {number}    mobile               user's mobile
        @apiParam  {String}    email                user's email
        @apiParam  {String}    password             user's password
        @apiParam  {number}    verificationCode     verification code

        @apiSuccess  {number}    code       返回码（0：失败，1：成功）
        @apiSuccess  {string}    msg        返回消息
        """
        parser = self.parser.copy()
        args = parser.parse_args()
        email = args.get("email")
        mobile = args.get("mobile")
        password = args.get("password")
        verification_code = args.get("verificationCode")

        self.email, self.mobile = email, mobile

        if not self.account_available():
            return json_resp(msg=self.error_msg)

        if not self.verify_code(verification_code):
            return json_resp(msg=self.error_msg)

        if not U.update(password=password).where(
            U.mobile == mobile, U.email == email, U.status == 1
        ).execute():
            return json_resp(msg="user is not registered error")

        return json_resp(status=1, msg="success")

    def post(self):
        """
        @api {post} /user  register
        @apiVersion 1.0.0
        @apiName User.post
        @apiGroup User

        @apiParam  {number}    mobile                user's mobile
        @apiParam  {String}    email                 user's email
        @apiParam  {String}    password              user's password
        @apiParam  {number}    verificationCode      verification code

        @apiSuccess  {number}    code       返回码（0：失败，1：成功）
        @apiSuccess  {string}    msg        返回消息
        """
        parser = self.parser.copy()
        args = parser.parse_args()
        email = args.get("email")
        mobile = args.get("mobile")
        password = args.get("password")
        verification_code = args.get("verificationCode")

        self.email, self.mobile = email, mobile

        if not self.account_available():
            return json_resp(msg=self.error_msg)

        if not self.verify_code(verification_code):
            return json_resp(msg=self.error_msg)

        ip = request.remote_addr
        if not U.create(
                mobile=mobile, email=email, password=password,
                status=1, createIp=ip, createAt=datetime.datetime.now()
        ):
            return json_resp(msg="account has been registered error")

        return json_resp(status=1, msg="success")


class VerificationCode(AuthResource):

    def send_code(self):
        config = current_app.config
        assert self.email or self.mobile
        verification_code = random.randint(100000, 999999)

        _email, _mobile = session.get("email"), session.get("mobile")
        if self.email == _email and self.mobile == _mobile:

            _frozen_before = session.get("frozen_before")
            if _frozen_before and _frozen_before > time.time():
                self.error_msg = "user account is frozen 1 hour"
                return False

            _last_expired = session.get("last_expired")
            if _last_expired and _last_expired > time.time():
                self.error_msg = "please try 1 minute interval"
                return False
        else:
            session.update({
                "email": self.email,
                "mobile": self.mobile,
                "verification_code": 0,
                "test_verification_code_failed": 0,
                "send_verification_code_success": 0,
                "last_verification_code_expired": 0,
                "account_frozen_before": 0
            })
        if self.email:
            result = Mail.send_verification_code(to_list=[self.email], code=verification_code)
        else:
            result = None
        if not result:
            self.error_msg = "user account error"
            return False

        session.update({
            "verification_code": verification_code,
            "last_verification_code_expired": time.time() + config.get("LAST_VERIFICATION_CODE_EXPIRED")
        })

        _send_verification_code_success = int(session.get("send_verification_code_success"))
        if _send_verification_code_success < config.get("SEND_VERIFICATION_CODE_SUCCESS"):
            session.update({"send_verification_code_success": _send_verification_code_success + 1})
        else:
            session.update({
                "send_verification_code_success": 0,
                "account_frozen_before": time.time() + config.get("ACCOUNT_FROZEN_BEFORE"),
            })
        return True

    def get(self):
        """
        @api {get} /verification/code
        @apiVersion 1.0.0
        @apiName VerificationCode.get
        @apiGroup VerificationCode

        @apiParam  {number}    mobile         user's mobile
        @apiParam  {String}    email          user's email
        @apiParam  {String}    status         user's status（0：注册，1：修改密码）

        @apiSuccess  {number}    code    返回码（0：失败，1：成功）
        @apiSuccess  {string}    msg     返回消息
        """
        parser = SsoRequestParser()
        parser.add_argument(
            "mobile", type=int, default=0, ignore=False,
            case_sensitive=True, help="mobile error", location=["values", "json"]
        )
        parser.add_argument(
            "email", type=str, default="", ignore=False,
            case_sensitive=True, help="email error", location=["values", "json"]
        )
        parser.add_argument(
            "status", type=int, required=True, choices=[0, 1],
            ignore=False, case_sensitive=True, store_missing=False,
            help="status error", location=["values", "json"]
        )

        args = parser.parse_args(strict=True)
        email = args.get("email")
        mobile = args.get("mobile")
        status = args.get("status")

        self.email, self.mobile = email, mobile
        if not self.account_available():
            return json_resp(msg=self.error_msg)

        u = U.better_get(U.mobile == mobile, U.email == email, U.status == 1)
        if u and status == 0:
            return json_resp(msg="account has been registered error")
        if not u and status == 1:
            return json_resp(msg="user hasn't been registered error")

        if not self.send_code():
            return json_resp(msg=self.error_msg)

        # u = filter(lambda u: u.status == status, u) if u else u
        return json_resp(status=1, msg="success")


class Session(AuthResource):

    def delete(self):
        """
        @api {delete} /session  logout
        @apiVersion 1.0.0
        @apiName Session.delete
        @apiGroup Session

        @apiSuccess  {number}    code    返回码（0：失败，1：成功）
        @apiSuccess  {string}    msg     返回消息
        """
        logout_user()
        return json_resp(status=1, msg="success")

    def post(self):
        """
        @api {post} /session  login
        @apiVersion 1.0.0
        @apiName Session.post
        @apiGroup Session

        @apiParam  {number}    mobile         user's mobile
        @apiParam  {String}    email          user's email
        @apiParam  {String}    password       user's password

        @apiSuccess  {number}    code    返回码（0：失败，1：成功）
        @apiSuccess  {string}    msg     返回消息
        """
        parser = SsoRequestParser()
        parser.add_argument(
            "mobile", type=int, default=0, help="mobile error", location=["values", "json"]
        )
        parser.add_argument(
            "email", type=str, default="", help="email error", location=["values", "json"]
        )
        parser.add_argument(
            "password", type=str, required=True, help="password error", location=["values", "json"]
        )
        args = parser.parse_args()
        email = args.get("email")
        mobile = args.get("mobile")
        password = args.get("password")

        self.mobile, self.email = mobile, email

        if not self.account_available():
            return json_resp(msg=self.error_msg)

        _current_user = U.better_get(U.mobile == mobile, U.email == email, U.status == 1)
        if not _current_user:
            return json_resp(msg="account hasn't been registered error")
        if not Password.verify(password, _current_user.password):
            return json_resp(msg="password mismatching error")

        login_user(_current_user, remember=True)

        ip = request.remote_addr
        U.update(
            lastLoginIp=ip, lastLoginAt=datetime.datetime.now()
        ).where(
            U.mobile == mobile, U.email == email, U.status == 1
        ).execute()
        return json_resp(status=1, msg="success")
