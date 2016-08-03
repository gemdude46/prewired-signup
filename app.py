from flask import Flask, Response, request, redirect
from threading import Lock
import datetime, socket, urllib, os, time, json

reg_lock = Lock()

fields = (
    'name',
    'email',
    'mobile',
    'dietary',
    'medication',
    'illnesses',
    'website',
    'birthmonth',
    'disabilities',
    'postcode',
    'gender',
    'ethnicity',
    'religion',
    'EC1name',
    'EC1relation',
    'EC1phone',
    'EC1email',
    'EC2name',
    'EC2relation',
    'EC2phone',
    'EC2email',
    'photo',
    'registeredby',
    'ts'
)

app = Flask(__name__)

def cut_w_s(t):
    return ' '.join(t.split())

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead < 0:
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def get_member_list():
    with reg_lock:
        f = open('members', 'r')
        c = [i.strip().split('\t') for i in f.readlines() if i.strip()]
        f.close()
    return c

def get_next_pw():
    return '{0.day}/{0.month}/{0.year}'.format(next_weekday(datetime.date.today(), 2))


def coming_much(p):
    if not p.strip():
        return 'Please enter your name.'
    p = ' '.join(p.split()).lower()
    if p not in [i[0].lower() for i in get_member_list()]:
        return ('Sorry, but it appeares you are not on our list of members.<br>'+
                'Please check for typos or <a href="/register">register</a> if you haven\'t already.')
    while not os.path.exists(get_next_pw()):
        try:
            os.makedirs(get_next_pw())
        except:
            time.sleep(0.1)
    
    f = open(os.path.join(get_next_pw(), p),'w')
    f.write(str(time.time()))
    f.close()
    
    return 'success'
        

@app.route('/')
def index():
    f = open('signup.html', 'r')
    c = f.read()
    f.close()
    m = '['+(','.join(['"{}"'.format(i[0]) for i in get_member_list()]))+']'
    c=c.replace('{d}', get_next_pw())
    c=c.replace('{m}', m)
    if 'err' in request.args:
        em = '<div style="color:white;background-color:red;">{}</div>'.format(request.args['err'])
    else:
        em = '<p style="font-size:20px;">First time? Please <a href="/register" style="font-size:20px;">register</a>.</p>'
    c=c.replace('{err}',em)
    return c

@app.route('/$')
def ds():
    f = open('signup.$', 'r')
    c = f.read()
    f.close()
    return Response(c, mimetype='text/plain')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        f = open('register.html', 'r')
        c = f.read()
        f.close()
        return c.replace('*:', '<font color=red>*</font>:').replace('---', '&nbsp;'*4).replace('{req}',('',
        '<div id=req>Please make sure you fill out all the required fields.</div>')['req' in request.args])
    else:
        if (request.form.get('update','off') == 'on' and request.form.get('storage','off') == 'on' and request.form.get('name') and
            '@' in request.form.get('email','') and request.form.get('EC1name') and request.form.get('EC1relation') and
            request.form.get('EC1phone') and request.form.get('EC1email') and request.form.get('EC2name') and
            request.form.get('EC2relation') and request.form.get('EC2phone') and request.form.get('EC2email') and request.form.get('photo')
            in ('yes','no') and request.form.get('registeredby') in ('parent','attendee')):
            
            if request.form['name'].lower() in [i[0] for i in get_member_list()]:
                return ('<!DOCTYPE html><html><head><title>Redirecting...</title><script type="text/'+
                'javascript">location.href="/eviltwin";</script></head><body><h1>Redirecting...'+
                '</h1>If you are not redirected, <a href="/eviltwin">click here</a>.</body></html>')
            
            with reg_lock:
                f = open('members', 'a')
                f.write(('\t'.join([cut_w_s((request.form.get(field),str(time.time()))
                [field=='ts']or'-')for field in fields]).lower()+'\n').encode('utf-8'))
                f.close()
            
            f = open('registered.html', 'r')
            c = f.read()
            f.close()
            return c
        else:
            return ('<!DOCTYPE html><html><head><title>Redirecting...</title><script type="text/'+
            'javascript">location.href="/register?req";</script></head><body><h1>Redirecting...'+
            '</h1>If you are not redirected, <a href="/register?req">click here</a>.</body></html>')
                

@app.route('/eviltwin')
def evil_twin():
    f = open('evil.html', 'r')
    c = f.read()
    f.close()
    return c

@app.route('/ls')
def ls():
    f = open('who.html', 'r')
    c = f.read()
    f.close()
    c=c.replace('{d}', get_next_pw())
    return c

@app.route('/ls$')
def lsds():
    f = open('who.$', 'r')
    c = f.read()
    f.close()
    return Response(c, mimetype='text/plain')

@app.route('/coming/old')
def coming_old():
    msg = coming_much(request.args['p'])
    if msg == 'success':
        f = open('coming_old_success.html', 'r')
        c = f.read()
        f.close()
        return c
    else:
        return redirect('/?err='+urllib.quote(msg))

@app.route('/coming/new')
def coming_new():
    return Response(coming_much(request.args['p']), mimetype='text/plain')

@app.route('/coming/who')
def coming_who():
    if not os.path.exists(get_next_pw()):
        return Response('[]', mimetype='application/json')
    return Response(json.dumps(os.listdir(get_next_pw())), mimetype='application/json')

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8",80))
hostip=s.getsockname()[0]
s.close()

app.run(port=1337, host=hostip)
