# coding:utf-8
'''
Created on 2022/5/1
@author: Fred
@performance: data
'''

from flask import views
from performance_app.perf_blueprint import per_blueprint
from performance_app.perf_blueprint import model



'''
@note: 创建performance test use case api
'''

per_blueprint.add_url_rule('/performance/self-defined/create', view_func=model.selfDCreate.as_view('self-defined'))
per_blueprint.add_url_rule('/performance/seq-rw/create', view_func=model.seqrwCreate.as_view('seq-rw'))
per_blueprint.add_url_rule('/performance/video/create', view_func=model.videoCreate.as_view('video'))
per_blueprint.add_url_rule('/performance/random-rw/create', view_func=model.randomrwCreate.as_view('random-rw'))
# per_blueprint.add_url_rule('/performance/random-rw/create', view_func=model.randomrwCreate1.as_view('random-rw'))


per_blueprint.add_url_rule('/reliability/spof-pvc/create', view_func=model.spofPvcCreate.as_view('spof-pvc'))
per_blueprint.add_url_rule('/reliablility/spof-pvc/show', view_func=model.spofpvcShow.as_view('spof-pvc-show'))

per_blueprint.add_url_rule('/reliability/spof/create', view_func=model.spofCreate.as_view('spof'))


per_blueprint.add_url_rule('/performance/seq-rw/show/read/iops', view_func=model.seqreadShowIOPS.as_view('seqrw-read-iops'))
per_blueprint.add_url_rule('/performance/seq-rw/show/read/mbps', view_func=model.seqreadShowMBPS.as_view('seqrw-read-mbps'))
per_blueprint.add_url_rule('/performance/seq-rw/show/write/iops', view_func=model.seqwriteShowIOPS.as_view('seqrw-write-iops'))
per_blueprint.add_url_rule('/performance/seq-rw/show/write/mbps', view_func=model.seqwriteShowMBPS.as_view('seqrw-write-mbps'))

per_blueprint.add_url_rule('/performance/video/show/read/iops', view_func=model.videoreadShowIOPS.as_view('video-read-iops'))
per_blueprint.add_url_rule('/performance/video/show/read/mbps', view_func=model.videoreadShowMBPS.as_view('video-read-mbps'))
per_blueprint.add_url_rule('/performance/video/show/write/iops', view_func=model.videowriteShowIOPS.as_view('video-write-iops'))
per_blueprint.add_url_rule('/performance/video/show/write/mbps', view_func=model.videowriteShowMBPS.as_view('video-write-mbps'))


per_blueprint.add_url_rule('/performance/random-rw/show/read/iops', view_func=model.randomrwShowIOPS.as_view('random-rw-iops'))
per_blueprint.add_url_rule('/performance/random-rw/show/read/mbps', view_func=model.randomrwShowMBPS.as_view('random-rw-mbps'))
