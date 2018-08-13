from werkzeug.utils import secure_filename
from flask import Flask,render_template,jsonify,request,send_from_directory
import time
import os
import base64
import csv
import sys
import json
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pickle
import nltk
import re
from nltk.stem.snowball import SnowballStemmer

app = Flask(__name__)
FILES = 'logfiles'
DATA = 'data'
app.config['FILES'] = FILES
app.config['DATA'] = DATA

lines_to_select = {}
result_to_vector = ''
suggest_solution = ''
filename = ''


#path
basedir = os.path.abspath(os.path.dirname(__file__))
file_dir = os.path.join(basedir, app.config['FILES'])


ALLOWED_EXTENSIONS = set(['txt','png','jpg','xls','JPG','PNG','xlsx','gif','csv'])
stemmer = SnowballStemmer('english')

#detect the type of file
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

def tokenize_and_stem(error_line):
    #tokenize the word and then stem them
    tokens = [word for word in nltk.word_tokenize(error_line)]
    filtered_tokens = []
    for token in tokens:
        if re.search('[a-zA-Z]',token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems

##collect files
@app.route('/support')

def mainpage():
	return render_template("dataCollector.html")

@app.route('/collect', methods=['GET','POST'], strict_slashes = False)

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
		csv_dir = os.path.join(file_dir,fname)
		f.save(csv_dir)  #保存文件到upload目录
		print ("upload file saved")

	#else:  //TODO
	tag_need = ["ERROR", "WARN"]
	global lines_to_select
	lines_to_select = {}
	count = 0
	with open(csv_dir, 'r') as file:
		for line in file:
			if line.split(",")[0] in tag_need:
				count += 1
				lines_to_select[count] = line
	print("dict in collect:", lines_to_select)





	return render_template("successPage.html", lines_to_select = lines_to_select)


'''
	#solution dict part
	s = request.form['solution']
	print(basedir)
	with open(basedir + '/solutions.json', 'r') as solutions:
		dic = json.load(solutions)
		if fname in dic:
			fname = fname + '2'
		dic[fname] = s
		dic["count"] += 1
	with open(basedir + '/solutions.json', 'w') as solutions:
		json.dump(dic, solutions)
		'''

@app.route('/select', methods = ['GET','POST'], strict_slashes = False)

def select():
	basedir = os.path.abspath(os.path.dirname(__file__))
	file_dir = os.path.join(basedir, app.config['DATA'])
	selected_lines = request.values.getlist('selected')
	print(selected_lines)
	unix_time = int(time.time())
	global filename
	filename = str(unix_time) + ".csv"
	data_dir = os.path.join(file_dir,filename)
	global lines_to_select
	print("dictionary:" , lines_to_select)
	global result_to_vector
	result_to_vector = ''

	#save selected lines as csv
	with open(data_dir, 'a+') as f:
		for key in selected_lines:
			print(lines_to_select[int(key)])
			f.write(lines_to_select[int(key)])
			result_to_vector += lines_to_select[int(key)].split(",")[-1]

	#prediction part
	test_solution = joblib.load(basedir + '/pickles/test_solution.pkl')
	load_tfidf_vectorizer = pickle.load(open(basedir+"/pickles/tfidf_vectorizer.pkl","rb"),encoding = "latin1")
	log_vec = load_tfidf_vectorizer.transform([result_to_vector])
	km = joblib.load(basedir + '/pickles/doc_cluster.pkl')
	label = km.predict(log_vec)[0]
	global suggest_solution
	suggest_solution = test_solution[label]

	return render_template("predict.html", suggest_solution = suggest_solution)

	#return render_template("successPage.html", lines_to_select = lines_to_select)
'''暂时不用
	#solution dict part
	s = request.form['solution']
	print(basedir)
	with open(basedir + '/solutions.json', 'r') as solutions:
		dic = json.load(solutions)
		if filename in dic:
			filename = filename + '2'
		dic[filename] = s
		dic["count"] += 1
	with open(basedir + '/solutions.json', 'w') as solutions:
		json.dump(dic, solutions)


	#prediction part
	test_solution = joblib.load('test_solution.pkl')
	load_tfidf_vectorizer = pickle.load(open(basedir+"/pickles/tfidf_vectorizer.pkl","rb"),encoding = "latin1")
	log_vec = load_tfidf_vectorizer.transform([result_to_vector])
	km = joblib.load('doc_cluster.pkl')
	label = km.predict(log_vec)[0]
	suggest_solution = test_solution[label]
'''
@app.route('/predictSuccess', methods = ['POST'], strict_slashes = False)

def addCount():
	#open solutions.json, count++, dict[filename.csv] = result
	global lines_to_select
	global filename
	global suggest_solution
	basedir = os.path.abspath(os.path.dirname(__file__))
	with open(basedir + '/solutions.json', 'r') as solutions:
		dic = json.load(solutions)
		if filename in dic:
			filename = filename + 'another'
		dic[filename] = suggest_solution
	with open(basedir + '/solutions.json', 'w') as solutions:
		json.dump(dic, solutions)
		
	return render_template("successPage.html", lines_to_select = lines_to_select)


@app.route('/addSolution', methods = ['POST'], strict_slashes = False)

def addNew():

	global lines_to_select
	global filename
	global suggest_solution
	basedir = os.path.abspath(os.path.dirname(__file__))
	newSolution = request.form['newSolution']
	with open(basedir + '/solutions.json', 'r') as solutions:
		dic = json.load(solutions)
		if filename in dic:
			filename = filename + 'another'
		dic[filename] = newSolution
		dic["count"] += 1
	with open(basedir + '/solutions.json', 'w') as solutions:
		json.dump(dic, solutions)
		
	return render_template("successPage.html", lines_to_select = lines_to_select)




if __name__ == "__main__":
  app.run(debug = True, host = '0.0.0.0', port = 80)