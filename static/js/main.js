/**
 * SmileCraft Dental Clinic - Ultra-Premium Client-Side Engine
 * Handles interactive animations, cinematic scroll reveals, central testimonials, and AJAX booking.
 */

document.addEventListener('DOMContentLoaded', () => {

    // 1. Page Loader Fade Out
    const loader = document.getElementById('loader');
    if (loader) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                loader.classList.add('fade-out');
            }, 600); // Cinematic smooth fade out
        });
        
        if (document.readyState === 'complete') {
            setTimeout(() => {
                loader.classList.add('fade-out');
            }, 600);
        }
    }

    // 2. Intersection Observer for Cinematic Scroll Reveals
    const revealElements = document.querySelectorAll('.reveal');
    
    if (revealElements.length > 0) {
        const revealObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                    // Optional: Unobserve after revealing to only play animation once
                    // observer.unobserve(entry.target); 
                }
            });
        }, {
            root: null,
            threshold: 0.15, // Trigger when 15% of the element is visible
            rootMargin: "0px 0px -50px 0px" // Trigger slightly before it hits the viewport bottom
        });

        revealElements.forEach(el => revealObserver.observe(el));
    }

    // 3. Sticky Header Handler
    const header = document.getElementById('mainHeader');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // 4. Mobile Hamburger Menu Toggle
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const navMenu = document.getElementById('navMenu');
    
    if (hamburgerBtn && navMenu) {
        hamburgerBtn.addEventListener('click', () => {
            hamburgerBtn.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                hamburgerBtn.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });
    }

    // 5. Back to Top Button
    const backToTopBtn = document.getElementById('backToTopBtn');
    if (backToTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 500) {
                backToTopBtn.classList.add('active');
            } else {
                backToTopBtn.classList.remove('active');
            }
        });

        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // 6. Elegant Crossfade Testimonials Engine
    const testimonialItems = document.querySelectorAll('.testimonial-item');
    const prevTBtn = document.getElementById('prevTBtn');
    const nextTBtn = document.getElementById('nextTBtn');
    
    if (testimonialItems.length > 0 && prevTBtn && nextTBtn) {
        let currentIndex = 0;
        
        function showTestimonial(index) {
            // Remove active class from all
            testimonialItems.forEach(item => {
                item.classList.remove('active');
            });
            
            // Add active class to current
            testimonialItems[index].classList.add('active');
        }
        
        nextTBtn.addEventListener('click', () => {
            currentIndex = (currentIndex + 1) % testimonialItems.length;
            showTestimonial(currentIndex);
        });
        
        prevTBtn.addEventListener('click', () => {
            currentIndex = (currentIndex - 1 + testimonialItems.length) % testimonialItems.length;
            showTestimonial(currentIndex);
        });
        
        // Auto-play the testimonials every 8 seconds for dynamic feel
        setInterval(() => {
            currentIndex = (currentIndex + 1) % testimonialItems.length;
            showTestimonial(currentIndex);
        }, 8000);
    }

    // 7. AJAX Appointment Booking Form Submission
    const bookingForm = document.getElementById('bookingForm');
    const modalOverlay = document.getElementById('modalOverlay');
    const modalMessage = document.getElementById('modalMessage');
    const closeModalBtn = document.getElementById('closeModalBtn');
    
    if (bookingForm && modalOverlay && modalMessage && closeModalBtn) {
        
        bookingForm.addEventListener('submit', async (e) => {
            e.preventDefault(); 
            
            const submitBtn = bookingForm.querySelector('.btn-submit');
            const originalBtnText = submitBtn.innerHTML;
            
            const name = document.getElementById('name').value.trim();
            const phone = document.getElementById('phone').value.trim();
            const email = document.getElementById('email').value.trim();
            const date = document.getElementById('date').value;
            const time = document.getElementById('time').value;
            
            if (!name || !phone || !email || !date || !time) {
                alert('Please fill out all mandatory booking inputs.');
                return;
            }
            
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                alert('Please supply a valid email address.');
                return;
            }

            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="loader-spinner" style="width: 20px; height: 20px; border-width: 2px; border-top-color: white; display: inline-block; vertical-align: middle; margin-right: 8px;"></span> Processing...';
            
            try {
                const formData = new FormData(bookingForm);
                const response = await fetch('https://formspree.io/f/xzdqjzdp', {
                    method: 'POST',
                    headers: {
                        'Accept': 'application/json'
                    },
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    modalMessage.innerHTML = 'Your consultation request has been securely submitted. Our concierge team will reach out shortly.';
                    modalOverlay.classList.add('active');
                    bookingForm.reset();
                } else {
                    alert('An error occurred during booking. Please try again.');
                }
                
            } catch (error) {
                console.error('Error submitting appointment request:', error);
                alert('Unable to process booking at this time. Please check your network connection.');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        });
        
        closeModalBtn.addEventListener('click', () => {
            modalOverlay.classList.remove('active');
        });
        
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                modalOverlay.classList.remove('active');
            }
        });
    }
});
