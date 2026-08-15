#!/usr/bin/env python

import os
from bottle import route,request, static_file,run

@route('/')
	return static_file('test.htm', root='.')
	
@route('/upload', method='POST')
def do_upload():
	category    = request.files.get('category')
    upload_file = request.files.get('upload')
	name, ext   = os.path.splittest(upload.filename)
	save_path = "/tmp"
	if not os.path.exists(save_path):
		os.makedirs(save_path)

	file_path="{path}/{file}".format(path=save_path,file=upload.filename)
	upload.save(file_path)
	return "File successfully saved to '{0}'.".format(save_path)

if __name__ == '__main__':
    run(host='0.0.0.0', port=9100)