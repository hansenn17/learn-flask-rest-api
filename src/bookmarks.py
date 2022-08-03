from flask import Blueprint, jsonify, request
import validators
from src.database import Bookmark, db
from flask_jwt_extended import get_jwt_identity, jwt_required

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")


@bookmarks.route('/', methods=['GET', 'POST'])
@jwt_required()
def bookmark():
    
    current_user = get_jwt_identity()
    
    if request.method == "POST":

        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({
                'error': 'enter valid url'
            }), 400

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                'error': 'URL already exists'
            }), 409

        bookmark = Bookmark(url=url, body=body, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()

        return jsonify({
            "id": bookmark.id,
            "url": bookmark.url,
            "short_url": bookmark.short_url,
            "visit": bookmark.visits,
            "body": bookmark.body,
            "created_at": bookmark.created_at,
            "update_at": bookmark.updated_at
        }), 201
    
    else:
        page=request.args.get('page', 1, type=int)
        per_page=request.args.get('per_page', 5, type=int)

        bookmarks = Bookmark.query.filter_by(user_id=current_user).paginate(page=page, per_page=per_page)

        data=[]

        for bookmark in bookmarks.items:
            data.append({
                "id": bookmark.id,
                "url": bookmark.url,
                "short_url": bookmark.short_url,
                "visit": bookmark.visits,
                "body": bookmark.body,
                "created_at": bookmark.created_at,
                "update_at": bookmark.updated_at
            })
        
        meta = {
            "page": bookmarks.page,
            "pages": bookmarks.pages,
            "total_count": bookmarks.total,
            "prev_page": bookmarks.prev_num,
            "next_page": bookmarks.next_num,
            "has_next": bookmarks.has_next,
            "has_prev": bookmarks.has_prev,
        }

        return jsonify({'data': data, 'meta': meta}), 200


@bookmarks.get('/<int:id>')
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({"message": "item not found"}), 404

    return jsonify({
        "id": bookmark.id,
        "url": bookmark.url,
        "short_url": bookmark.short_url,
        "visit": bookmark.visits,
        "body": bookmark.body,
        "created_at": bookmark.created_at,
        "update_at": bookmark.updated_at
    }), 200


@bookmarks.put('/<int:id>')
@bookmarks.patch('/<int:id>')
@jwt_required()
def editbookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({"message": "item not found"}), 404

    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return jsonify({
            'error': 'enter valid url'
        }), 400
    
    bookmark.url = url
    bookmark.body = body

    db.session.commit()

    return jsonify({
        "id": bookmark.id,
        "url": bookmark.url,
        "short_url": bookmark.short_url,
        "visit": bookmark.visits,
        "body": bookmark.body,
        "created_at": bookmark.created_at,
        "update_at": bookmark.updated_at
    }), 200


@bookmarks.delete('/<int:id>')
@jwt_required()
def deletebookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({"message": "item not found"}), 404

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({}), 204

@bookmarks.get("/stats")
@jwt_required()
def get_stats():
    current_user = get_jwt_identity()

    data = []

    bookmarks = Bookmark.query.filter_by(user_id = current_user).all()

    for bookmark in bookmarks:
        new_link = {
            "visits": bookmark.visits,
            "url": bookmark.url,
            "id": bookmark.id,
            "short_url": bookmark.short_url
        }

        data.append(new_link)

    return jsonify({"data": data}), 200