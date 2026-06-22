document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss flash messages
    document.querySelectorAll('.snap-message').forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            msg.style.transition = 'all 0.3s ease';
            setTimeout(() => msg.remove(), 300);
        }, 4000);
    });

    // AJAX like toggle
    document.querySelectorAll('.like-form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = form.querySelector('.like-btn');
            const icon = btn.querySelector('.action-icon');
            const countEl = btn.querySelector('.like-count') || btn.querySelector('span:last-child');

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    btn.classList.toggle('liked', data.liked);
                    icon.textContent = data.liked ? '❤️' : '🤍';
                    if (countEl) countEl.textContent = data.like_count;

                    btn.style.transform = 'scale(1.2)';
                    setTimeout(() => { btn.style.transform = ''; }, 200);
                }
            } catch (err) {
                form.submit();
            }
        });
    });

    // AJAX follow toggle
    document.querySelectorAll('.follow-form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = form.querySelector('.follow-btn, .snap-btn');

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    const following = data.following;

                    if (btn.classList.contains('snap-btn-primary')) {
                        btn.classList.remove('snap-btn-primary');
                        btn.classList.add('snap-btn-outline');
                    } else if (btn.classList.contains('snap-btn-outline')) {
                        btn.classList.remove('snap-btn-outline');
                        btn.classList.add('snap-btn-primary');
                    }

                    btn.textContent = following ? 'Following' : 'Follow';

                    const followerCount = document.querySelector('.follower-count');
                    if (followerCount && data.follower_count !== undefined) {
                        followerCount.textContent = data.follower_count;
                    }
                }
            } catch (err) {
                form.submit();
            }
        });
    });
});
