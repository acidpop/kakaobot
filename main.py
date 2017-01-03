#-*- coding: utf-8 -*-

import signal
import json
from flask import Flask, request
from flask import Response
from flask import render_template
import os
import sys
import requests
import linecache
from bs4 import BeautifulSoup
import urllib2
import xmltodict
import pymysql

from LogMgr import log

app = Flask(__name__)

# user_key : status
#global user_status = {}


def PrintException():
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        log.error('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
        #print 'EXCEPTION IN ({}, LINE {} "{}"): {}' % format(filename, lineno, line.strip(), exc_obj)
        print lineno
        print exc_obj


@app.route("/")
def hello():
    return "<h1>Hello World!</h1>"

@app.route("/keyboard", methods=['GET'])
def kakao_keyboard():
    try:
        json_res = {}
        #json_res["type"] = "text"
        json_res["type"] = "buttons"
        json_res["buttons"] = [u"버튼1", u"버튼2"] 

        response =  json.dumps(json_res, ensure_ascii=False, indent=4)

        #print response
        log.info("[kakao] keyboard - res:'%s'", response)

        return Response(response, mimetype='application/json; charset=utf-8')
    except Exception as e:
        PrintException()
        resp = Response("oops", mimetype='text/plane')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp


@app.route("/message", methods=['POST'])
def kakao_message():
    try:
        response = ""

        data = request.data.decode('utf-8')

        log.info('[kakao message] recv : %s', data)

        dataDict = json.loads(data)

        user_key = dataDict["user_key"]
        msgType =  dataDict["type"]
        content =  dataDict["content"] 

        log.info('[kakao message] Parsing json, user_key:%s, type:%s, content:%s', dataDict['user_key'], dataDict['type'], dataDict['content'])

        json_res = {}

        if msgType == 'text':
            log.info('Message is text type')
            json_res["message"] = {"text" : "KakaoTalk Chat Bot 시험 메시지입니다."}
            response =  json.dumps(json_res, ensure_ascii=False, indent=4)
            return Response(response, mimetype='application/json; charset=utf-8') 

        json_res["message"] = {"text" : "버튼을 눌렀어?!"}

        response =  json.dumps(json_res, ensure_ascii=False, indent=4)

        log.info("[kakao] message - res:'%s'", response)

        return Response(response, mimetype='application/json; charset=utf-8')

    except Exception as e:
        PrintException()
        resp = Response("oops", mimetype='text/plane')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

@app.route("/friend", methods=['POST'])
def kakao_friend():
    log.info('[kakao freend]')
    data = request.data.decode('utf-8')
    dataDict = json.loads(data)

    response = ""
    log.info("[kakao] friend - user_key:'%s'", dataDict["user_key"])

    return response

@app.route("/friend/<user_id>", methods=['DELETE'])
def kakao_delete_friend(user_id):
    response = ""
    log.info("[kakao] friend delete - user_id:'%s'", user_id)

    return response

@app.route("/chat_room/<room_id>", methods=['DELETE'])
def kakao_delete_root(room_id):
    response = ""

    log.info("[kakao] room delete - room_id:'%s'", room_id)

    return response




# Bus API
@app.route("/busarrive/", methods=["GET", "POST"])
@app.route("/busarrive/<station_id>", methods=["GET", "POST"])
def acidpop_get_bus_arrive_for_station_id(station_id):
    #daum_bus_url = 'https://m.map.daum.net/actions/busStationInfo?busStopId=BS103829&q=42-366'
    daum_bus_url = 'https://m.map.daum.net/actions/busStationInfo?busStopId=BS103829&q=' + station_id

    log.info("url : %s", daum_bus_url)

    try:

        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11')]
        data = opener.open(daum_bus_url)

        log.info("URL Text \n%s", data)

        sp = BeautifulSoup(data)

        busList = sp.find('ul', attrs={'class':'list_result bus_list_wrap'})

        busItem = busList.findAll('li')

        json_res = []
        bus_res = {}
        bus_arrive_arr = []

        for item in busItem:
            busType = item.find_all('span', class_="bus_type")[0].text
            busType2 = item.find('span', attrs={'class': 'screen_out'}).text
            bus_res["bus_type"] = busType + busType2
            #print bus_res["bus_type"]
            log.info('bus_type : %s', bus_res["bus_type"])
            busNo = item.find('strong', attrs={'class': 'tit_g'}).text
            bus_res["bus_no"] = busNo
            #print bus_res["bus_no"]
            log.info('bus_no : %s', bus_res["bus_no"])
            busArrives = item.findAll('span', attrs={'class': 'txt_situation'})
            for arrive in busArrives:
                bustime = arrive.text.replace('\t', '')
                bustime = bustime.replace('\n', '|')
                bus_arrive_arr.append(bustime)
                #print arrive.text

            bus_res["bus_time"] = bus_arrive_arr
            bus_arrive_arr = []

            json_res.append(bus_res)

            bus_res = {}

        response =  json.dumps(json_res, ensure_ascii=False, indent=4)
        log.info("[REST] Bus Arrive - res:'%s'", response)

    except urllib2.HTTPError, e:
        log.error("get bus info Fail, HTTPError:'%d', Except :'%s'", e.code, e)
        resp = Response("oops", mimetype='text/plane')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except urllib2.URLError, e:
        log.error("get bus info Fail, URLError:'%s', Except :'%s'", str(e.reason), e)
        resp = Response("oops", mimetype='text/plane')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except:
        PrintException()
        resp = Response("oops", mimetype='text/plane')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    #except httplib.HTTPException, e:
    #    log.error("GetTorrentFileLink Fail, HTTP Exception :'%s'", str(e.reason), e)
    #    return '', ''

    resp = Response(response, mimetype='application/json; charset=utf-8')
    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp



@app.errorhandler(404)
def page_not_found(error):
    log.error('Page not found: %s', (request.path))
    return render_template('404.htm'), 404


@app.errorhandler(500)
def internal_server_error(error):
    log.error('Server Error: %s', (error))
    return render_template('500.htm'), 500

@app.errorhandler(Exception)
def unhandled_exception(e):
    PrintException()
    log.error('Unhandled Exception: %s', (e))
    return render_template('500.htm'), 500



SIGNALS_TO_NAMES_DICT = dict((getattr(signal, n), n) for n in dir(signal) if n.startswith('SIG') and '_' not in n )

def signal_handler(signal, frame):
    log.info('recv signal : %s[%d]', SIGNALS_TO_NAMES_DICT[signal], signal)
    #print('recv signal : %s[%d]', SIGNALS_TO_NAMES_DICT[signal], signal)
    #traceback.print_stack(frame)

if __name__ == "__main__":
    # signal Register
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGABRT, signal_handler)
    signal.signal(signal.SIGSEGV, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    app.run(host='0.0.0.0', debug=True, port=8181)

