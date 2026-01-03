from django.conf.locale import fy

from beam_rect_fc import beam_rect_fc
from beam_t_fc import beam_T_fc
from report_beam_rect import report_beam_rect_fc

param = []
param.append([250,500,30,"HRB400","HRB400",1500,42.5,0,42.5])
param.append([250,500,30,"HRB400","HRB400",1500,42.5,1000,42.5])
param.append([250,500,30,"HRB400","HRB400",2500,42.5,1000,42.5])
param.append([250,500,30,"HRB400","HRB400",7000,42.5,500,42.5])
param.append([250,500,30,"HRB400","HRB400",8000,42.5,500,42.5])
num = 1
for p in param:
    result = beam_rect_fc(*p)
    report = report_beam_rect_fc(num,p,result)
    print(report)
    num += 1