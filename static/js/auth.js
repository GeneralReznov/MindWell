// MindWell Authentication functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔐 MindWell authentication loading...');
    
    // DOM elements
    const loginToggle = document.getElementById('loginToggle');
    const signupToggle = document.getElementById('signupToggle');
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const authAlert = document.getElementById('authAlert');
    const googleSignInBtn = document.getElementById('googleSignInBtn');
    const forgotPasswordLink = document.getElementById('forgotPasswordLink');

    // Form toggle functionality
    function switchToLogin() {
        loginToggle.classList.add('active');
        signupToggle.classList.remove('active');
        loginForm.classList.add('active');
        signupForm.classList.remove('active');
    }

    function switchToSignup() {
        signupToggle.classList.add('active');
        loginToggle.classList.remove('active');
        signupForm.classList.add('active');
        loginForm.classList.remove('active');
    }

    // Event listeners for toggle buttons
    loginToggle.addEventListener('click', switchToLogin);
    signupToggle.addEventListener('click', switchToSignup);

    // Alert functions
    function showAlert(message, type = 'error') {
        authAlert.textContent = message;
        authAlert.className = `alert ${type} show`;
        setTimeout(() => {
            authAlert.classList.remove('show');
        }, 5000);
    }

    function hideAlert() {
        authAlert.classList.remove('show');
    }

    // Loading state functions
    function setButtonLoading(button, loading = true) {
        const btnText = button.querySelector('.btn-text');
        const btnLoader = button.querySelector('.btn-loader');
        
        if (loading) {
            button.disabled = true;
            btnText.style.opacity = '0';
            btnLoader.classList.remove('hidden');
        } else {
            button.disabled = false;
            btnText.style.opacity = '1';
            btnLoader.classList.add('hidden');
        }
    }

    // Validation functions
    function validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function validatePassword(password) {
        return password.length >= 6;
    }

    // Success redirect with animation
    function showSuccessAndRedirect(message = 'Welcome to MindWell!', userName = '') {
        showAlert(message, 'success');
        
        // Create full-screen welcome overlay
        const overlay = document.createElement('div');
        overlay.className = 'welcome-overlay';
        overlay.innerHTML = `
            <div class="welcome-content">
                <div class="welcome-icon">🧠</div>
                <h2>Welcome to MindWell${userName ? ', ' + userName : ''}!</h2>
                <p>Taking you to your wellness dashboard...</p>
                <div class="loading-spinner"></div>
            </div>
        `;
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .welcome-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                opacity: 0;
                animation: fadeInOverlay 0.5s ease forwards;
            }
            .welcome-content {
                text-align: center;
                color: white;
                transform: translateY(20px);
                animation: slideUpContent 0.8s ease 0.3s forwards;
                opacity: 0;
            }
            .welcome-icon {
                font-size: 4rem;
                margin-bottom: 20px;
                animation: bounceIcon 1s ease 0.8s forwards;
            }
            .welcome-content h2 {
                font-size: 2rem;
                margin-bottom: 10px;
                font-weight: 700;
            }
            .welcome-content p {
                font-size: 1.1rem;
                margin-bottom: 30px;
                opacity: 0.9;
            }
            .loading-spinner {
                width: 40px;
                height: 40px;
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-top: 3px solid white;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes fadeInOverlay {
                to { opacity: 1; }
            }
            @keyframes slideUpContent {
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes bounceIcon {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-10px); }
                60% { transform: translateY(-5px); }
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(overlay);
        
        // Redirect after animation
        setTimeout(() => {
            window.location.href = '/';
        }, 2500);
    }

    // Check for Firebase configuration errors
    if (window.firebaseConfigError) {
        console.warn('⚠️ Firebase configuration error - using demo mode');
        showAlert('Demo Mode: Firebase authentication unavailable', 'warning');
        initializeDemoMode();
        return;
    }

    // Firebase authentication handlers
    if (typeof window.firebaseAuth !== 'undefined' && window.firebaseUtils) {
        console.log('🔥 Firebase initialized successfully');
        
        // Monitor auth state changes
        window.firebaseUtils.onAuthStateChanged(window.firebaseAuth, async (user) => {
            if (user) {
                console.log('User signed in:', user.email);
                
                // Send user data to backend to create/update user record
                try {
                    const idToken = await user.getIdToken();
                    const response = await fetch('/auth/firebase-login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            idToken: idToken,
                            email: user.email,
                            displayName: user.displayName,
                            photoURL: user.photoURL
                        })
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        showSuccessAndRedirect('Authentication successful!', user.displayName);
                    } else {
                        showAlert('Authentication failed. Please try again.');
                    }
                } catch (error) {
                    console.error('Error sending auth data to backend:', error);
                    showAlert('Authentication error. Please try again.');
                }
            }
        });

        // Email/password login
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            hideAlert();
            
            const email = document.getElementById('loginEmail').value.trim();
            const password = document.getElementById('loginPassword').value;
            const submitBtn = this.querySelector('.auth-btn.primary');
            
            // Validation
            if (!validateEmail(email)) {
                showAlert('Please enter a valid email address.');
                return;
            }
            
            if (!validatePassword(password)) {
                showAlert('Password must be at least 6 characters long.');
                return;
            }
            
            setButtonLoading(submitBtn, true);
            
            try {
                await window.firebaseUtils.signInWithEmailAndPassword(window.firebaseAuth, email, password);
            } catch (error) {
                console.error('Login error:', error);
                let errorMessage = 'Login failed. Please try again.';
                
                switch (error.code) {
                    case 'auth/user-not-found':
                        errorMessage = 'No account found with this email. Please sign up first.';
                        break;
                    case 'auth/wrong-password':
                        errorMessage = 'Incorrect password. Please try again.';
                        break;
                    case 'auth/invalid-email':
                        errorMessage = 'Please enter a valid email address.';
                        break;
                    case 'auth/too-many-requests':
                        errorMessage = 'Too many failed attempts. Please try again later.';
                        break;
                    case 'auth/user-disabled':
                        errorMessage = 'This account has been disabled.';
                        break;
                }
                
                showAlert(errorMessage);
            } finally {
                setButtonLoading(submitBtn, false);
            }
        });

        // Email/password signup
        signupForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            hideAlert();
            
            const name = document.getElementById('signupName').value.trim();
            const email = document.getElementById('signupEmail').value.trim();
            const password = document.getElementById('signupPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const submitBtn = this.querySelector('.auth-btn.primary');
            
            // Validation
            if (!name) {
                showAlert('Please enter your full name.');
                return;
            }
            
            if (!validateEmail(email)) {
                showAlert('Please enter a valid email address.');
                return;
            }
            
            if (!validatePassword(password)) {
                showAlert('Password must be at least 6 characters long.');
                return;
            }
            
            if (password !== confirmPassword) {
                showAlert('Passwords do not match.');
                return;
            }
            
            setButtonLoading(submitBtn, true);
            
            try {
                const userCredential = await window.firebaseUtils.createUserWithEmailAndPassword(window.firebaseAuth, email, password);
                
                // Update user profile with name
                await window.firebaseUtils.updateProfile(userCredential.user, {
                    displayName: name
                });
                
                showAlert('Account created successfully! Welcome to MindWell!', 'success');
            } catch (error) {
                console.error('Signup error:', error);
                let errorMessage = 'Account creation failed. Please try again.';
                
                switch (error.code) {
                    case 'auth/email-already-in-use':
                        errorMessage = 'An account with this email already exists. Please sign in instead.';
                        break;
                    case 'auth/invalid-email':
                        errorMessage = 'Please enter a valid email address.';
                        break;
                    case 'auth/weak-password':
                        errorMessage = 'Password is too weak. Please choose a stronger password.';
                        break;
                    case 'auth/operation-not-allowed':
                        errorMessage = 'Account creation is currently disabled.';
                        break;
                }
                
                showAlert(errorMessage);
            } finally {
                setButtonLoading(submitBtn, false);
            }
        });

        // Google Sign In
        googleSignInBtn.addEventListener('click', async function() {
            hideAlert();
            
            try {
                await window.firebaseUtils.signInWithPopup(window.firebaseAuth, window.googleProvider);
            } catch (error) {
                console.error('Google sign in error:', error);
                let errorMessage = 'Google sign in failed. Please try again.';
                
                switch (error.code) {
                    case 'auth/popup-closed-by-user':
                        return; // User closed popup, no error needed
                    case 'auth/popup-blocked':
                        errorMessage = 'Popup was blocked. Please allow popups and try again.';
                        break;
                    case 'auth/cancelled-popup-request':
                        return; // User cancelled, no error needed
                }
                
                showAlert(errorMessage);
            }
        });

        // Forgot password
        forgotPasswordLink.addEventListener('click', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('loginEmail').value.trim();
            
            if (!email) {
                showAlert('Please enter your email address first.');
                return;
            }
            
            if (!validateEmail(email)) {
                showAlert('Please enter a valid email address.');
                return;
            }
            
            try {
                await window.firebaseUtils.sendPasswordResetEmail(window.firebaseAuth, email);
                showAlert('Password reset email sent! Check your inbox.', 'success');
            } catch (error) {
                console.error('Password reset error:', error);
                let errorMessage = 'Failed to send reset email. Please try again.';
                
                switch (error.code) {
                    case 'auth/user-not-found':
                        errorMessage = 'No account found with this email address.';
                        break;
                    case 'auth/invalid-email':
                        errorMessage = 'Please enter a valid email address.';
                        break;
                }
                
                showAlert(errorMessage);
            }
        });

    } else {
        console.warn('⚠️ Firebase not available - using demo mode');
        initializeDemoMode();
    }

    function initializeDemoMode() {
        // Demo mode handlers
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('loginEmail').value;
            const submitBtn = this.querySelector('.auth-btn.primary');
            
            if (!email) {
                showAlert('Please enter an email address.');
                return;
            }
            
            setButtonLoading(submitBtn, true);
            setTimeout(() => {
                setButtonLoading(submitBtn, false);
                showSuccessAndRedirect('Demo login successful!', email.split('@')[0]);
            }, 1000);
        });
        
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const name = document.getElementById('signupName').value;
            const email = document.getElementById('signupEmail').value;
            const submitBtn = this.querySelector('.auth-btn.primary');
            
            if (!name || !email) {
                showAlert('Please fill in all required fields.');
                return;
            }
            
            setButtonLoading(submitBtn, true);
            setTimeout(() => {
                setButtonLoading(submitBtn, false);
                showSuccessAndRedirect('Demo account created!', name);
            }, 1000);
        });
        
        googleSignInBtn.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<div class="spinner" style="width:20px;height:20px;border:2px solid #f3f3f3;border-top:2px solid #667eea;border-radius:50%;animation:spin 1s linear infinite;margin:0 auto;"></div>';
            this.disabled = true;
            
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
                showSuccessAndRedirect('Demo Google sign in successful!', 'Demo User');
            }, 1500);
        });
    }

    // Initialize Particle.js
    function initializeParticles() {
        if (typeof particlesJS !== 'undefined') {
            particlesJS('particles-js', {
                particles: {
                    number: {
                        value: 120,
                        density: {
                            enable: true,
                            value_area: 800
                        }
                    },
                    color: {
                        value: "#ffffff"
                    },
                    shape: {
                        type: "circle",
                        stroke: {
                            width: 0,
                            color: "#000000"
                        }
                    },
                    opacity: {
                        value: 0.6,
                        random: true,
                        anim: {
                            enable: true,
                            speed: 1,
                            opacity_min: 0.1,
                            sync: false
                        }
                    },
                    size: {
                        value: 3,
                        random: true,
                        anim: {
                            enable: true,
                            speed: 2,
                            size_min: 0.1,
                            sync: false
                        }
                    },
                    line_linked: {
                        enable: true,
                        distance: 150,
                        color: "#ffffff",
                        opacity: 0.3,
                        width: 1
                    },
                    move: {
                        enable: true,
                        speed: 2,
                        direction: "none",
                        random: true,
                        straight: false,
                        out_mode: "out",
                        bounce: false,
                        attract: {
                            enable: true,
                            rotateX: 600,
                            rotateY: 1200
                        }
                    }
                },
                interactivity: {
                    detect_on: "canvas",
                    events: {
                        onhover: {
                            enable: true,
                            mode: "grab"
                        },
                        onclick: {
                            enable: true,
                            mode: "push"
                        },
                        resize: true
                    },
                    modes: {
                        grab: {
                            distance: 140,
                            line_linked: {
                                opacity: 0.8
                            }
                        },
                        push: {
                            particles_nb: 4
                        }
                    }
                },
                retina_detect: true
            });
            console.log('✨ Particle.js initialized successfully');
        } else {
            console.warn('⚠️ Particle.js not loaded, using fallback');
            createFallbackParticles();
        }
    }

    // Fallback particle system if Particle.js fails to load
    function createFallbackParticles() {
        const container = document.getElementById('particles-js') || document.createElement('div');
        container.id = 'particles-js';
        container.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        `;
        
        if (!document.getElementById('particles-js')) {
            document.querySelector('.auth-container').appendChild(container);
        }
        
        for (let i = 0; i < 30; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: absolute;
                width: ${Math.random() * 4 + 2}px;
                height: ${Math.random() * 4 + 2}px;
                background: rgba(255, 255, 255, ${Math.random() * 0.6 + 0.2});
                border-radius: 50%;
                pointer-events: none;
                animation: floatParticle ${Math.random() * 15 + 10}s linear infinite;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation-delay: ${Math.random() * 8}s;
            `;
            container.appendChild(particle);
        }
        
        // Add enhanced particle animation
        if (!document.getElementById('particleStyles')) {
            const style = document.createElement('style');
            style.id = 'particleStyles';
            style.textContent = `
                @keyframes floatParticle {
                    0% { 
                        opacity: 0; 
                        transform: translateY(100vh) translateX(0) rotate(0deg) scale(0.5); 
                    }
                    10% { 
                        opacity: 1; 
                        transform: translateY(90vh) translateX(10px) rotate(45deg) scale(1); 
                    }
                    50% { 
                        opacity: 0.8; 
                        transform: translateY(50vh) translateX(-20px) rotate(180deg) scale(1.2); 
                    }
                    90% { 
                        opacity: 0.6; 
                        transform: translateY(10vh) translateX(30px) rotate(315deg) scale(0.8); 
                    }
                    100% { 
                        opacity: 0; 
                        transform: translateY(-10vh) translateX(0) rotate(360deg) scale(0.3); 
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Initialize particles with retry mechanism
    setTimeout(() => {
        initializeParticles();
    }, 100);
    
    console.log('✅ MindWell authentication ready!');
});