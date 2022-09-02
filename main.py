import datetime
import os

from flask import Flask, request, redirect, url_for, flash, render_template
from peewee import *
from playhouse.flask_utils import object_list

db = SqliteDatabase('album.db')


class Photo(Model):
    id = IntegerField(primary_key=True)
    name = CharField()
    timestamp = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


if db.connect():
    print('数据库连接成功')

db.create_tables([Photo])
app = Flask(__name__)
app.secret_key = 'Simon Yen is the best!'


@app.route('/')
def home():
    photos = Photo.select().order_by(Photo.timestamp.desc())
    return object_list(
        'home.html',
        query=photos,
        context_variable='photos',
        paginate_by=10
    )


@app.post('/upload')
def upload():
    image = request.files.get('images')
    if image is None:
        flash('请上传图片！')
        return redirect(url_for('home'))
    photo = Photo()
    photo.name = image.filename
    flash('上传成功。')
    image.save(os.path.join('.', 'static', image.filename))
    photo.save()
    return redirect(url_for('home'))


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    photos = Photo.select().order_by(Photo.timestamp.desc())
    return render_template('admin.html', photos=photos)


@app.route('/delete/<int:id>')
def delete(id):
    p = Photo.select().where(Photo.id == id).get()
    if os.path.isfile(os.path.join('.', 'static', p.name)):
        os.remove(os.path.join('.', 'static', p.name))
    Photo.delete().where(Photo.id == id).execute()
    flash('删除成功。')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
