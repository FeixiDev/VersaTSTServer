# coding:utf-8
'''
Created on 2022/5/1
@author: Fred
@performance: data post
'''

from flask import Flask, Blueprint

def create_app():

    from performance_app.perf_blueprint import per_blueprint
    app = Flask(__name__)

    # 将蓝图注册到app
    app.register_blueprint(per_blueprint)
    return app
