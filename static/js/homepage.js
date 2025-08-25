// Homepage animations and interactions
document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS animations
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            once: true,
            offset: 100
        });
    }

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Navbar scroll effect
    let lastScrollTop = 0;
    const navbar = document.querySelector('.futuristic-nav');
    
    window.addEventListener('scroll', function() {
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > 100) {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
            navbar.querySelectorAll('.nav-link').forEach(link => {
                link.style.color = '#2d3748';
            });
            navbar.querySelector('.brand-text').style.background = 'linear-gradient(135deg, #667eea, #764ba2)';
            navbar.querySelector('.brand-text').style.webkitBackgroundClip = 'text';
            navbar.querySelector('.brand-text').style.webkitTextFillColor = 'transparent';
        } else {
            navbar.style.background = 'rgba(255, 255, 255, 0.1)';
            navbar.style.boxShadow = 'none';
            navbar.querySelectorAll('.nav-link').forEach(link => {
                link.style.color = 'rgba(255, 255, 255, 0.9)';
            });
            navbar.querySelector('.brand-text').style.background = 'linear-gradient(135deg, white, rgba(255,255,255,0.8))';
            navbar.querySelector('.brand-text').style.webkitBackgroundClip = 'text';
            navbar.querySelector('.brand-text').style.webkitTextFillColor = 'transparent';
        }
        
        lastScrollTop = scrollTop;
    });

    // Parallax effect for hero section
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const heroSection = document.querySelector('.hero-section');
        if (heroSection) {
            const parallax = scrolled * 0.5;
            heroSection.style.transform = `translateY(${parallax}px)`;
        }
    });

    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.feature-card, .feature-pill, .timeline-item').forEach(el => {
        observer.observe(el);
    });

    // Add hover effects to floating cards
    document.querySelectorAll('.floating-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1) rotate(5deg)';
            this.style.zIndex = '10';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) rotate(0deg)';
            this.style.zIndex = '1';
        });
    });

    // Stats counter animation
    function animateCounter(element, target, duration = 2000) {
        let start = 0;
        const increment = target / (duration / 16);
        
        function updateCounter() {
            start += increment;
            if (start < target) {
                element.textContent = Math.ceil(start);
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = target;
            }
        }
        updateCounter();
    }

    // Trigger counter animation when stats come into view
    const statsObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const statNumbers = entry.target.querySelectorAll('.stat-number');
                statNumbers.forEach(stat => {
                    const text = stat.textContent;
                    if (text.includes('K')) {
                        const num = parseInt(text.replace('K+', ''));
                        animateCounter(stat, num);
                        setTimeout(() => {
                            stat.textContent = num + 'K+';
                        }, 2000);
                    } else if (text.includes('%')) {
                        const num = parseInt(text.replace('%', ''));
                        animateCounter(stat, num);
                        setTimeout(() => {
                            stat.textContent = num + '%';
                        }, 2000);
                    }
                });
                statsObserver.unobserve(entry.target);
            }
        });
    });

    const heroStats = document.querySelector('.hero-stats');
    if (heroStats) {
        statsObserver.observe(heroStats);
    }

    // Dynamic particle generation
    function createParticle() {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDuration = (Math.random() * 10 + 15) + 's';
        particle.style.animationDelay = Math.random() * 5 + 's';
        
        const size = Math.random() * 40 + 40;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        
        document.querySelector('.particles-container').appendChild(particle);
        
        // Remove particle after animation
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        }, 25000);
    }

    // Create new particles periodically
    setInterval(createParticle, 3000);

    // Mouse move effect for cards
    document.addEventListener('mousemove', function(e) {
        const cards = document.querySelectorAll('.feature-card, .floating-card');
        const mouseX = e.clientX;
        const mouseY = e.clientY;
        
        cards.forEach(card => {
            const rect = card.getBoundingClientRect();
            const cardX = rect.left + rect.width / 2;
            const cardY = rect.top + rect.height / 2;
            
            const deltaX = (mouseX - cardX) / rect.width;
            const deltaY = (mouseY - cardY) / rect.height;
            
            if (Math.abs(deltaX) < 1 && Math.abs(deltaY) < 1) {
                card.style.transform = `perspective(1000px) rotateX(${deltaY * 10}deg) rotateY(${deltaX * 10}deg) translateZ(20px)`;
            } else {
                card.style.transform = '';
            }
        });
    });

    // Define updateMoodTheme function first
    function updateMoodTheme(mood) {
        const root = document.documentElement;
        const themes = {
            happy: {
                primary: '#fbbf24',
                secondary: '#f59e0b',
                accent: '#fcd34d'
            },
            sad: {
                primary: '#3b82f6',
                secondary: '#1d4ed8',
                accent: '#60a5fa'
            },
            anxious: {
                primary: '#10b981',
                secondary: '#059669',
                accent: '#34d399'
            },
            energized: {
                primary: '#ef4444',
                secondary: '#dc2626',
                accent: '#f87171'
            },
            neutral: {
                primary: '#667eea',
                secondary: '#764ba2',
                accent: '#4facfe'
            }
        };
        
        const theme = themes[mood];
        if (theme) {
            root.style.setProperty('--primary-gradient', `linear-gradient(135deg, ${theme.primary} 0%, ${theme.secondary} 100%)`);
            root.style.setProperty('--secondary-gradient', `linear-gradient(135deg, ${theme.accent} 0%, ${theme.primary} 100%)`);
        }
    }

    // Mood simulation for demo (cycles through moods)
    let currentMoodIndex = 0;
    const moods = ['neutral', 'happy', 'sad', 'anxious', 'energized'];
    
    function simulateMoodChange() {
        if (!document.body.dataset.userLoggedIn) {
            currentMoodIndex = (currentMoodIndex + 1) % moods.length;
            const newMood = moods[currentMoodIndex];
            
            document.documentElement.setAttribute('data-mood', newMood);
            document.body.className = document.body.className.replace(/mood-\w+/, `mood-${newMood}`);
            
            // Update CSS custom properties
            updateMoodTheme(newMood);
        }
    }
    
    // Change mood every 10 seconds for demo
    setInterval(simulateMoodChange, 10000);

    // Form validation and enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea');
        
        inputs.forEach(input => {
            // Add focus and blur effects
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                if (!this.value) {
                    this.parentElement.classList.remove('focused');
                }
            });
            
            // Add input validation
            input.addEventListener('input', function() {
                if (this.type === 'email') {
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (emailRegex.test(this.value)) {
                        this.style.borderColor = '#10b981';
                    } else {
                        this.style.borderColor = '#ef4444';
                    }
                }
            });
        });
    });

    // Add loading states to buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.href && this.href.includes('#')) return; // Skip anchor links
            
            this.style.pointerEvents = 'none';
            this.style.opacity = '0.8';
            
            setTimeout(() => {
                this.style.pointerEvents = '';
                this.style.opacity = '';
            }, 2000);
        });
    });

    console.log('🌈 MindWell homepage loaded with animations!');
});

// Utility functions
function showMessage(text, type = 'info') {
    const message = document.createElement('div');
    message.className = `alert alert-${type} position-fixed`;
    message.style.top = '20px';
    message.style.right = '20px';
    message.style.zIndex = '9999';
    message.textContent = text;
    
    document.body.appendChild(message);
    
    setTimeout(() => {
        message.remove();
    }, 3000);
}

// Export for use in other scripts
window.MindWellHomepage = {
    showMessage
};