# -*- coding: utf-8 -*-
# @Date:   2018-01-02 16:02:00
# @Last Modified time: 2018-01-02 16:02:38
from types import MethodType
from flask_session import Session


class SsoSession(Session):

    @staticmethod
    def open_session(self, app, request):
        """
        open_session is called before @app.before_request by app.request_context(environ).push
        """
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = request.headers.get("Authorization") if request.headers else sid
            sid = request.values.get("Authorization") if not sid and request.values else sid
            sid = request.json.get("Authorization") if not sid and request.json else sid
            sid = request.files.get("Authorization") if not sid and request.files else sid
            if sid:
                request._cookies, request.cookies = request.cookies, request.cookies.copy()
                request.cookies.update({app.session_cookie_name: sid})
                open_session_memento = self.open_session_memento(app, request)
                request.cookies = request._cookies
                del request._cookies
                return open_session_memento
        # verify cookie and make session
        open_session_memento = self.open_session_memento(app, request)
        return open_session_memento

    @staticmethod
    def save_session(self, app, session, response):
        """
        save_session is called after @app.after_request by app.process_response
        """
        save_session_memento = self.save_session_memento(app, session, response)
        if response.headers.get("Set-Cookie"):
            # set token == session.sid
            response.headers["Authorization"] = session.sid
        else:
            response.headers["Authorization"] = ""
        return save_session_memento

    def _get_interface(self, app):
        session_interface = super(SsoSession, self)._get_interface(app)
        session_interface.save_session_memento = session_interface.save_session
        session_interface.open_session_memento = session_interface.open_session
        session_interface.save_session = MethodType(self.save_session, session_interface)
        session_interface.open_session = MethodType(self.open_session, session_interface)
        return session_interface
