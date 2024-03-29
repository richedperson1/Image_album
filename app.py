from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError,DatabaseError
from sqlalchemy.sql import func
from geoalchemy2.types import Geography

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photos.db'  # Using SQLite database

db = SQLAlchemy(app)

# Define models
class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement = True)
    title = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    albumRelation = relationship('AlbumPhoto', secondary='album_photo', back_populates='albums', cascade='all, delete')

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'month': self.month
        }
        
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement = True)
    url = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    people = db.Column(db.JSON)
    location = db.Column(Geography(geometry_type='POINT', management=True))
    photosRelation= relationship('AlbumPhoto', secondary='album_photo', back_populates='albums', cascade='all, delete')
    def serialize(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'people': self.people,
            'location': self.location,
        }

class AlbumPhoto(db.Model):
    album_id = db.Column(db.Integer, db.ForeignKey('album.id', ondelete='CASCADE'), nullable=False)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id', ondelete='CASCADE'), nullable=False)
    id = db.Column(db.Integer, primary_key=True,autoincrement = True)
    # album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    # photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    is_main = db.Column(db.Boolean, default=False)

# CRUD APIs for albums
@app.route('/albums', methods=['GET'])
def get_albums():
    albums = Album.query.all()
    return jsonify([album.serialize() for album in albums])

@app.route('/albums/<int:album_id>', methods=['GET'])
def get_album(album_id):
    album = Album.query.get(album_id)
    if not album:
        return jsonify({'error': 'Album not found'}), 404
    return jsonify(album.serialize())

@app.route('/albums', methods=['POST'])
def create_album():
    data = request.get_json()
    album = Album(title=data['title'], year=data['year'], month=data['month'])
    db.session.add(album)
    db.session.commit()
    return jsonify(album.serialize()), 201

@app.route('/albums/<int:album_id>', methods=['PUT'])
def update_album(album_id):
    album = Album.query.get(album_id)
    if not album:
        return jsonify({'error': 'Album not found'}), 404
    data = request.get_json()
    album.title = data['title']
    album.year = data['year']
    album.month = data['month']
    db.session.commit()
    return jsonify(album.serialize())

@app.route('/albums/<int:album_id>', methods=['DELETE'])
def delete_album(album_id):
    album = Album.query.get(album_id)
    if not album:
        return jsonify({'error': 'Album not found'}), 404
    db.session.delete(album)
    db.session.commit()
    return jsonify({'message': 'Album deleted successfully'})

# CRUD APIs for photos
@app.route('/get_photos', methods=['GET'])
def get_photos():
    photos = Photo.query.all()
    return jsonify([photo.serialize() for photo in photos])

@app.route('/photos/<int:photo_id>', methods=['GET'])
def get_photo(photo_id):
    photo = Photo.query.get(photo_id)
    if not photo:
        return jsonify({'error': 'Photo not found'}), 404
    return jsonify(photo.serialize())

@app.route('/upload_photos', methods=['POST'])
def upload_photo():
    """
    ! Assuming that album name and relative meta data is also given while uploading the images. Because firstly album is created then we give provision for user to upload image to perticular album.
    
    It might chance their is same name album occur multiple album will occur multiple times.
    """
    try:
        data = request.get_json()
        albumName = data.get("albumTitle")
        albumTitle = data.get("albumTitle")
        albumYear = data.get("albumYears")
        albumMonth = data.get("albumMonth")
        
        photo = Photo(url=data['url'], title=data['title'], people=data.get('people'), location=data.get('location'))
        db.session.add(photo)
        db.session.commit()
        return jsonify({"result":"Image is uploaded successfully"}), 202

    except IntegrityError as e:
        return jsonify({"result":f"File not uploaded due integrity issue : {e}"}),502
@app.route('/photos/<int:photo_id>', methods=['PUT'])
def update_photo(photo_id):
    photo = Photo.query.get(photo_id)
    if not photo:
        return jsonify({'error': 'Photo not found'}), 404
    data = request.get_json()
    photo.title = data['title']
    photo.people = data.get('people')
    photo.location = data.get('location')
    db.session.commit()
    return jsonify(photo.serialize())

@app.route('/photos/<int:photo_id>', methods=['DELETE'])
def delete_photo(photo_id):
    photo = Photo.query.get(photo_id)
    if not photo:
        return jsonify({'error': 'Photo not found'}), 404
    db.session.delete(photo)
    db.session.commit()
    return jsonify({'message': 'Photo deleted successfully'})

# Helper methods
def paginate(query, page, per_page):
    return query.limit(per_page).offset((page - 1) * per_page)

if __name__ == '__main__':
    app.run(debug=True)
