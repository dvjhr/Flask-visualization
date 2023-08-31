#!/usr/bin/env python
from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from flask_session import Session
import pandas as pd
import jinja2.exceptions
from flask_cors import CORS, cross_origin
import os
from datetime import datetime
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app)
Session(app)

@app.route('/')
def index():
    raw_datasets_count = len(datasets_open())
    clean_datasets_count = len(datasets_preprocess())
    cluster_group, cluster_data = datasets_cluster()
    model_results = model_result()
    labeling_datas = datasets_sentiment()[:50]
    ranking_datas = datasets_ranking()
    print("LAGIIII ", dict(session))
    return render_template(
        'index.html',
        session=dict(session),
        raw_datasets_count=raw_datasets_count,
        clean_datasets_count=clean_datasets_count,
        all_cluster_count=len(cluster_data), 
        cluster_group=cluster_group, 
        cluster_data=cluster_data,
        model_results=model_results,
        labeling_datas=labeling_datas,
        ranking_datas=ranking_datas
        )

# @app.route('/rank_data')
# @cross_origin(origin='*')
def datasets_ranking():
    csv_data = pd.read_csv('data/resultRank.csv')
    dict_data = csv_data.to_dict('records')
    return dict_data

### CORS section
# @app.after_request
# def after_request_func(response):
    # print("called after req")
    # origin = request.headers.get('Origin')
    # response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # response.headers['Content-Security-Policy'] = "default-src '*'; style-src 'self' 'unsafe-inline';"
    # if request.method == 'OPTIONS':
        # response = make_response()
    # response.headers.add('Access-Control-Allow-Credentials', 'true')
    # response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    # response.headers.add('Access-Control-Allow-Headers', 'x-csrf-token')
    # response.headers.add('Access-Control-Allow-Methods',
    #                     'GET, POST, OPTIONS, PUT, PATCH, DELETE')
    # response.headers.add('Access-Control-Allow-Origin', '*')
    # if origin:
    #     response.headers.add('Access-Control-Allow-Origin', '*')
    # else:
    #     response.headers.add('Access-Control-Allow-Credentials', 'true')
    #     if origin:
    #         response.headers.add('Access-Control-Allow-Origin', '*')

    # print(origin)
    # return response

def datasets_open():
    csv_data = pd.read_csv('data/dataset.csv')
    csv_column = csv_data.columns
    dict_data = csv_data.to_dict('records')
    return dict_data

def datasets_preprocess():
    csv_data = pd.read_csv('data/datasetCleaned.csv')
    dict_data = csv_data.to_dict('records')
    return dict_data

def datasets_cluster():
    csv_data = pd.read_csv('data/datasetWclusters.csv')
    dict_data = csv_data.to_dict('records')
    cluster_counts = csv_data.groupby(['cluster']).count().to_dict()['komentarClean']
    return cluster_counts, dict_data

def datasets_sentiment():
    csv_data = pd.read_csv('data/datasetWsentiment.csv')
    dict_data = csv_data.to_dict('records')
    return dict_data

def model_result():
    csv_data = pd.read_csv('data/modelResult.csv')
    dict_data = csv_data.to_dict('records')
    return dict_data

@app.route('/<pagename>')
def admin(pagename):
    print(pagename)
    session['date'] = datetime.today().strftime('%d-%m-%Y')
    # print("HALOOO")
    if pagename in ['clustering','datasets','preprocessing','labeling','modelling','ranking']:
        print("LAGIIII ", dict(session))
        print(session.get(pagename))
        if pagename == "clustering":
            group, datas = datasets_cluster()
            return render_template(pagename+'.html', pagename=pagename, session=dict(session), group=group, datas=datas[:5000])
        if pagename == "datasets":
            datas = datasets_open()
        elif pagename == "preprocessing":
            datas = datasets_preprocess()
            # return render_template(pagename+'.html', session=dict(session), datas=datas[:500])
        elif pagename == "labeling":
            datas = datasets_sentiment()
        elif pagename == "modelling":
            datas = model_result()
        elif pagename == "ranking":
            datas = datasets_ranking()
        return render_template(pagename+'.html', pagename=pagename, session=dict(session), datas=datas)
    elif pagename != "upload":
        return render_template(pagename+'.html')
    return "Success"

@app.route('/session/<pagename>/<value>')
def session_create(pagename, value):
    if pagename and not session.get(pagename):
        print("SESSION CREATED FOR ", pagename)
        session['index'] = 1
    session[pagename] = value
    print("SESSION IS ", session.get(pagename))
    return jsonify({"pagename": pagename, "value": session[pagename]}), 301

@app.route('/session_remove/<pagename>')
def session_remove(pagename):
    print("SESSION REMOVED FOR ", pagename)
    if pagename == "all":
        session.clear()
        return redirect('/')
    else:
        session[pagename] = None
        session.pop('username', None)
        return jsonify({"pagename": pagename, "value": session[pagename]})

@app.route('/get_session')
def get_session():
    ses = session
    print(ses)
    return dict(ses)

@app.route('/upload/file', methods=['POST'])
def upload_file():
    uploaded_file = request.files.getlist('filename')
    pagename = request.form['pagename']
    for files in uploaded_file:
        if files:
            # You can process the file here, for example, save it to a specific location
            files.save(os.path.join('data', 'raw', secure_filename(files.filename)))
        else:
            return 'No file uploaded.'
    return redirect(f'/{pagename}')

@app.errorhandler(jinja2.exceptions.TemplateNotFound)
def template_not_found(e):
    return not_found(e)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')

if __name__ == '__main__':
    print("App refreshed!")
    app.run(debug=True)
