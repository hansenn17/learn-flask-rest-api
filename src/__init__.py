from flask import Flask, jsonify, redirect
import os
from src.auth import auth
from src.bookmarks import bookmarks
from src.database import db, Bookmark
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_relative_config=True
    )

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DATABASE_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=os.environ.get(
                "SQLALCHEMY_TRACK_MODIFICATIONS"),
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY')
        )
    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)

    migrate = Migrate(app, db)

    # with app.app_context():
    #     db.create_all()

    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    @app.get('/<short_url>')
    def redirect_to_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()

        if bookmark:
            bookmark.visits = bookmark.visits + 1
            db.session.commit()

            return redirect(bookmark.url)

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def handle_500(e):
        return jsonify({'error': 'something unexpected happened'}), 500

    return app
