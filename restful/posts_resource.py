from main import *


class PostResource(Resource):
    def get(self, post_id):
        abort_if_post_not_found(post_id)
        session = db_session.create_session()
        post = session.query(Post).get(post_id)
        return jsonify({'post': post.to_dict(
            only=('title', 'content', 'user.name',
                  'user.surname', 'string_created_date'))})


class PostListResource(Resource):
    def get(self):
        session = db_session.create_session()
        posts = session.query(Post).all()
        return jsonify({'posts': [item.to_dict(
            only=('id', 'title',
                  'user.name', 'user.surname')) for item in posts]})


def abort_if_post_not_found(post_id):
    session = db_session.create_session()
    post = session.query(Post).get(post_id)
    if not post:
        abort(404, message=f"Post {post_id} not found")
