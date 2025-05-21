document.addEventListener('DOMContentLoaded', function() {
    const eventSource = new EventSource('/stream');
    const postsContainer = document.getElementById('posts-list');
    const noPostsElement = document.querySelector('.no-posts');

    eventSource.onmessage = function(e) {
        const post = JSON.parse(e.data);
        
        if (noPostsElement) noPostsElement.remove();

        if (!document.querySelector(`[data-post-id="${post.id}"]`)) {
            const canDelete = CURRENT_USER.is_authenticated && 
                            (CURRENT_USER.is_admin || CURRENT_USER.id === post.user_id);
            
            const postHTML = `
            <div class="post" data-post-id="${post.id}">
                <div class="post-header">
                    <span class="post-author">${post.username}</span>
                    <span class="post-date">${post.created_at}</span>
                    ${canDelete ? `<button class="delete-post" data-post-id="${post.id}">×</button>` : ''}
                </div>
                ${post.title ? `<h3 class="post-title">${post.title}</h3>` : ''}
                <div class="post-content">${post.content}</div>
                ${post.image ? `
                <div class="post-image">
                    <img src="/static/images/${post.image}" alt="Post image">
                </div>` : ''}
                <div class="post-footer">
                    <span class="post-views">👁️ ${post.views} views</span>
                    <span class="post-comments-toggle">💬 ${post.comments_count} comments</span>
                </div>
                <div class="comments-section" style="display: none;">
                    ${CURRENT_USER.is_authenticated ? `
                    <form class="add-comment" data-post-id="${post.id}">
                        <textarea placeholder="Add a comment..." required></textarea>
                        <button type="submit">Comment</button>
                    </form>` : ''}
                </div>
            </div>`;
            
            postsContainer.insertAdjacentHTML('afterbegin', postHTML);
            setupPostInteractions(postsContainer.firstChild);
        }
    };

    function setupPostInteractions(postElement) {
        // Toggle comments
        postElement.querySelector('.post-comments-toggle')?.addEventListener('click', function() {
            const commentsSection = postElement.querySelector('.comments-section');
            commentsSection.style.display = commentsSection.style.display === 'none' ? 'block' : 'none';
        });

        // Delete post
        postElement.querySelector('.delete-post')?.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this post?')) {
                fetch(`/delete_post/${this.dataset.postId}`, { method: 'POST' })
                    .then(response => response.json())
                    .then(data => data.success && postElement.remove());
            }
        });

        // Add comment
        postElement.querySelector('.add-comment')?.addEventListener('submit', function(e) {
            e.preventDefault();
            const content = this.querySelector('textarea').value;
            fetch('/comment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `post_id=${this.dataset.postId}&content=${encodeURIComponent(content)}`
            }).then(response => response.json())
              .then(data => data.success && (this.querySelector('textarea').value = ''));
        });
    }

    // Initialize existing posts
    document.querySelectorAll('.post').forEach(setupPostInteractions);

    // Post form submission
    document.getElementById('create-post')?.addEventListener('submit', function(e) {
        e.preventDefault();
        fetch('/post', {
            method: 'POST',
            body: new FormData(this)
        }).then(response => response.json())
          .then(data => {
              if (data.success) this.reset();
              else document.getElementById('post-error').textContent = data.error || 'Error';
          });
    });
});
