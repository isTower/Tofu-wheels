# django中间件，用来验证用户登录

###功能
对django除了内置模块的所有url进行登录认证，没有登录则重定向到登录页面

###用法
0. 将py文件放置到project目录下，在settings.py文件的MIDDLEWARE中添加:
        ’project.middlewareloginrequired.MiddlewareLoginRequired‘
1. 在views.py中导入login_excepted：
        from project.middlewareloginrequired import login_excepted
2. 使用该装饰器 
        @login_excepted 或者 @login_excepted()
3. 如果需要登录之后跳转到原先的页面，需要在登录view中使用：
        path = request.GET.get('next')
        中间代码省略
        login(request, user)
                return redirect(path)