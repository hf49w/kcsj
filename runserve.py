from waitress import serve
from bilibili_backend.wsgi import application  # 替换成你实际的 wsgi 应用程序对象

if __name__ == "__main__":
    serve(application, host='0.0.0.0', port=8088)
