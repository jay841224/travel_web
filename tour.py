from flask import Flask, render_template, redirect, url_for, request, session
from flask import flash, jsonify
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import googlemaps
import datetime
import json
from flask_migrate import Migrate, MigrateCommand
from sqlalchemy.sql.expression import func
from flask_script import Manager

app = Flask(__name__)
app.secret_key = 'jay011089'
app.permanent_session_lifetime = timedelta(minutes=600)
# sql
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ertuuktkzrmdyo:23ed549c19ea7b9919bd6ef6bb7c2e82aeac506db1260e0395cb92e16c2f9b88@ec2-54-157-78-113.compute-1.amazonaws.com:5432/ddk3lh7bab56tv'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
# google maps
gmaps = googlemaps.Client(key='AIzaSyCyeAdNWCl74p91fi5n8RzfBzIq06g6Zp8')


# database for user
class Users(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    # 連結location_information
    location = db.relationship(
        'Location_information', backref='user_bf')
    dates = db.relationship('Dates', backref='date_bf')
    playList = db.relationship('PlayList', backref='play_bf')

    def __init__(self, user_name, email):
        self.user_name = user_name
        self.email = email


# database for location
# !!connect to user!!
class Location_information(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users._id'))
    inform = db.Column(db.PickleType)  # {name: , lat: , lng: }
    placeId = db.Column(db.String(300))

    def __repr__(self):
        return '{}'.format(self.inform['id'])


class Dates(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users._id'))
    dateId = db.Column(db.DateTime, unique=True)
    playList = db.relationship('PlayList', backref='playList_bf')

    def __repr__(self):
        return '{}'.format(self.dateId)


class PlayList(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users._id'))
    date = db.Column(db.DateTime, db.ForeignKey('dates.dateId'))
    startTime = db.Column(db.PickleType)
    index = db.Column(db.PickleType)
    tranList = db.Column(db.PickleType)
    cost = db.Column(db.PickleType)
    tranTime = db.Column(db.PickleType)
    note = db.Column(db.PickleType)
    stayTime = db.Column(db.PickleType)
    indexPlaceName = db.Column(db.PickleType)
    costTran = db.Column(db.PickleType)


@app.route('/', methods=["POST", "GET"])
def home():
    return render_template('home.html')


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        name = request.form['nm']
        email = request.form['email']
        # session.permanent = False

        found_user = Users.query.filter_by(user_name=name).first()
        if found_user and found_user.email == email:
            session['email'] = email
            session['user'] = name
            return redirect(url_for('choose'))
        else:
            flash('wrong user name or email!')
    else:
        if 'user' in session:
            return redirect(url_for('user'))
    return render_template('login.html')


@app.route('/choose')
def choose():
    return render_template('choose.html')


@app.route('/choose_day')
def choose_day():
    U = Users.query.filter_by(user_name=session['user']).first()
    if Dates.query.filter_by(user_id=U._id).first():
        flash('你已經選取過日期，請按確定繼續')
    return render_template('choose_day.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if 'user' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form['nm']
        email = request.form['email']
        if Users.query.filter_by(user_name=name).first():
            flash('the user name have been used!', 'info')
        else:
            usr = Users(name, email)
            db.session.add(usr)
            db.session.commit()  # add commit when you change database
            return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/user')
def user():
    if 'user' in session:
        flash('You logged in!', 'info')
        name = session['user']
        email = session['email']
        return render_template('user.html', name=name, email=email)
    else:
        return redirect(url_for('login'))
    # return f'<h1>{usr}</h1>'


@app.route('/logout')
def logout():
    if 'user' in session:
        name = session['email']
        flash('You logged out! {}'.format(name), 'message')
    session.pop('user', None)  # remove session['user']
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/view')
def view():
    # U = Users.query.filter_by(user_name=session['user']).first()  # get user
    # startDate = datetime.datetime(2020, 3, 20)
    # a = Dates.query.filter_by(user_id=U._id, dateId=startDate).update({'playList': 'jjj'})
    # a = Dates.query.filter_by(user_id=U._id, dateId=startDate).first()
    # print(a.playList)
    return render_template('view.html', values=Users.query.all())


@app.route('/map', methods=['POST', 'GET'])
def map():
    if 'user' not in session:
        flash('You should login first!')
        return redirect(url_for('login'))
    U = Users.query.filter_by(user_name=session['user']).first()  # get user
    resultList = []
    try:
        for data in U.location:  # 輸出已加入的位置
            if data.inform['photo'] == 'https://maps.gstatic.com/tactile/pane/default_geocode-2x.png':
                resultList.append(
                    [data.inform['name'], data.inform['photo'], data.inform['id']])
            else:
                resultList.append([data.inform['name'], 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=200&photoreference=' +
                                   data.inform['photo'] + '&key=AIzaSyCyeAdNWCl74p91fi5n8RzfBzIq06g6Zp8', data.inform['id']])
    except:
        pass
    return render_template('map.html', resultList=resultList)


@app.route('/addMap', methods=['POST', 'GET'])
def add_map():
    U = Users.query.filter_by(user_name=session['user']).first()  # get user
    placeId = request.args.get('placeId')
    placeLocation_lat = request.args.get('placeLocation_lat')
    placeLocation_lng = request.args.get('placeLocation_lng')
    from getLocation import get_detail
    location_detail = get_detail(placeId)
    # 增加緯度
    location_detail['lat'] = placeLocation_lat
    location_detail['lng'] = placeLocation_lng
    # add detail to database
    In = Location_information(inform=location_detail,
                              placeId=location_detail['id'], user_bf=U)
    db.session.add(In)
    db.session.commit()
    return jsonify(result=location_detail['name'],
                   photo=location_detail['photo'],
                   id=location_detail['id'])


@app.route('/delMap', methods=['POST', 'GET'])
def del_map():
    U = Users.query.filter_by(user_name=session['user']).first()  # get user
    placeId = request.args.get('placeId')
    data = Location_information.query.filter_by(
        placeId=placeId, user_id=U._id).first()
    lat = data.inform['lat']
    lng = data.inform['lng']
    db.session.delete(data)
    db.session.commit()
    return jsonify(placeId=placeId, lat=lat, lng=lng)


@app.route('/test')
def test():
    return render_template('try.html')


@app.route('/planning')
def planning():
    if 'user' not in session:
        flash('You should login first!')
        return redirect(url_for('login'))
    U = Users.query.filter_by(user_name=session['user']).first()  # get user

    resultList = []
    for data in U.location:  # 輸出已加入的位置
        if data.inform['photo'] == 'https://maps.gstatic.com/tactile/pane/default_geocode-2x.png':
            resultList.append(
                [data.inform['name'], data.inform['photo'], data.inform['id']])
        else:
            resultList.append([data.inform['name'], 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=200&photoreference=' +
                               data.inform['photo'] + '&key=AIzaSyCyeAdNWCl74p91fi5n8RzfBzIq06g6Zp8', data.inform['id']])
    # 傳送設定的第一天
    first_day = Dates.query.filter_by(user_id=U._id).first().dateId
    allDays = []
    all_day = Dates.query.filter_by(user_id=U._id).all()
    for d in all_day:
        year = d.dateId.strftime("%Y")
        month = d.dateId.strftime("%m")
        date = d.dateId.strftime("%d")
        this_date_format = {'year': year, 'month': month, 'date': date}
        allDays.append(this_date_format)
    # 最大天數
    max_days = len(Dates.query.filter_by(user_id=U._id).all())
    return render_template('planning.html', resultList=resultList,
                           allDays=allDays,
                           first_date_format=allDays[0],
                           max_days=max_days)


@app.route('/cal', methods=['POST', 'GET'])
def cal():
    time = request.args.get('time')
    print(time)
    return jsonify(a='123')


@app.route('/search', methods=['POST', 'GET'])
def search():
    placeId = request.args.get('placeId')
    data = Location_information.query.filter_by(placeId=placeId).first()
    print(data.inform['lat'], data.inform['lng'])
    lat = data.inform['lat']
    lng = data.inform['lng']
    name = data.inform['name']
    return jsonify(lat=lat, lng=lng, placeId=placeId, placeName=name)


@app.route('/addDates', methods=['POST', 'GET'])
def addDates():
    startDate = request.args.get('startDate')  # 3/20/2020
    endDate = request.args.get('endDate')
    startDate = startDate.split('/')
    endDate = endDate.split('/')
    startDate = datetime.datetime(int(startDate[2]), int(startDate[0]),
                                  int(startDate[1]))
    endDate = datetime.datetime(int(endDate[2]), int(endDate[0]),
                                int(endDate[1]))

    if startDate:
        U = Users.query.filter_by(user_name=session['user']).first()

        while Dates.query.filter_by(user_id=U._id).first():
            db.session.delete(Dates.query.filter_by(user_id=U._id).first())
        db.session.commit()
        while PlayList.query.filter_by(user_id=U._id).first():
            db.session.delete(PlayList.query.filter_by(user_id=U._id).first())
        db.session.commit()

        # 加入選定日期database
        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days) + 1):
                yield start_date + datetime.timedelta(n)

        for single_date in daterange(startDate, endDate):
            if Dates.query.filter_by(user_id=U._id, dateId=single_date).first():
                pass
            else:
                st = Dates(dateId=single_date, date_bf=U)
                db.session.add(st)
                db.session.commit()
    else:
        pass
    return jsonify(1)


@app.route('/save_playList', methods=['POST', 'GET'])
def save_playList():
    U = Users.query.filter_by(user_name=session['user']).first()
    index = request.args.getlist('index')
    indexTime = request.args.getlist('indexTime')
    note = request.args.getlist('note')
    stayTime = request.args.getlist('stayTime')
    cost = request.args.getlist('cost')
    tranList = request.args.getlist('tranList')
    toDay = request.args.get('toDay')  # 日期_id
    indexPlaceName = request.args.getlist('indexPlaceName')
    costTran = request.args.getlist('costTran')
    tranTime = request.args.getlist('tranTime')
    print(878888888)
    print(tranList)
    D = Dates.query.filter_by(date_bf=U).all()
    D = D[int(toDay) - 1]
    if PlayList.query.filter_by(play_bf=U, playList_bf=D).first():
        while PlayList.query.filter_by(play_bf=U, playList_bf=D).first():
            db.session.delete(PlayList.query.filter_by(
                play_bf=U, playList_bf=D).first())
    newList = PlayList(play_bf=U, playList_bf=D, startTime=indexTime,
                       index=index, tranList=tranList, cost=cost,
                       tranTime=tranTime, note=note, stayTime=stayTime,
                       indexPlaceName=indexPlaceName, costTran=costTran)
    db.session.add(newList)
    db.session.commit()

    return jsonify(1)


@app.route('/change_day', methods=['POST', 'GET'])
def change_day():
    U = Users.query.filter_by(user_name=session['user']).first()
    toDay = request.args.get('toDay')
    D = Dates.query.filter_by(date_bf=U).all()
    for l in D:
        print(l)
    D = D[int(toDay) - 1]

    play = PlayList.query.filter_by(play_bf=U, playList_bf=D).first()
    print(play)
    if play:
        return jsonify(indexTime=play.startTime,
                       index=play.index, tranList=play.tranList, cost=play.cost,
                       note=play.note, stayTime=play.stayTime,
                       indexPlaceName=play.indexPlaceName,
                       costTran=play.costTran,
                       tranTime=play.tranTime)
    else:
        return jsonify(indexTime=[],
                       index=[], tranList=[], cost=[],
                       note=[], stayTime=[], costTran=[],
                       tranTime=[])


@app.route('/show_travel', methods=['POST', 'GET'])
def show_travel():
    U = Users.query.filter_by(user_name=session['user']).first()
    all_day = Dates.query.filter_by(user_id=U._id).all()
    index = []
    note = []
    tranList = []
    stayTime = []
    indexTime = []
    indexPlaceName = []

    for date in all_day:
        play = PlayList.query.filter_by(play_bf=U, playList_bf=date).first()
        try:
            index.append(play.index)
            note.append(play.note)
            tranList.append(play.tranList)
            stayTime.append(play.stayTime)
            indexTime.append(play.startTime)
            indexPlaceName.append(play.indexPlaceName)
        except:
            index.append([])
            note.append([])
            tranList.append([])
            stayTime.append([])
            indexTime.append([])
            indexPlaceName.append([])
    return jsonify(index=index, note=note,
                   tranList=tranList, stayTime=stayTime,
                   indexTime=indexTime,
                   indexPlaceName=indexPlaceName)


@app.route('/final')
def final():
    return render_template('final.html')



if __name__ == '__main__':
    db.create_all()
    manager.run()
    app.run(debug=True)
