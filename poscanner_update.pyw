import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
import time
import traceback
import ingrex
import json
import os
import time
import requests
from ingrex import Intel, Utils
import telepot
from telegram.error import NetworkError, BadRequest
from telepot.exception import TooManyRequestsError
from copy import deepcopy
from telegram import Emoji

bot = telepot.Bot('247649707:AAFmQTqq_nXIajuySRETIU0jknfNWICPBv4')
config = None
global res_stat_7,enl_stat_7,res_stat_8,enl_stat_8
res_stat_7 = 0
enl_stat_7 = 0
res_stat_8 = 0
enl_stat_8 = 0
global res_po_8,enl_po_8
res_po_8 = ''
enl_po_8 = ''

def get_entities(tilekey):
    field = {
        'minLngE6':113531287,
        'minLatE6':22112090,
        'maxLngE6':113589600,
        'maxLatE6':22216029,
    }
    with open('cookie') as cookies:
        cookies = cookies.read().strip()
    intel = ingrex.Intel(cookies, field)
    result = intel.fetch_map([tilekey])
    return result
def get_portal_details(guid):
    field = {
        'minLngE6':113531287,
        'minLatE6':22112090,
        'maxLngE6':113589600,
        'maxLatE6':22216029,
    }
    with open('cookie') as cookies:
        cookies = cookies.read().strip()
    intel = ingrex.Intel(cookies, field)
    result = intel.fetch_portal(guid = guid)
    return result
def format_entity(self,portal):
    global res_stat_7,enl_stat_7,res_stat_8,enl_stat_8
    link = "https://ingress.com/intel?ll={0},{1}&pll={0},{1}".format(portal['location'][0], portal['location'][1])
    time_str = '\U000023F1<b>Time</b>:' + time.strftime('%Y-%m-%d %H:%M', time.localtime(portal['time'])) + '\n'
    title = '\U0001F4E1<b>Title</b>: ' + '<a href=\"' + link + '\">' + \
            portal['title'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') + \
            '</a>\n'
    level = '\U0001F4CA<b>Level</b>: ' + str(portal['level']) + '\n'
    rescount = ''
    if portal['level'] == 7:
        res_count = 0
        count = get_portal_details(portal['guid'])
        count = count[15]
        for x in range(0,len(count),1):
            if count[x][1] != 8:
                res_count += 1
        rescount = '\U0001F449缺<b>'+str(res_count)+'</b>隻八腳上八塔\n'
    if portal['faction'] == 'R':
        faction = '\U0001F50D<b>Faction</b>: RES'
        faction += '\U0001F42C'
    else:
        faction = '\U0001F50D<b>Faction</b>: ENL'
        faction += Emoji.FROG_FACE

    faction += '\n'
    address_str = '\U0001F4EE<b>Address</b>: ' + coordinate_to_address(self,lat=portal['location'][0], lng=portal['location'][1])
    if portal['level'] == 7:
        entity_str = time_str + title + level + faction + rescount + address_str + '\n'
    else:
        entity_str = time_str + title + level + faction + address_str + '\n'
    return entity_str
def format_detail(portal_detail):
    res_str = '\n\U0001F463<b>Resonators</b>:\n'
    for resonator in portal_detail.decoded['resonators']:
        res_str += resonator['owner'] + ' ' + 'L' + str(resonator['level']) + '\n'
    mod_str = '\n\U0001F4AC<b>Mods</b>:\n'
    for mod in portal_detail.decoded['mods']:
        mod_str += mod['owner'] + ' '  + ' ' + mod['rarity'] + ' ' + mod[
            'name'] + '\n'
    if portal_detail.decoded['owner'] == '__ADA__' or portal_detail.decoded['owner'] == '__JARVIS__':
        owner = '\U0001F451<b>Owner</b>:\n<b>' + portal_detail.decoded['owner'] + '</b>'
    else:
        owner = '\U0001F451<b>Owner</b>:\n' + portal_detail.decoded['owner']
    detail = res_str + mod_str + '\n' + owner
    return detail

def send_alert(self,text, chat_id):
    try:
        r = bot.sendMessage(chat_id=chat_id, text=text, parse_mode='HTML', disable_web_page_preview=True)
        time.sleep(1)
        return r['message_id']
    except NetworkError:
        log(self,'sendMessage error, maybe too many requests')
        time.sleep(60)
        send_alert(self,chat_id=chat_id, text=text)
    except TooManyRequestsError:
        log(self,'TooManyRequests error, maybe too many requests')
        time.sleep(60)
        send_alert(self,chat_id=chat_id, text=text)
    except:
        log(self,'Other error, maybe too many requests')
        time.sleep(60)
        #send_alert(self,chat_id=chat_id, text=text)

def edit_message(self,text, chat_id, message_id):
    try:
        bot.editMessageText((chat_id,message_id),text, parse_mode='HTML',disable_web_page_preview=True)
    except :
        log(self,'Edit message exception occurred. ')


def coordinate_to_address(self,lat, lng):
    url = 'http://maps.google.com/maps/api/geocode/json?latlng={},{}&language=zh-CN&sensor=false'.format(lat, lng)
    result = requests.get(url).json()
    if result['status'] == 'OK':
        return result['results'][0]['formatted_address']
    else:
        log(self,'CTA convert error. lat,lng=' + str([lat, lng]))
        return 'ERROR: ' + result['status']

def log(self,operation):
    time_str = '[' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '] '
    self.emit(SIGNAL('STATUS'),time_str + operation)

def load_config():
    global config
    with open('config.json') as f:
        config = json.load(f)
def Portal(self,detail):
    text = '\U000023F1<b>Time</b>: '
    link = "https://ingress.com/intel?ll={0},{1}&pll={0},{1}".format(float(detail[2]/1000000),float(detail[3]/1000000))
    portal_time = detail[13]/1000
    text += str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(portal_time)))+ '\n'
    if 'R' in str(detail[1]):
        text += '\U0001F50D<b>Faction</b>: RES'+'\U0001F42C'+'\n'
    else:
        text += '\U0001F50D<b>Faction</b>: ENL'+Emoji.FROG_FACE+'\n'
    text += '\U0001F4E1<b>Title</b>: '+'<a href=\"' + link + '\">' + \
            detail[8].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') + \
            '</a>\n'
    text += '\U0001F4AC<b>Mods</b>:\n'
    for x in range(0,len(detail[14]),1):
        if detail[14][x] != None:
            text += str(detail[14][x][1])+'('+str(detail[14][x][2])+')'+' by '+str(detail[14][x][0])+ '\n'
    text += '\n\U0001F463<b>Resonators</b>:\n'
    for x in range(0,len(detail[15]),1):
        if detail[15][x] != None:
            text += str(detail[15][x])+'\n'
    text += '\n\U0001F451<b>Owner</b>:'+str(detail[16])+ '\n'
    address_str = '\U0001F4EE<b>Address</b>: '+ coordinate_to_address(self,lat=float(detail[2]/1000000), lng=float(detail[3]/1000000))
    text += address_str
    return text
class Worker(QThread):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.url = 'https://accounts.google.com/ServiceLogin?service=ah&passive=true&continue=https%3A%2F%2Fappengine.google.com%2F_ah%2Fconflogin%3Fcontinue%3Dhttps%3A%2F%2Fwww.ingress.com%2Fintel&ltmpl=gm&shdf=ChMLEgZhaG5hbWUaB0luZ3Jlc3MMEgJhaCIUDxXHTvPWkR39qgc9Ntp6RlMnsagoATIUG3HUffbxSU31LjICBdNoinuaikg#identifier'

    def run(self):
        global res_stat_7,enl_stat_7,res_stat_8,enl_stat_8,res_po_8,enl_po_8
        load_config()
        i='Config has been loading......'
        log(self,i)
        status = {}
        last_status = {}
        if os.path.isfile('status.sav'):
            log(self,'Save has been loading......')
            with open('status.sav') as f:
                last_status = json.load(f)
        #n = 0
        while True:
            try:
                time1 = time.time()
                log(self,'Grabbing Data......')
                for tilekey in config['tilekeys']:
                    result = get_entities(tilekey)
                    entities = result['map'][tilekey]['gameEntities']
                    for entity in entities:
                        entity_type = entity[2][0]
                        if entity_type == 'p':
                            level = entity[2][4]
                            if level == 7:
                                if entity[2][1] == 'R':
                                    res_stat_7 += 1
                                else:
                                    enl_stat_7 += 1
                            elif level == 8:
                                if entity[2][1] == 'R':
                                    res_stat_8 += 1
                                    res_po_8 += '['+str(res_stat_8)+']'+entity[2][8]+'\n'
                                else:
                                    enl_stat_8 += 1
                                    enl_po_8 += '['+str(enl_stat_8)+']'+entity[2][8]+'\n'
                            if level >= config['min_level']:
                                guid = entity[0]
                                if guid in last_status.keys():
                                    portal = {'title': entity[2][8],
                                            'time': entity[1] / 1000,
                                            'faction': entity[2][1],
                                            'level': entity[2][4],
                                            'location': [entity[2][2] / 1E6, entity[2][3] / 1E6],
                                            'message_id': last_status[guid]['message_id'],
                                            'guid': guid}

                                    status[guid] = portal
                                else:
                                    portal = {'title': entity[2][8],
                                            'time': entity[1] / 1000,
                                            'faction': entity[2][1],
                                            'level': entity[2][4],
                                            'location': [entity[2][2] / 1E6, entity[2][3] / 1E6],
                                            'message_id': None,
                                            'guid': guid}
                                    status[guid] = portal
                time2 = time.time()
                log(self,'fetching done, ' + 'time: ' + str((time2 - time1)/60)+'mins')
                for guid in last_status.keys():
                    if guid not in status.keys():  # message to be deleted
                        link = "https://ingress.com/intel?ll={0},{1}&pll={0},{1}".format(last_status[guid]['location'][0],last_status[guid]['location'][1])
                        title = 'Title: ' + '<a href=\"' + link + '\">' + \
                                last_status[guid]['title'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') + \
                                '</a>\n'
                        text = title + '<b>DESTROYED</b>'
                        try:
                            edit_message(self,text, chat_id=config['chat_id'], message_id=last_status[guid]['message_id'])
                        except BadRequest as e:
                            log(self,'Edit message exception occurred. ' + str(e.message))
                        log(self,'portal destroyed: ' + last_status[guid]['title'] + ' ,message updated')
                    else:
                        if status[guid]['time'] > last_status[guid]['time']:
                            if status[guid]['level'] > last_status[guid]['level']:  # message to be re-pushed
                                link = "https://ingress.com/intel?ll={0},{1}&pll={0},{1}".format(
                                    last_status[guid]['location'][0],
                                    last_status[guid]['location'][1])
                                title = 'Title: ' + '<a href=\"' + link + '\">' + \
                                        last_status[guid]['title'].replace('&', '&amp;').replace('<', '&lt;').replace('>',
                                                                                                              '&gt;') + \
                                        '</a>\n'
                                text = title + '<b>REPLACED</b>'
                                try:
                                    edit_message(self,text, chat_id=config['chat_id'], message_id=last_status[guid]['message_id'])
                                except BadRequest as e:
                                    log(self,'Edit message exception occurred. ' + str(e.message))
                                log(self,'portal status changed: ' + last_status[guid]['title'])
                                text = format_entity(self,status[guid])
                                if status[guid]['level'] >= config['detail_level']:
                                    detail = get_portal_details(guid)
                                    portal_detail = Portal(self,detail)
                                    #text += format_detail(portal_detail)
                                    text = portal_detail
                                message_id = send_alert(self,text, config['chat_id'])
                                log(self,'alert sent: ' + status[guid]['title'])
                                status[guid]['message_id'] = message_id
                                log(self,'message replaced')
                            else:  # message to be edited
                                text = format_entity(self,status[guid])
                                if status[guid]['level'] >= config['detail_level']:
                                    detail = get_portal_details(guid)
                                    portal_detail = Portal(self,detail)
                                    #text += format_detail(portal_detail)
                                    text = portal_detail
                                try:
                                    edit_message(self,text, chat_id=config['chat_id'], message_id=status[guid]['message_id'])
                                except BadRequest as e:
                                    log(self,'Edit message exception occurred. ' + str(e.message))
                                log(self,'portal status changed: ' + status[guid]['title'] + ' ,message updated')
                for guid in status.keys():
                    if guid not in last_status.keys():  # message to be pushed
                        text = format_entity(self,status[guid])
                        if status[guid]['level'] >= config['detail_level']:
                            detail = get_portal_details(guid)
                            portal_detail = Portal(self,detail)
                            #text += format_detail(portal_detail)
                            text = portal_detail
                        log(self,'new portal found. title: ' + status[guid]['title'])
                        message_id = send_alert(self,text, config['chat_id'])
                        log(self,'alert sent: ' + status[guid]['title'])
                        status[guid]['message_id'] = message_id
            except:
                traceback.print_exc()
                #log(self,str(error_log))
            with open('status.sav', 'w') as f:
                f.write(json.dumps(status))
            last_status = deepcopy(status)
            status.clear()
            log_7 = '7塔數據:'+'\U0001F42C藍軍:'+str(res_stat_7)+Emoji.FROG_FACE+'綠軍:'+str(enl_stat_7)
            log_8 = '8塔數據:'+'\U0001F42C藍軍:'+str(res_stat_8)+Emoji.FROG_FACE+'綠軍:'+str(enl_stat_8)
            log(self,log_7)
            log(self,log_8)
            bot.sendMessage(config['chat_id'],text = log_7+'\n'+log_8)
            bot.sendMessage(config['chat_id'],text = '\U0001F42C'+'藍軍8po:\n'+res_po_8+'\n'+Emoji.FROG_FACE+'綠軍8po:\n'+enl_po_8)
            res_stat_7 = 0
            enl_stat_7 = 0
            res_stat_8 = 0
            enl_stat_8 = 0
            res_po_8 = ''
            enl_po_8 = ''
            log(self,'wait for ' + str(config['interval']) + ' sec.')
            time.sleep(config['interval'])
class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setWindowTitle('--Portal Scanner--')
        self.setWindowIcon(QtGui.QIcon('ingress.ico'))
        self.resize(900, 500)
        self.text = QtGui.QTextBrowser()
        self.text.setGeometry(QtCore.QRect(10, 10, 781, 481))
        self.text.setStyleSheet("background-color: black;")
        self.text.setFont(QFont("consolas"))
        self.text.setTextColor(QtGui.QColor('white'))
        self.run = QtGui.QPushButton('Run')
        self.run.setGeometry(QtCore.QRect(650, 510, 112, 34))

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(self.run)
        self.setLayout(layout)

        self.work = Worker()
        # SIGNAL&SLOT
        self.run.clicked.connect(self.start)
        self.connect(self.work, SIGNAL("STATUS"),self.updateUI)
    def start(self):
        self.work.start()
        self.run.setEnabled(False)

    def updateUI(self,status):
        if 'exception' in status:
            self.text.setTextColor(QtGui.QColor('red'))
            self.text.append('%s'%(status))
        elif 'error' in status:
            self.text.setTextColor(QtGui.QColor('red'))
            self.text.append('%s'%(status))
        elif 'changed' in status:
            self.text.setTextColor(QtGui.QColor('Magenta'))
            self.text.append('%s'%(status))
        elif 'new' in status:
            self.text.setTextColor(QtGui.QColor('yellow'))
            self.text.append('%s'%(status))
        elif 'alert' in status:
            self.text.setTextColor(QtGui.QColor('yellow'))
            self.text.append('%s'%(status))
        elif 'destroyed' in status:
            self.text.setTextColor(QtGui.QColor('lightGray'))
            self.text.append('%s'%(status))
        else:
            self.text.setTextColor(QtGui.QColor('white'))
            self.text.append('%s'%(status))

app = QApplication(sys.argv)
QQ = MainWindow()
QQ.show()
app.exec_()
