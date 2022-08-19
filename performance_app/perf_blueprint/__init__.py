# coding:utf-8
'''
Created on 2022/5/1
@author: Fred
@performance: data post
'''
from flask import Flask,Blueprint

per_blueprint = Blueprint("per_blueprint", __name__)

from performance_app.perf_blueprint import views
