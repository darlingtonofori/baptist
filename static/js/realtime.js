document.addEventListener('DOMContentLoaded', function() {
    const eventSource = new EventSource('/stream');
    const postsContainer = document.querySelector('#posts-container'); // Make sure your HTML has this
    
    eventSource.onmessage = function(e) {
        const post = JSON.parse(e.data);
        
        // Create HTML for new post
        const postHTML = `
            <div class="post" id="post-${post.id}">
                <h3>${post.title}</h3>
                ${post.image ? `<img src="/static/images/${post.image}" alt="Post image">` : ''}
                <p>${post.content}</p>
                <small>Posted by ${post.username} at ${post.created_at}</small>
            </div>
        `;
        
        // Prepend new post (or append if you prefer)
        postsContainer.insertAdjacentHTML('afterbegin', postHTML);
    };
    
    eventSource.onerror = function() {
        console.log("EventSource failed, reconnecting...");
        setTimeout(() => {
            eventSource.close();
            this.eventSource = new EventSource('/stream');
        }, 1000);
    };
});
