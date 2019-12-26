from requests import get
import json
from datetime import datetime, timedelta
from pytz import timezone
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.dates import DateFormatter
import matplotlib.font_manager as fontman
import subprocess
import getopt
import os
import sys
#import wikiquote
# import textwrap
import PIL
from PIL import ImageFont, ImageDraw
import PIL.ImageOps
from pyunsplash import PyUnsplash
from random import randint
from scipy import interpolate

#location where figure will be stored
path="/home/homeassistant/.homeassistant/www"
os.chdir(path)

# import long-live token
import headerfiles as parameters
headers=parameters.headers
address_hass=parameters.address_hass

# e-paper display size
width_displ=640
height_displ=384
dpi=100;

# check if passed options are valid
try:
    options, args = getopt.getopt(sys.argv[1:], 's:',['selection='])
    # print(options)
    # print(args)
except getopt.GetoptError:
    print("incorrect syntax")
    print("usage: python3 db_plotter.py -s <value>")
    print("default to option 1")
    display_option=1
    sys.exit(2)
for opt, value in options:
    if opt in ('-s','-S','--selection'):
        display_option=int(float(value))
        print("successful argument")
        print(display_option)

####################################################################
# get timezone to convert to local time, since database attributes are in UTC time
url='http://'+address_hass+':8123/api/config'
response = get(url, headers=headers)
temp=response.text
readable_json=json.loads(temp)
time_zone=readable_json['time_zone']
tz = timezone(time_zone)

matplotlib.rcParams['timezone'] = time_zone #because matplotlib is stupid when formatting axis


# # if you want to do checks with time correct
# url='http://'+address_hass+':8123/api/states/sensor.date_time_iso'
# response = get(url, headers=headers)
# temp=response.text
# readable_json=json.loads(temp)
#
# hass_time_real = datetime.strptime(readable_json['state'], '%Y-%m-%dT%H:%M:%S')
# hass_time_recorder=datetime.strptime(readable_json['last_changed'],'%Y-%m-%dT%H:%M:%S.%f%z')

# add timezone to datetime
# hass_time_real = tz.localize(hass_time_real)
# hass_time_recorder.astimezone(tz)
# dt=hass_time_real-hass_time_recorder


############################################################################
## get commute evolution of last hour
# time_now=datetime.datetime.now()
# time_now.strftime('%m/%d/%Y')
# datetime.timedelta(days=days_to_subtract)

if display_option==2:
    entity_id='sensor.commute'
    # url='http://'+address_hass+':8123/api/history/period/'+'2019-09-17T19:00:00+02:00'+'?filter_entity_id='+entity_id
    # end_time=2016-12-31T00%3A00%3A00%2B02%3A00

    # this downloads history of the last day
    url='http://'+address_hass+':8123/api/history/period'+'?filter_entity_id='+entity_id

    response = get(url, headers=headers)
    temp=response.text
    temp=temp[1:len(temp)-1]
    readable_json=json.loads(temp)

    time_array= np.array([])
    state_array=np.array([])
    for i in readable_json:
        try:
            state_array=np.append(state_array,float(i['state']))
            time_update=datetime.strptime(i['last_updated'],'%Y-%m-%dT%H:%M:%S.%f%z')
            time_array=np.append(time_array, time_update.astimezone(tz))
        except:
            print("unknown state")

    # only plot data from last hour
    time_treshold=time_array[-1]-timedelta(hours=1)
    idx=time_array>time_treshold

    last_info=readable_json[-1]
    last_attr=last_info['attributes']

    fig=plt.figure(num=None, figsize=(int(width_displ/dpi), int(height_displ/dpi)), dpi=dpi, facecolor='w', edgecolor='k')

    plt.plot(time_array[idx],state_array[idx],linewidth=7.0,c='k')
    plt.ylabel('Minutes',fontsize=20)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax.legend(['updated: '+time_array[-1].strftime('%d/%m %H:%M')],loc='best')
    # ax.legend(['Waze'])
    plt.title('Commute: '+format(state_array[-1],'.0f')+' min'+'\n '+'Route: '+last_attr['route'],fontsize=28)
    # plt.title(r'{\fontsize{30pt}{3em}\selectfont{}{Time:'+format(state_array[-1],'.0f')+'\n}{\fontsize{18pt}{3em}\selectfont{}(September 16 - October 30, 2012)}')
    # plt.title('My Title\n' + r'$\alpha - \omega$ are LaTeX Markup')
    # ax.set_title('Commute time: '+format(state_array[-1],'.0f')+' \n '+last_attr['route'],fontsize=28)
    xformatter = DateFormatter('%H:%M')
    plt.gcf().axes[0].xaxis.set_major_formatter(xformatter)
    plt.gcf().autofmt_xdate()

    fig.savefig('plot.png',bbox_inches='tight',dpi=dpi)
    # create BMP
    cp = subprocess.run(["convert plot.png -resize 640x384 -type GrayScale -depth 8 black2.bmp"],shell=True,stdout=subprocess.PIPE)

elif display_option==1:
    entity_id='sensor.robot_power'
    url='http://'+address_hass+':8123/api/history/period'+'?filter_entity_id='+entity_id
    response = get(url, headers=headers)
    temp=response.text
    temp=temp[1:len(temp)-1]
    readable_json=json.loads(temp)

    time_array= np.array([])
    state_array=np.array([])
    for i in readable_json:
        try:
            state_array=np.append(state_array,float(i['state']))
            time_update=datetime.strptime(i['last_updated'],'%Y-%m-%dT%H:%M:%S.%f%z')
            time_array=np.append(time_array, time_update.astimezone(tz))
        except:
            print("uknown state")
    fig=plt.figure(num=None, figsize=(int(width_displ/dpi), int(height_displ/dpi)), dpi=dpi, facecolor='w', edgecolor='k')
    plt.plot(time_array,state_array,linewidth=7.0,c='k')
    plt.ylabel('Watt',fontsize=20)
    ax = plt.gca()
    ax.legend(['updated: '+time_array[-1].strftime('%d/%m %H:%M')],loc='best')
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    plt.title('Power Mowing Robot',fontsize=28)
    xformatter = DateFormatter('%H:%M')
    plt.gcf().axes[0].xaxis.set_major_formatter(xformatter)
    plt.gcf().autofmt_xdate()

    fig.savefig('plot.png',bbox_inches='tight',dpi=dpi)
    # create BMP
    cp = subprocess.run(["convert plot.png -resize 640x384 -type GrayScale -depth 8 black2.bmp"],shell=True,stdout=subprocess.PIPE)
# elif display_option==3:
#     str_qtd=wikiquote.quote_of_the_day()
#
#     white=255
#     image=PIL.Image.new('L',(width_displ,height_displ) , color=white)
#     draw = ImageDraw.Draw(image)
#
#     fList = fontman.findSystemFonts(fontpaths=None, fontext='ttf')
#     targetFont = []
#     searchFont='DejaVuSerif'
#     for row in fList:
#         try:
#             if searchFont in row:
#                 targetFont.append(row)
#         except TypeError:
#             pass
#     font = ImageFont.truetype(targetFont[0], 16)
#
#     margin = offset = 40
#     for line in textwrap.wrap(str_qtd[0], width=60):
#         draw.text((margin, offset), line, font=font)
#         offset += font.getsize(line)[1]
#     wrapper = textwrap.TextWrapper(width=50)
#     image.save('test.png')
#
elif display_option==4:
    api_key = '4d567a0f2dea38fb54e06c03a3efa0e8df73cdec5de06bc5c62653033357b90c'
    py_un = PyUnsplash(api_key=api_key)

    randNumb1 = randint(1, 5)
    pageLength=30
    randNumb2= randint(0,pageLength-1)
    listPhoto = py_un.search(type_='photos',query='white',per_page=pageLength,page=randNumb1)

    i=1
    for photo in listPhoto.entries:
        # print(photo.link_download)
        i=i+1
        if i>=randNumb2:
            cmd="wget "+photo.link_download+" --output-document=\""+"unsplash.jpeg\""
            cp = subprocess.run([cmd],shell=True,stdout=subprocess.PIPE)
            break

    cp = subprocess.run(["convert unsplash.jpeg -resize 640x384 -type GrayScale -depth 8  -rotate \"180\" black1.bmp"],shell=True,stdout=subprocess.PIPE)
elif display_option==5:
    entity_id='sensor.temperature_bathroom'
    url='http://'+address_hass+':8123/api/history/period'+'?filter_entity_id='+entity_id
    response = get(url, headers=headers)
    temp=response.text
    temp=temp[1:len(temp)-1]
    readable_json=json.loads(temp)

    amount_of_hours=12

    time_array= np.array([])
    state_array=np.array([])
    for i in readable_json:
        try:
            state_array=np.append(state_array,float(i['state']))
            time_update=datetime.strptime(i['last_updated'],'%Y-%m-%dT%H:%M:%S.%f%z')
            time_array=np.append(time_array, time_update.astimezone(tz))
        except:
            print("unknown state")

    # only plot data from last 12 hour
    time_treshold=time_array[-1]-timedelta(hours=amount_of_hours)
    idx=time_array>time_treshold

    last_info=readable_json[-1]
    last_attr=last_info['attributes']

    fig=plt.figure(num=None, figsize=(int(width_displ/dpi), int(height_displ/dpi)), dpi=dpi, facecolor='w', edgecolor='k')

    fig.add_subplot(2, 2, 1)
    plt.plot(time_array[idx],state_array[idx],linewidth=7.0,c='k')
    # plt.ylabel('C',fontsize=14)
    ax = plt.gca()
    # ax.legend(['updated: '+time_array[-1].strftime('%d/%m %H:%M')],loc='best')
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    plt.title('Badkamer',fontsize=16)
    xformatter = DateFormatter('%H:%M')
    plt.gcf().axes[0].xaxis.set_major_formatter(xformatter)
    plt.gcf().autofmt_xdate()

# zolder
    entity_id='sensor.temperature_zolder'
    url='http://'+address_hass+':8123/api/history/period'+'?filter_entity_id='+entity_id
    response = get(url, headers=headers)
    temp=response.text
    temp=temp[1:len(temp)-1]
    readable_json=json.loads(temp)

    time_array= np.array([])
    state_array=np.array([])
    for i in readable_json:
        try:
            state_array=np.append(state_array,float(i['state']))
            time_update=datetime.strptime(i['last_updated'],'%Y-%m-%dT%H:%M:%S.%f%z')
            time_array=np.append(time_array, time_update.astimezone(tz))
        except:
            print("unknown state")

    # only plot data from last 12 hour
    time_treshold=time_array[-1]-timedelta(hours=amount_of_hours)
    idx=time_array>time_treshold

    last_info=readable_json[-1]
    last_attr=last_info['attributes']

    fig.add_subplot(2, 2, 2)
    plt.plot(time_array[idx],state_array[idx],linewidth=7.0,c='k')
    # plt.ylabel('C',fontsize=14)
    ax = plt.gca()
    # ax.legend(['updated: '+time_array[-1].strftime('%d/%m %H:%M')],loc='best')
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    plt.title('Zolder',fontsize=16)
    xformatter = DateFormatter('%H:%M')
    plt.gcf().axes[1].xaxis.set_major_formatter(xformatter)
    plt.gcf().autofmt_xdate()

    entity_id='sensor.temperature_living'
    url='http://'+address_hass+':8123/api/history/period'+'?filter_entity_id='+entity_id
    response = get(url, headers=headers)
    temp=response.text
    temp=temp[1:len(temp)-1]
    readable_json=json.loads(temp)

    time_array= np.array([])
    state_array=np.array([])
    for i in readable_json:
        try:
            state_array=np.append(state_array,float(i['state']))
            time_update=datetime.strptime(i['last_updated'],'%Y-%m-%dT%H:%M:%S.%f%z')
            time_array=np.append(time_array, time_update.astimezone(tz))
        except:
            print("unknown state")

    # only plot data from last 12 hour
    time_treshold=time_array[-1]-timedelta(hours=amount_of_hours)
    idx=time_array>time_treshold

    last_info=readable_json[-1]
    last_attr=last_info['attributes']

    fig.add_subplot(2, 2, 3)
    plt.plot(time_array[idx],state_array[idx],linewidth=7.0,c='k')
    # plt.ylabel('C',fontsize=14)
    ax = plt.gca()
    # ax.legend(['updated: '+time_array[-1].strftime('%d/%m %H:%M')],loc='best')
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    plt.title('Lving',fontsize=16)
    xformatter = DateFormatter('%H:%M')
    plt.gcf().axes[2].xaxis.set_major_formatter(xformatter)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()

    entity_id='sensor.temperature_flow_radiator'
    url='http://'+address_hass+':8123/api/history/period'+'?filter_entity_id='+entity_id
    response = get(url, headers=headers)
    temp=response.text
    temp=temp[1:len(temp)-1]
    readable_json=json.loads(temp)

    time_array= np.array([])
    state_array=np.array([])
    for i in readable_json:
        try:
            state_array=np.append(state_array,float(i['state']))
            time_update=datetime.strptime(i['last_updated'],'%Y-%m-%dT%H:%M:%S.%f%z')
            time_array=np.append(time_array, time_update.astimezone(tz))
        except:
            print("unknown state")

    # only plot data from last 12 hour
    time_treshold=time_array[-1]-timedelta(hours=amount_of_hours)
    idx=time_array>time_treshold

    last_info=readable_json[-1]
    last_attr=last_info['attributes']

    # convert to timestamps because of python interpolation crap
    time_array_seconds= np.array([])
    for i in range(time_array.size):
        if idx[i]==True:
            time_array_seconds=np.append(time_array_seconds,time_array[i].timestamp())

    f = interpolate.interp1d(time_array_seconds,state_array[idx], kind='previous', axis=0)
    time_interpol=np.linspace(time_array_seconds[0],time_array_seconds[-1],600)
    temp_interpol=f(time_interpol)

    # convert back to datetime
    time_array_plot= np.array([])
    for i in range(time_interpol.size):
        # breakpoint()
        time_array_plot=np.append(time_array_plot,datetime.fromtimestamp(time_interpol[i]))

    # breakpoint()
    fig.add_subplot(2, 2, 4)
    plt.plot(time_array_plot,temp_interpol,linewidth=7.0,c='k')
    # plt.plot(time_array[idx],state_array[idx],linewidth=7.0,c='k',marker="o")
    # plt.plot(time_array[idx],state_array[idx],c='k',marker="o")
    # plt.ylabel('C',fontsize=14)
    ax = plt.gca()
    # ax.legend(['updated: '+time_array[-1].strftime('%d/%m %H:%M')],loc='best')
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    plt.title('Radiator',fontsize=16)
    xformatter = DateFormatter('%H:%M')
    plt.gcf().axes[3].xaxis.set_major_formatter(xformatter)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()

    fig.savefig('test.png',dpi=dpi)
    # fig.savefig('test.png',bbox_inches='tight',dpi=dpi)

    # white=255
    # image=PIL.Image.new('L',(width_displ,height_displ) , color=white)
    # draw = ImageDraw.Draw(image)
    #
    # fList = fontman.findSystemFonts(fontpaths=None, fontext='ttf')
    # targetFont = []
    # # searchFont='DejaVuSerif'
    # searchFont='UbuntuMono'
    # for row in fList:
    #     try:
    #         if searchFont in row:
    #             targetFont.append(row)
    #     except TypeError:
    #         pass
    # # breakpoint()
    # font = ImageFont.truetype(targetFont[0], 16)
    # margin=0
    # offset=0
    # im = PIL.Image.open("thermometer.bmp").convert("L")
    # im = PIL.ImageOps.invert(im)
    # draw.bitmap((margin,offset),im)
    # margin=margin+25
    # offset=offset+5
    # draw.text((margin, offset), 'Temp Badkamer  '+format(state_array[-1],'.0f')+' C', font=font)
    # image.save('test.png')
    cp = subprocess.run(["convert test.png -resize 640x384 -type GrayScale -depth 8  -rotate \"180\" black1.bmp"],shell=True,stdout=subprocess.PIPE)


    # fig=plt.figure(num=None, figsize=(int(width_displ/dpi), int(height_displ/dpi)), dpi=dpi, facecolor='w', edgecolor='k')
    #
    # plt.plot(time_array[idx],state_array[idx],linewidth=7.0,c='k')
    # plt.ylabel('Minutes',fontsize=20)
    # plt.xticks(fontsize=18)
    # plt.yticks(fontsize=18)
    # ax = plt.gca()
    # ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    # ax.legend(['updated: '+time_array[-1].strftime('%d/%m %H:%M')],loc='best')
    # # ax.legend(['Waze'])
    # # plt.title('Temp bathroom: '+format(state_array[-1],'.0f')+' min'+'\n '+'Route: '+last_attr['route'],fontsize=28)
    # # plt.title(r'{\fontsize{30pt}{3em}\selectfont{}{Time:'+format(state_array[-1],'.0f')+'\n}{\fontsize{18pt}{3em}\selectfont{}(September 16 - October 30, 2012)}')
    # # plt.title('My Title\n' + r'$\alpha - \omega$ are LaTeX Markup')
    # # ax.set_title('Commute time: '+format(state_array[-1],'.0f')+' \n '+last_attr['route'],fontsize=28)
    # xformatter = DateFormatter('%H:%M')
    # plt.gcf().axes[0].xaxis.set_major_formatter(xformatter)
    # plt.gcf().autofmt_xdate()
    # fig.savefig('plot.png',bbox_inches='tight',dpi=dpi)
    # # create BMP
    # cp = subprocess.run(["convert plot.png -resize 640x384 -type GrayScale -depth 8 black2.bmp"],shell=True,stdout=subprocess.PIPE)
