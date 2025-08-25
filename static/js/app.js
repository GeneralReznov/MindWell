// Mental Health Tracker - Client-side JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize mood-aware interactions
    initializeMoodFeatures();
    
    // Setup form enhancements
    setupFormEnhancements();
    
    // Setup smooth transitions
    setupSmoothTransitions();
    
    // Setup accessibility features
    setupAccessibility();
});

function initializeMoodFeatures() {
    const currentMood = document.documentElement.getAttribute('data-mood') || 'neutral';
    
    // Apply mood-specific animations
    applyMoodAnimations(currentMood);
    
    // Setup mood-responsive tooltips
    setupMoodTooltips(currentMood);
    
    // Initialize mood change listeners
    setupMoodChangeListeners();
}

function applyMoodAnimations(mood) {
    const cards = document.querySelectorAll('.mood-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 100}ms`;
        card.classList.add('animate-in');
    });
    
    // Mood-specific particle effects (subtle)
    if (mood === 'happy') {
        createHappyEffects();
    } else if (mood === 'energized') {
        createEnergyEffects();
    }
}

function createHappyEffects() {
    // Subtle golden sparkle effect
    const sparkles = document.createElement('div');
    sparkles.className = 'happy-sparkles';
    sparkles.innerHTML = '✨';
    sparkles.style.cssText = `
        position: fixed;
        top: 20%;
        right: 10%;
        font-size: 1.5rem;
        pointer-events: none;
        animation: sparkle 3s ease-in-out infinite;
        z-index: 1000;
    `;
    document.body.appendChild(sparkles);
    
    // Add sparkle animation
    if (!document.getElementById('sparkle-style')) {
        const style = document.createElement('style');
        style.id = 'sparkle-style';
        style.textContent = `
            @keyframes sparkle {
                0%, 100% { opacity: 0; transform: scale(0.5) rotate(0deg); }
                50% { opacity: 1; transform: scale(1) rotate(180deg); }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Remove after 10 seconds
    setTimeout(() => sparkles.remove(), 10000);
}

function createEnergyEffects() {
    // Subtle pulsing effect on buttons
    const buttons = document.querySelectorAll('.mood-btn');
    buttons.forEach(btn => {
        btn.style.animation = 'pulse 2s ease-in-out infinite';
    });
    
    if (!document.getElementById('energy-style')) {
        const style = document.createElement('style');
        style.id = 'energy-style';
        style.textContent = `
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.02); }
            }
        `;
        document.head.appendChild(style);
    }
}

// Add updateMoodTheme function
function updateMoodTheme(mood) {
    const root = document.documentElement;
    const body = document.body;
    
    // Remove existing mood classes
    body.classList.remove('mood-happy', 'mood-sad', 'mood-anxious', 'mood-energized', 'mood-neutral');
    
    // Add new mood class
    if (mood && mood !== 'neutral') {
        body.classList.add(`mood-${mood}`);
    }
    
    // Update CSS custom properties
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
    
    const theme = themes[mood] || themes.neutral;
    root.style.setProperty('--primary-gradient', `linear-gradient(135deg, ${theme.primary} 0%, ${theme.secondary} 100%)`);
    root.style.setProperty('--secondary-gradient', `linear-gradient(135deg, ${theme.accent} 0%, ${theme.primary} 100%)`);
    
    console.log(`🎨 Theme updated to: ${mood || 'neutral'}`);
}

function setupMoodTooltips(mood) {
    const moodMessages = {
        happy: {
            checkin: "Share your bright energy with us! ✨",
            journal: "Capture these beautiful thoughts 📝",
            habits: "Build on this positive momentum 🌱",
            history: "See how far you've come! 📈"
        },
        sad: {
            checkin: "We're here to listen with compassion 🤗",
            journal: "This is a safe space for your feelings 💙",
            habits: "Small, gentle steps forward 🌿",
            history: "Your journey shows strength 💪"
        },
        anxious: {
            checkin: "Take your time, there's no rush 🌿",
            journal: "Let your thoughts flow onto paper 🍃",
            habits: "Calming practices for peace ☮️",
            history: "Understanding patterns brings clarity 🧘"
        },
        energized: {
            checkin: "Channel this amazing energy! ⚡",
            journal: "Express your powerful thoughts 🚀",
            habits: "Transform energy into growth 💪",
            history: "Your progress is incredible! 🎯"
        }
    };
    
    const messages = moodMessages[mood] || {
        checkin: "Share how you're feeling today 💙",
        journal: "Express your thoughts freely 📝", 
        habits: "Small steps toward wellbeing 🌱",
        history: "Your journey of growth 📈"
    };
    
    // Add tooltips to navigation links
    document.querySelectorAll('.nav-link').forEach(link => {
        const href = link.getAttribute('href');
        let message = '';
        
        if (href.includes('mood_checkin')) message = messages.checkin;
        else if (href.includes('journal')) message = messages.journal;
        else if (href.includes('habits')) message = messages.habits;
        else if (href.includes('history')) message = messages.history;
        
        if (message) {
            link.setAttribute('title', message);
            link.setAttribute('data-bs-toggle', 'tooltip');
        }
    });
    
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function setupMoodChangeListeners() {
    // Listen for mood selection changes
    const moodInputs = document.querySelectorAll('input[name="mood_type"]');
    moodInputs.forEach(input => {
        input.addEventListener('change', function() {
            const selectedMood = this.value;
            previewMoodChange(selectedMood);
        });
    });
}

function previewMoodChange(newMood) {
    // Temporarily update the page theme for preview
    document.documentElement.setAttribute('data-mood', newMood);
    document.body.className = document.body.className.replace(/mood-\w+/, `mood-${newMood}`);
    
    // Add a subtle feedback effect
    const selectedOption = document.querySelector(`input[value="${newMood}"]`).nextElementSibling;
    selectedOption.style.transform = 'scale(1.05)';
    selectedOption.style.transition = 'transform 0.3s ease';
    
    setTimeout(() => {
        selectedOption.style.transform = '';
    }, 300);
}

function setupFormEnhancements() {
    // Enhanced textarea auto-resize
    const textareas = document.querySelectorAll('.mood-textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
        
        // Add helpful character counter for long entries
        if (textarea.name === 'content') {
            addCharacterCounter(textarea);
        }
    });
    
    // Enhanced range slider feedback
    const rangeInputs = document.querySelectorAll('.mood-range');
    rangeInputs.forEach(range => {
        range.addEventListener('input', function() {
            updateRangeVisual(this);
            provideMoodFeedback(this.value);
        });
    });
    
    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateMoodForm(this)) {
                e.preventDefault();
            } else {
                showSubmissionFeedback();
            }
        });
    });
}

function addCharacterCounter(textarea) {
    const counter = document.createElement('small');
    counter.className = 'text-muted character-counter';
    counter.style.cssText = 'display: block; text-align: right; margin-top: 0.5rem;';
    textarea.parentNode.appendChild(counter);
    
    const updateCounter = () => {
        const length = textarea.value.length;
        counter.textContent = `${length} characters`;
        
        if (length > 500) {
            counter.classList.add('text-success');
            counter.textContent += ' - Great detail! ✨';
        } else if (length > 100) {
            counter.classList.add('text-info');
            counter.textContent += ' - Keep going! 💭';
        }
    };
    
    textarea.addEventListener('input', updateCounter);
    updateCounter();
}

function updateRangeVisual(range) {
    const value = range.value;
    const max = range.max;
    const percentage = (value / max) * 100;
    
    // Update the visual fill of the range slider
    range.style.background = `linear-gradient(to right, var(--mood-primary) ${percentage}%, var(--mood-light) ${percentage}%)`;
}

function provideMoodFeedback(intensity) {
    const feedbackElement = document.querySelector('.intensity-feedback');
    if (!feedbackElement) {
        const feedback = document.createElement('div');
        feedback.className = 'intensity-feedback mt-2 text-center';
        document.querySelector('.intensity-slider').appendChild(feedback);
    }
    
    const feedback = document.querySelector('.intensity-feedback');
    const messages = {
        1: "Very mild - barely noticeable",
        2: "Mild - subtle feeling",
        3: "Light - gentle presence", 
        4: "Moderate - clearly present",
        5: "Medium - noticeable impact",
        6: "Strong - significant feeling",
        7: "Very strong - hard to ignore",
        8: "Intense - overwhelming at times",
        9: "Very intense - deeply felt",
        10: "Extreme - all-consuming"
    };
    
    feedback.innerHTML = `<small class="text-muted">${messages[intensity] || ''}</small>`;
}

function validateMoodForm(form) {
    const moodType = form.querySelector('input[name="mood_type"]:checked');
    const content = form.querySelector('textarea[name="content"]');
    
    // Mood check-in validation
    if (form.classList.contains('mood-checkin-form') && !moodType) {
        showValidationMessage('Please select how you\'re feeling', 'warning');
        return false;
    }
    
    // Journal validation
    if (content && content.value.trim().length === 0) {
        showValidationMessage('Your thoughts matter - please share something, even if it\'s brief', 'info');
        content.focus();
        return false;
    }
    
    return true;
}

function showValidationMessage(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show mood-alert`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alert, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

function showSubmissionFeedback() {
    // Add loading state to submit button
    const submitBtn = document.querySelector('button[type="submit"]');
    if (submitBtn) {
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
        submitBtn.disabled = true;
        
        // Re-enable after form submission (handled by server redirect)
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 3000);
    }
}

function setupSmoothTransitions() {
    // Smooth page transitions
    const links = document.querySelectorAll('a[href^="/"], a[href^="./"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!e.ctrlKey && !e.metaKey) {
                document.body.style.opacity = '0.9';
                document.body.style.transition = 'opacity 0.2s ease';
            }
        });
    });
    
    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
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
}

function setupAccessibility() {
    // Enhanced keyboard navigation
    const interactiveElements = document.querySelectorAll('.mood-option, .habit-card, .action-card');
    interactiveElements.forEach(element => {
        if (!element.hasAttribute('tabindex')) {
            element.setAttribute('tabindex', '0');
        }
        
        element.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
    
    // Focus management for mood selection
    const moodInputs = document.querySelectorAll('input[name="mood_type"]');
    moodInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.outline = '3px solid var(--mood-accent)';
            this.parentElement.style.outlineOffset = '2px';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.outline = '';
            this.parentElement.style.outlineOffset = '';
        });
    });
    
    // Screen reader announcements for mood changes
    let announcer = document.getElementById('mood-announcer');
    if (!announcer) {
        announcer = document.createElement('div');
        announcer.id = 'mood-announcer';
        announcer.setAttribute('aria-live', 'polite');
        announcer.setAttribute('aria-atomic', 'true');
        announcer.style.cssText = 'position: absolute; left: -10000px; width: 1px; height: 1px; overflow: hidden;';
        document.body.appendChild(announcer);
    }
}

// Utility functions for mood-specific features
function announceMoodChange(mood) {
    const announcer = document.getElementById('mood-announcer');
    const messages = {
        happy: 'Happy mood selected. The interface is now warm and welcoming.',
        sad: 'Sad mood selected. The interface is now gentle and supportive.',
        anxious: 'Anxious mood selected. The interface is now calm and reassuring.',
        energized: 'Energized mood selected. The interface is now vibrant and motivating.'
    };
    
    if (announcer && messages[mood]) {
        announcer.textContent = messages[mood];
    }
}

// Habit completion celebration
function celebrateHabitCompletion(habitName) {
    const celebration = document.createElement('div');
    celebration.className = 'habit-celebration';
    celebration.innerHTML = '🎉';
    celebration.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 3rem;
        pointer-events: none;
        z-index: 1001;
        animation: celebrate 1s ease-out forwards;
    `;
    
    document.body.appendChild(celebration);
    
    // Add celebration animation
    if (!document.getElementById('celebration-style')) {
        const style = document.createElement('style');
        style.id = 'celebration-style';
        style.textContent = `
            @keyframes celebrate {
                0% { transform: translate(-50%, -50%) scale(0); opacity: 0; }
                50% { transform: translate(-50%, -50%) scale(1.2); opacity: 1; }
                100% { transform: translate(-50%, -50%) scale(1) translateY(-50px); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    setTimeout(() => celebration.remove(), 1000);
    
    // Show encouraging message
    showValidationMessage(`Great job completing "${habitName}"! You're building positive momentum. 🌟`, 'success');
}

// Initialize any page-specific features
function initializePageFeatures() {
    const path = window.location.pathname;
    
    if (path.includes('habits')) {
        initializeHabitsPage();
    } else if (path.includes('journal')) {
        initializeJournalPage();
    } else if (path.includes('history')) {
        initializeHistoryPage();
    }
}

function initializeHabitsPage() {
    // Add completion celebration to habit buttons
    const habitButtons = document.querySelectorAll('button[type="submit"]');
    habitButtons.forEach(button => {
        if (button.textContent.includes('Done')) {
            button.addEventListener('click', function() {
                const habitCard = this.closest('.habit-card');
                if (habitCard) {
                    const habitName = habitCard.querySelector('h6').textContent;
                    setTimeout(() => celebrateHabitCompletion(habitName), 500);
                }
            });
        }
    });
}

function initializeJournalPage() {
    // Add writing encouragement
    const textarea = document.querySelector('textarea[name="content"]');
    if (textarea) {
        let encouragementTimer;
        
        textarea.addEventListener('input', function() {
            clearTimeout(encouragementTimer);
            
            if (this.value.length > 50) {
                encouragementTimer = setTimeout(() => {
                    if (this.value.length > 100) {
                        showEncouragement('Your thoughts are flowing beautifully. Keep going! 💭');
                    }
                }, 3000);
            }
        });
    }
}

function initializeHistoryPage() {
    // Add insights based on mood data
    const charts = document.querySelectorAll('canvas');
    charts.forEach(chart => {
        chart.addEventListener('click', function() {
            showValidationMessage('Your emotional journey shows incredible self-awareness. Every entry is growth! 📈', 'info');
        });
    });
}

function showEncouragement(message) {
    const encouragement = document.createElement('div');
    encouragement.className = 'encouragement-toast';
    encouragement.innerHTML = `
        <div class="toast show" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 1050;">
            <div class="toast-body bg-success text-white rounded">
                ${message}
            </div>
        </div>
    `;
    
    document.body.appendChild(encouragement);
    
    setTimeout(() => encouragement.remove(), 3000);
}

// Initialize page-specific features when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initializePageFeatures, 100);
});

// Service worker registration for offline capabilities (basic)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Note: Service worker file would need to be created separately
        // navigator.serviceWorker.register('/sw.js');
    });
}
