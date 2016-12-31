# -*- coding: utf-8 -*-
import logging
import pymongo
import re
import os
import time
from django.shortcuts import render
from django.conf import settings
from django.http import StreamingHttpResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger

logger = logging.getLogger('search.views')

def global_setting(request):
    return {'SITE_NAME': settings.SITE_NAME,
            'SITE_DESC': settings.SITE_DESC,
            'COPYRIGHT': settings.COPYRIGHT,}


# 连接到mongodb 默认使用数据库spider
def get_database_connect():
    conn = pymongo.MongoClient(host='127.0.0.1', port=27017)
    db = conn.paper_spider
    return db


def handle_keywords(keywords):
    search_words = []
    word_format = ''
    for word in re.split(r' ', keywords):
        if (word != ''):
            word_format += (word.capitalize() + ' ')
    word_format = word_format[:-1]
    search_words.append(word_format)
    if (word_format.isupper() == False):
        search_words.append(word_format.upper())
    if (word_format.islower() == False):
        search_words.append(word_format.lower())
    if (word_format.istitle() == False):
        search_words.append(word_format.capitalize())  # 字符串的首字母转换成大写,其余转换成小写
    for word in re.split(r' ', keywords):
        if (word != ''):
            if (word.isupper() == False):
                search_words.append(word.upper())
            if (word.islower() == False):
                search_words.append(word.lower())
            if (word.istitle() == False):
                search_words.append(word.capitalize())  # 字符串的首字母转换成大写,其余转换成小写
    search_words = list(set(search_words))  # list去除重复
    return search_words


def handle_search(words):
    collections = ['conference', 'journal']
    results = []
    db = get_database_connect()
    for coll in collections:
        for word in words:
            for d in db[coll].find({'title': re.compile(word)}):
                results.append(d)
    return results


# 分页代码
def get_page(request, result_list):
    paginator = Paginator(result_list, 5)  # 每页显示5条结果
    try:
        page = int(request.GET.get('page', 1))
        result_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        result_list = paginator.page(1)
    return result_list


def index(request):
    return render(request, 'index.html', locals())


def search(request):
    if (request.method == 'GET'):   #当提交表单时
        keywords = request.GET.get('wd', None)
        if (keywords is not None):
            words = handle_keywords(keywords)
            if ((len(words) == 1) and (words[0] == '')):
                return render(request, 'index.html')
            else:
                try:
                    results = handle_search(words)
                    count = len(results)  # 搜索结果数量
                    results = get_page(request, list(results))    # 结果分页
                    return render(request, 'search.html', {'results': results, 'count': count})
                except Exception as e:
                    logger.error(e)
                    return render(request, 'search.html', locals())
    else:   # 正常访问时
        return render(request, 'search.html', locals())


def file_iterator(filename, chunk_size=512):
    if ((filename is not None) and (filename != '')):
    	if (os.path.exists(filename)):
    		with open(filename, 'rb') as f:
    			while True:
    				c = f.read(chunk_size)
    				if c:
    					yield c
    				else:
    					break
    	else:
    		print('文件不存在', filename)


def download(request):
    try:
        filename = request.GET.get('filename', time.strftime('%Y%m%d_%H%M%S', time.localtime()))
        filename = filename.strip() + '.pdf'
        filepath = request.GET.get('fileurl', None)
        if ((filepath is not None) and (filepath != '')):
        	filepath = 'files/' + filepath
        	if (os.path.exists(filepath)):
	            buffer = file_iterator(filepath)
	            response = StreamingHttpResponse(buffer)
	            response['Content-Type'] = 'application/octet-stream;charset=UTF-8'
	            response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filename)
	            return response  
    except Exception as e:
        logger.error(e)
    return render(request, 'error.html')


def error(request):
    return render(request, 'error.html')
