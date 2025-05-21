# Add these imports at the top
import time
import json
from flask import Response

# ... [keep all your existing code exactly as is until the routes section]

# Add this new route before the if __name__ block
@app.route('/stream')
def stream():
    def event_stream():
        last_id = Post.query.order_by(Post.id.desc()).first().id if Post.query.count() > 0 else 0
        while True:
            new_posts = Post.query.filter(Post.id > last_id).order_by(Post.created_at.asc()).all()
            for post in new_posts:
                last_id = post.id
                data = {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'image': post.image,
                    'username': post.author.username,
                    'created_at': post.created_at.strftime('%Y-%m-%d %H:%M'),
                    'views': post.views,
                    'comments_count': len(post.comments),
                    'user_id': post.user_id
                }
                yield f"data: {json.dumps(data)}\n\n"
            time.sleep(1)
    
    return Response(event_stream(), mimetype="text/event-stream")

# ... [keep all your other existing routes exactly as they are]

if __name__ == '__main__':
    app.run(debug=True)
