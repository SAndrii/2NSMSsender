#################
#### imports ####
#################
# -*- coding: utf-8 -*-

import unicodedata
import glob
from time import gmtime, strftime, localtime
from . import app
from flask import render_template, Blueprint, request, redirect, url_for, flash
from .core.send import nform, topdu, validnumber
from .core.connect2n import connector
from .forms import AddSMSForm

a = glob.glob('project\sendto\*')
s=[]
for i in a:
	s.append(i.partition('project\\sendto\\')[2])
	opt = dict(zip([i for i in range(len(a))], s))

def logger(n, m):
    from time import gmtime, strftime, localtime
    stamp = strftime('%d %b %Y %a, %H:%M:%S', localtime())
    return (stamp +  '\t' + n + '\t' + m + '\n')

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash('Error in the {} field - {}'.format(getattr(form, field).label.text, error), 'info')
 
@app.route('/')
def index():  
	form = AddSMSForm(request.form)
	return render_template('index.html', form=form, opt=opt)

@app.route('/send', methods=['GET', 'POST'])
def send():
	tel = []
	form = AddSMSForm(request.form)
	if request.method == 'POST':
		if form.validate_on_submit():
			message = request.form['message']
			s = unicodedata.name(message[0]).partition(' ')[0]
			if (s == 'LATIN' and len(message) <= 160) or (s == 'CYRILLIC' and len(message) <=70):
				pass
			else:
				flash('ERROR! message lehght must be less 160 character in english or 70 in cyrillic ', 'error')
				return render_template('index.html', form=form)
			number = request.form['number']
			if number[1:].isdigit() and validnumber(number):
				tel.append(validnumber(number))
			elif number in opt.values():
				with open('project\\sendto\\' + number, 'r') as f:
					for i in f.readlines():
						tel.append(i.strip('\n'))
					f.close()
			else:
				flash('ERROR! Invalid phone number format', 'error')
				return render_template('index.html', form=form)
			if request.form.get('checkbox'):
				dcs = 1
			else:
				dcs = 0
			for u in tel:
				status = connector((nform(topdu(u, message, dcs), sim=0)), sms=1)
				if status[0].find('*smsout') == -1:
					flash('Sending sms, please wait', 'info')
					while status[0].find('*smsout') == -1:
						status = connector((nform(topdu(u, message), sim=0)), sms=1)
				with open('logger.txt', 'a') as f:
					f.write(logger(u, message))
					f.close()
				flash('Sms was sent to ' + u, 'success')
			return redirect(url_for('index'))
			return render_template('index.html', form=form)
		else:
			flash_errors(form)
			flash('ERROR! SMS not send', 'error')
	return render_template('index.html', form=form)