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


with app.app_context():
    db.create_all()

# Define models
class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement = True)
    title = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    albumRelation = db.relationship('AlbumPhoto', secondary='album_photo', back_populates='albums', cascade='all, delete')

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
    location = db.Column(Geography(geometry_type='POINT'))
    photosRelation= db.relationship('AlbumPhoto', secondary='album_photo', back_populates='albums', cascade='all, delete')
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
@app.route('/albums_list', methods=['GET'])
def get_albums():
    try:
        albums = Album.query.all()
        return jsonify([album.serialize() for album in albums])
    except Exception as err:
        return jsonify({"result":"Result not found"})

@app.route('/albums/<int:album_id>', methods=['GET'])
def get_album(album_id):
    try:
        
        album = Album.query.filter(Album.id==album_id).first()
        if not album:
            return jsonify({'error': 'Album not found'}), 404
        return jsonify(album.serialize())   
    except Exception as err:
        return jsonify({"result":"Result not found"})
    
@app.route('/create_albums', methods=['POST'])
def create_album():
    try:
        data = request.json
        album = Album(title=data['title'], year=data['year'], month=data['month'])
        db.session.add(album)
        db.session.commit()
        return jsonify(album.serialize()), 201
    except Exception as err:
        return jsonify({"result":"Result not found"})

@app.route('/update_albums', methods=['PUT'])
def update_album():
    try:
        data = request.json
        album = Album.query.filter(Album.id==data["album_id"]).first()
        if not album:
            return jsonify({'error': 'Album not found'}), 404
        data = request.get_json()
        album.title = data['title']
        album.year = data['year']
        album.month = data['month']
        db.session.commit()
        return jsonify(album.serialize())
    except Exception as err:
        return jsonify({"result":"Result not found"})

@app.route('/albums/<int:album_id>', methods=['DELETE'])
def delete_album(album_id):
    try:
        data = request.json
        album = Album.query.filter(Album.id==data["album_id"]).first()
        if not album:
            return jsonify({'error': 'Album not found'}), 404
        db.session.delete(album)
        db.session.commit()
        return jsonify({'message': 'Album deleted successfully'})
    
    except Exception as err:
        return jsonify({"result":"Result not found"})
# CRUD APIs for photos
@app.route('/get_photos', methods=['GET'])
def get_photos():
    try:
        photos = Photo.query.all()
        return jsonify([photo.serialize() for photo in photos])
    
    except Exception as err:
        return jsonify({"result":"Result not found"})
    
@app.route('/photos/<int:photo_id>', methods=['GET'])
def get_photo(photo_id):
    try:
        photo = Photo.query.filter(Photo.id == photo_id).first()
        if not photo:
            return jsonify({'error': 'Photo not found'}), 404
        return jsonify(photo.serialize())

    except NameError as e:
        return jsonify({"result":f"Please enter proper name :  {e}"}),401
    
    except Exception as e:
        return jsonify({"result":f"Please enter proper name :  {e}"}),404
    
    
@app.route('/upload_photos', methods=['POST'])
def upload_photo():
    """
    ! Assuming that album name and relative meta data is also given while uploading the images. Because firstly album is created then we give provision for user to upload image to perticular album.
    
    It might chance their is same name album occur multiple album will occur multiple times.
    """
    
    try:
        # First storing image data then storing the album data
        
        # This block of code is handling the process of uploading a photo to one or more albums in a
        # application.
        
        photo = Photo(url=data['url'], title=data['title'], people=data.get('people'), location=data.get('location'))
        db.session.add(photo)
        db.session.commit()
        
        # This block of code is handling the process of uploading a photo to one or more albums.
        
        
        data = request.get_json()
        albumName = data.get("albumTitle")
        albumTitle = data.get("albumTitle")
        albumYear = data.get("albumYears")
        albumMonth = data.get("albumMonth")
        
        album4uploadList = Album.query.filter(Album.title==albumTitle).filter(Album.year==albumYear).filter(Album.month==albumMonth).all()
        
        albumIds = []
        
        for albumObj in album4uploadList:
            albumIds.append(albumObj.id)
            
        
        for albumId in albumIds:
            newAlbumPhotoEntry = AlbumPhoto(album_id = albumId,photo_id =  photo.id)
            db.session.add(newAlbumPhotoEntry)
            
        db.session.commit()
        
        return jsonify({"result":"Image is uploaded successfully"}), 202

    except IntegrityError as e:
        return jsonify({"result":f"File not uploaded due integrity issue : {e}"}),502

    except DatabaseError as e:
        return jsonify({"result":f"File not uploaded due DatabaseError : {e}"}),502
    
    except Exception as e:
        return jsonify({"result":f"File not uploaded due DatabaseError : {e}"}),502
    
    
@app.route('/photos/<int:photo_id>', methods=['PUT'])
def update_photo(photo_id):
    # This block of code defines a route in a application to update a specific photo in the
    # database.
    
    try:
        photo = Photo.query.filter(Photo.id == photo_id).first()
        if not photo:
            return jsonify({'error': 'Photo not found'}), 404
        data = request.json
        photo.title = data['title']
        photo.people = data.get('people')
        photo.location = data.get('location')
        db.session.commit()
        return jsonify(photo.serialize())
    
    except Exception as err:
        return jsonify({"result":"Result not found"})
    
@app.route('/photos/<int:photo_id>', methods=['DELETE'])
def delete_photo(photo_id):
    try:
        # This block of code defines a route in the application to delete a specific photo from the
        # database. Here's what each step does:
        
        photo = Photo.query.get(photo_id)
        if not photo:
            return jsonify({'error': 'Photo not found'}), 404
        db.session.delete(photo)
        db.session.commit()
        return jsonify({'message': 'Photo deleted successfully'})
    
    except Exception as err:
        return jsonify({"result":"Result not found"})
# Helper methods
def paginate(query, page, per_page):
    return query.limit(per_page).offset((page - 1) * per_page)

if __name__ == '__main__':
    app.run(debug=True)
