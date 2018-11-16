#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
a Demo HTTPServer Using xjtucas_pyclient
Author: xczh <zhuxingchi@tiaozhan.com>

Copyright (C) 2016 tiaozhan. All Rights Reserved.
"""

# 导入xjtucas_pyclient库
import sys
sys.path.append('../src/')
from xjtucas_pyclient import CASClient

# 我们使用tornado作为演示HTTPServer
import tornado.ioloop
import tornado.web

class CASHandler(tornado.web.RequestHandler):
    ''' 处理CAS登录/登出请求的类 '''

    def get(self):
        # 实例化一个CASClient，通常使用基础协议，版本1即可
        # service_url为登录完毕之后回调url，本例使用同一个请求处理类完成重定向登录和验证工作
        cas = CASClient(
            version = '1',
            service_url = 'http://localhost/cas?extra_param1=p1',
        )
        action = self.get_argument('action', default='login')
        if action == 'login':
            # 登录逻辑
            # 判断GET参数中是否包含ticket参数，有则进行ST验证工作，无则重定向登录
            ticket = self.get_argument('ticket', default=None)
            if ticket:
                # 验证ST是否有效，有效返回用户NetID，无效返回None
                # 注意本方法返回一个3维元组，在版本1中后两维全为None，可以忽略
                # WARNING: 这是一个同步方法，会阻塞IO，因而不能用于异步框架，本例仅仅用于说明用法，不能用于tornado生产环境！
                # TODO: 异步(asyncio)验证支持
                netid = cas.verify_ticket(ticket)[0]
                if netid is not None:
                    # 此时登录工作已经完成，输出提示页面
                    text = '''
                    <html>
                        <body>
                            <h2>xjtucas_pyclient Version: %s</h2>
                            <p>Your NetID: %s</p>
                        </body>
                    </html>
                    ''' % (CASClient.getVersion(), netid)
                    return self.write(text)
            # ST无效，重定向进行登录
            return self.redirect(cas.get_login_url())
        elif action == 'logout':
            # 登出逻辑
            return self.redirect(cas.get_logout_url())
        else:
            return self.send_error('unsupported action: %s' % action)

def make_app():
    return tornado.web.Application([
        (r"/cas", CASHandler),
    ])

if __name__ == '__main__':
    app = make_app()
    # 请使用 http://localhost 进行测试，此回环地址已被网络中心授权用于开发测试
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()
