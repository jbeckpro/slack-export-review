// Search functionality for Slack export HTML
document.addEventListener('DOMContentLoaded', function() {
    // Channel search on index page
    const channelSearch = document.getElementById('channelSearch');
    if (channelSearch) {
        channelSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const channelCards = document.querySelectorAll('.channel-card');
            
            channelCards.forEach(card => {
                const channelName = card.getAttribute('data-channel-name') || '';
                const channelText = card.textContent.toLowerCase();
                
                if (channelName.includes(searchTerm) || channelText.includes(searchTerm)) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });
        });
    }

    // Message search on channel pages
    const messageSearch = document.getElementById('messageSearch');
    if (messageSearch) {
        messageSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const messages = document.querySelectorAll('.message');
            
            messages.forEach(message => {
                const messageText = message.textContent.toLowerCase();
                const userName = message.getAttribute('data-user') || '';
                
                if (messageText.includes(searchTerm) || userName.includes(searchTerm)) {
                    message.classList.remove('hidden');
                } else {
                    message.classList.add('hidden');
                }
            });
            
            // Hide/show channel sections in combined view if no messages are visible
            const channelSections = document.querySelectorAll('.channel-section');
            channelSections.forEach(section => {
                const visibleMessages = section.querySelectorAll('.message:not(.hidden)');
                if (visibleMessages.length > 0) {
                    section.classList.remove('hidden');
                } else {
                    section.classList.add('hidden');
                }
            });
        });
    }

    // Smooth scrolling for channel navigation in combined view
    const channelNavLinks = document.querySelectorAll('.channel-nav a[href^="#"]');
    channelNavLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Copy permalink functionality
    const timestamps = document.querySelectorAll('.timestamp');
    timestamps.forEach(timestamp => {
        timestamp.addEventListener('click', function() {
            const messageElement = this.closest('.message');
            const ts = messageElement.getAttribute('data-ts');
            
            if (ts) {
                const url = new URL(window.location);
                url.hash = `message-${ts}`;
                
                navigator.clipboard.writeText(url.toString()).then(() => {
                    // Show temporary feedback
                    const originalText = this.textContent;
                    this.textContent = 'Link copied!';
                    this.style.color = '#36c5f0';
                    
                    setTimeout(() => {
                        this.textContent = originalText;
                        this.style.color = '';
                    }, 1500);
                }).catch(() => {
                    // Fallback for browsers that don't support clipboard API
                    console.log('Permalink:', url.toString());
                });
            }
        });
        
        // Add click cursor
        timestamp.style.cursor = 'pointer';
        timestamp.title = 'Click to copy permalink';
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + F to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            const searchInput = messageSearch || channelSearch;
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // Escape to clear search
        if (e.key === 'Escape') {
            const searchInput = messageSearch || channelSearch;
            if (searchInput && searchInput === document.activeElement) {
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input'));
                searchInput.blur();
            }
        }
    });

    // Auto-expand threads with search results
    if (messageSearch) {
        messageSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            if (searchTerm.length > 2) {
                const threadReplies = document.querySelectorAll('.thread-replies');
                threadReplies.forEach(thread => {
                    const threadText = thread.textContent.toLowerCase();
                    if (threadText.includes(searchTerm)) {
                        thread.style.display = 'block';
                    }
                });
            }
        });
    }

    // Highlight search terms in results
    function highlightSearchTerms(searchTerm) {
        if (searchTerm.length < 2) return;
        
        const messages = document.querySelectorAll('.message:not(.hidden)');
        messages.forEach(message => {
            const textElements = message.querySelectorAll('.message-text, .user-name');
            textElements.forEach(element => {
                const text = element.textContent;
                const regex = new RegExp(`(${searchTerm})`, 'gi');
                const highlightedText = text.replace(regex, '<mark>$1</mark>');
                
                if (highlightedText !== text) {
                    element.innerHTML = highlightedText;
                }
            });
        });
    }

    // Add search result counter
    function updateSearchCounter() {
        const searchInput = messageSearch || channelSearch;
        if (!searchInput) return;
        
        let counter = document.getElementById('search-counter');
        if (!counter) {
            counter = document.createElement('div');
            counter.id = 'search-counter';
            counter.style.cssText = `
                position: absolute;
                top: 50%;
                right: 10px;
                transform: translateY(-50%);
                font-size: 0.8rem;
                color: #666;
                pointer-events: none;
            `;
            
            const searchContainer = searchInput.parentElement;
            searchContainer.style.position = 'relative';
            searchContainer.appendChild(counter);
        }
        
        const visibleItems = messageSearch ? 
            document.querySelectorAll('.message:not(.hidden)').length :
            document.querySelectorAll('.channel-card:not(.hidden)').length;
        
        const totalItems = messageSearch ?
            document.querySelectorAll('.message').length :
            document.querySelectorAll('.channel-card').length;
        
        counter.textContent = `${visibleItems}/${totalItems}`;
        counter.style.display = searchInput.value ? 'block' : 'none';
    }

    // Add counter updates to existing search handlers
    if (channelSearch) {
        channelSearch.addEventListener('input', updateSearchCounter);
    }
    
    if (messageSearch) {
        messageSearch.addEventListener('input', updateSearchCounter);
    }
    
    // Initialize counter
    updateSearchCounter();
});