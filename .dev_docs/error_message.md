1.230.216.14 - - [11/Jan/2026 19:59:05] "GET /my/company HTTP/1.1" 500 -
Traceback (most recent call last):
  File "D:\projects\hrmanagement\venv\Lib\site-packages\flask\app.py", line 2213, in __call__
    return self.wsgi_app(environ, start_response)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\projects\hrmanagement\venv\Lib\site-packages\flask\app.py", line 2193, in wsgi_app
    response = self.handle_exception(e)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\projects\hrmanagement\venv\Lib\site-packages\flask\app.py", line 2190, in wsgi_app
    response = self.full_dispatch_request()
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\projects\hrmanagement\venv\Lib\site-packages\flask\app.py", line 1486, in full_dispatch_request
    rv = self.handle_user_exception(e)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\projects\hrmanagement\venv\Lib\site-packages\flask\app.py", line 1484, in full_dispatch_request
    rv = self.dispatch_request()
         ^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\projects\hrmanagement\venv\Lib\site-packages\flask\app.py", line 1469, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\projects\hrmanagement\app\shared\utils\decorators.py", line 146, in decorated_function
    return f(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^
  File "D:\projects\hrmanagement\app\domains\user\blueprints\mypage.py", line 75, in company_info
    return render_template('domains/user/mypage/company_info.html',
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: flask.templating.render_template() got multiple values for keyword argument 'attachment_list'