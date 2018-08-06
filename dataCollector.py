from werkzeug.utils import secure_filename
from flask import Flask,render_template,jsonify,request,send_from_directory
import time
import os
import base64
import csv
import sys
import json

app = Flask(__name__)
FILES = 'logfiles'
SOLUTION = 'solutions'
app.config['FILES'] = FILES

#path
basedir = os.path.abspath(os.path.dirname(__file__))
file_dir = os.path.join(basedir, app.config['FILES'])


ALLOWED_EXTENSIONS = set(['txt','png','jpg','xls','JPG','PNG','xlsx','gif','csv'])

#detect the type of file
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

##collect files
@app.route('/support')

def mainpage():
	return render_template("dataCollector.html")

@app.route('/collect', methods=['POST'], strict_slashes = False)

def upload():
	basedir = os.path.abspath(os.path.dirname(__file__))
	file_dir = os.path.join(basedir, app.config['FILES'])
	if not os.path.exists(file_dir):
		os.makedirs(file_dir)
	f=request.files['logfile']  # 从表单的file字段获取文件，logfile为该表单的name值
	if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
		fname=secure_filename(f.filename)
		print (fname)
		'''
		ext = fname.rsplit('.',1)[1]  # 获取文件后缀
		unix_time = int(time.time())
		tmp =str(unix_time)  # 修改了上传的文件名
		#new_filename = str(base64.b64encode(tmp.encode()))+'.'+ext
		new_filename = tmp+'.'+ext
		'''
		file_dir = os.path.join(file_dir,fname)
		f.save(file_dir)  #保存文件到upload目录
		print ("upload file saved")


	s = request.form['solution']
	print(basedir)
	with open(basedir + '/solutions.json', 'r') as solutions:
		dic = json.load(solutions)
		if fname in dic:
			fname = fname + '2'
		dic[fname] = s
	with open(basedir + '/solutions.json', 'w') as solutions:
		json.dump(dic, solutions)
	return render_template("successPage.html")


if __name__ == "__main__":
  app.run(debug = True, host = '0.0.0.0', port = 80)