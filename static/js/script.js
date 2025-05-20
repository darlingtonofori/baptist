document.addEventListener('DOMContentLoaded', function() {
    // Auth form toggle
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    if (toggleBtns) {
        toggleBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const formType = this.getAttribute('data-form');
                document.getElementById('auth-form').querySelector('button').name = formType;
                document.getElementById('auth-form').querySelector('button').textContent = formType.charAt(0).toUpperCase() + formType.slice(1);
                
                toggleBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }
    
    // Create post
    const postForm = document.getElementById('create-post');
    if (postForm) {
        postForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch('/post', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addNewPost(data.post);
                    this.reset();
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }
    
    // Add comment
    const commentForms = document.querySelectorAll('.add-comment');
    if (commentForms) {
        commentForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                const postId = this.getAttribute('data-post-id');
                const content = this.querySelector('textarea').value;
                
                fetch('/comment', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `post_id=${postId}&content=${encodeURIComponent(content)}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        addNewComment(postId, data.comment);
                        this.querySelector('textarea').value = '';
                    }
                })
                .catch(error => console.error('Error:', error));
            });
        });
    }
    
    // Toggle comments
    const commentToggles = document.querySelectorAll('.post-comments-toggle');
    if (commentToggles) {
        commentToggles.forEach(toggle => {
            toggle.addEventListener('click', function() {
                const commentsSection = this.closest('.post').querySelector('.comments-section');
                commentsSection.style.display = commentsSection.style.display === 'none' ? 'block' : 'none';
            });
        });
    }
    
    // Delete post
    const deleteButtons = document.querySelectorAll('.delete-post');
    if (deleteButtons) {
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                const postId = this.getAttribute('data-post-id');
                
                if (confirm('Are you sure you want to delete this post?')) {
                    fetch(`/delete_post/${postId}`, {
                        method: 'POST'
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            document.querySelector(`.post[data-post-id="${postId}"]`).remove();
                        }
                    })
                    .catch(error => console.error('Error:', error));
                }
            });
        });
    }
    
    // Live updates for posts
    if (document.getElementById('posts-list')) {
        setInterval(fetchNewPosts, 5000); // Check for new posts every 5 seconds
    }
    
    // Add tool form
    const toolForm = document.getElementById('add-tool');
    if (toolForm) {
        toolForm.addEventListener('submit', function(e) {
            // Form will submit normally since it's a traditional form with POST
        });
    }
});

function addNewPost(post) {
    const postsList = document.getElementById('posts-list');
    const postElement = document.createElement('div');
    postElement.className = 'post';
    postElement.setAttribute('data-post-id', post.id);
    postElement.innerHTML = `
        <div class="post-header">
            <span class="post-author">${post.username}</span>
            <span class="post-date">${post.created_at}</span>
            <button class="delete-post" data-post-id="${post.id}">×</button>
        </div>
        ${post.title ? `<h3 class="post-title">${post.title}</h3>` : ''}
        <div class="post-content">${post.content}</div>
        ${post.image ? `<div class="post-image"><img src="/static/images/${post.image}" alt="Post image"></div>` : ''}
        <div class="post-footer">
            <span class="post-views">👁️ ${post.views} views</span>
            <span class="post-comments-toggle">💬 0 comments</span>
        </div>
        <div class="comments-section" style="display: none;">
            <form class="add-comment" data-post-id="${post.id}">
                <textarea placeholder="Add a comment..." required></textarea>
                <button type="submit">Comment</button>
            </form>
        </div>
    `;
    
    postsList.insertBefore(postElement, postsList.firstChild);
    
    // Add event listeners to new elements
    postElement.querySelector('.post-comments-toggle').addEventListener('click', function() {
        const commentsSection = this.closest('.post').querySelector('.comments-section');
        commentsSection.style.display = commentsSection.style.display === 'none' ? 'block' : 'none';
    });
    
    postElement.querySelector('.add-comment').addEventListener('submit', function(e) {
        e.preventDefault();
        const postId = this.getAttribute('data-post-id');
        const content = this.querySelector('textarea').value;
        
        fetch('/comment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `post_id=${postId}&content=${encodeURIComponent(content)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addNewComment(postId, data.comment);
                this.querySelector('textarea').value = '';
            }
        })
        .catch(error => console.error('Error:', error));
    });
    
    postElement.querySelector('.delete-post').addEventListener('click', function() {
        const postId = this.getAttribute('data-post-id');
        
        if (confirm('Are you sure you want to delete this post?')) {
            fetch(`/delete_post/${postId}`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if
