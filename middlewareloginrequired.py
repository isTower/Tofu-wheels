#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/13 10:58
# @Author  : Money
# @Site    : 
# @File    : middlewareloginrequired.py
# @Software: PyCharm

from functools import wraps


from django.conf import settings
from django.shortcuts import HttpResponseRedirect
from django.urls import RegexURLPattern  # django2.0以上替换为：from django.urls import URLPattern


from . import urls



class MiddlewareLoginRequired(object):
    """
    需要用户登录之后才能访问页面的中间件，
    使用session判断用户是否登录
    """
    _NO_NEED_LOGIN = []  #用来存放不需要做登录认证的view

    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request, *args, **kwargs):
        response = self.get_response(request)
        user_hash = request.session.get('_auth_user_hash','')
        if not user_hash:
            url = request.path
            if url in self.exclude_url_path():
                return response
            else:
                return HttpResponseRedirect(settings.LOGIN_URL + '?next=' + url)
        return response

    @staticmethod
    def no_need_login(func):
        view_func = func.__module__ + '.' + func.__name__
        MiddlewareLoginRequired._NO_NEED_LOGIN.append(view_func)


    def get_all_urls(self, patterns, pre_fix, result):
        """
        获取所有的view函数和url的映射关系，
        :param patterns: urlpatterns
        :param pre_fix:
        :param result: 字典，{view函数:url}
        :return:
        """

        for item in patterns:
            part = item.regex.pattern.strip("^$") #django2.0以上替换为：part = item.pattern.regex.pattern.strip("^$")
            if isinstance(item, RegexURLPattern): #django2.0以上替换为：if isinstance(item, URLPattern):
                # django2.0以上替换为：url_path = item.pattern.regex.pattern.strip("^$").replace('\\', "")
                url_path = item.regex.pattern.strip("^$").replace('\\', "")
                view_func = item.callback.__module__ + '.' + item.callback.__name__
                if view_func.startswith(('django',)):
                    continue
                result.setdefault(view_func, pre_fix + url_path)
            else:
                self.get_all_urls(item.url_patterns, pre_fix + part, result=result)

        return result

    def exclude_url_path(self):
        view_url_dicts = self.get_all_urls(urls.urlpatterns, pre_fix="/", result={})
        url_paths = list([view_url_dicts[view] for view in self._NO_NEED_LOGIN
                     if view in view_url_dicts])
        return url_paths



def login_excepted(func=None):
    """
    类似login_required，
    使用这个函数装饰的view不需要登录就可以访问，
    使用方法：@login_excepted 或者
            @login_excepted()
    :param func:
    :return:
    """
    def _wrapped(func):
        MiddlewareLoginRequired.no_need_login(func)
        @wraps(func)
        def inner(*args, **kwargs):
            return func(*args, **kwargs)
        return inner
    if not func:
        return _wrapped
    return _wrapped(func)