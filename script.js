document.addEventListener('DOMContentLoaded', function() {

    // --- 1. FORM SUBMISSION LOGIC ---
    const quoteForm = document.getElementById('quoteForm');
    const formMessage = document.getElementById('formMessage');

    if (quoteForm) { // Only runs if the form is on the page
        quoteForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            formMessage.style.display = 'none';
            const formData = new FormData(quoteForm);

            fetch(quoteForm.action, {
                method: quoteForm.method,
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    formMessage.textContent = 'Success! Your request has been sent.';
                    formMessage.style.color = '#00ff73';
                    quoteForm.reset();
                } else {
                    return response.text().then(text => { throw new Error(text || 'Submission failed.'); });
                }
            })
            .catch(error => {
                formMessage.textContent = 'Error: ' + error.message;
                formMessage.style.color = '#ff4d4d';
            })
            .finally(() => {
                formMessage.style.display = 'block';
            });
        });
    }

    // --- 2. SMOOTH SCROLLING ---
    document.querySelectorAll('nav a').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                const targetElement = document.querySelector(href);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 80, // Adjust for header height
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // --- 3. ANIMATION LOGIC (Intersection Observer) ---
    const observerOptions = { threshold: 0.1 };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    document.querySelectorAll('.fade-in-up').forEach((el) => {
        observer.observe(el);
    });

    // --- 4. BACK TO TOP BUTTON LOGIC ---
    const mybutton = document.getElementById("backToTopBtn");

    if (mybutton) {
        window.addEventListener('scroll', function() {
            if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
                mybutton.style.display = "block";
            } else {
                mybutton.style.display = "none";
            }
        });
    }
});

// This function needs to be global so the onclick="" in HTML can see it
function topFunction() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}
// Intersection Observer for Scroll Animations
const observerOptions = {
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.fade-in-up').forEach((el) => {
        observer.observe(el);
    });
});

// Simple Form Validation Feedback
const quoteForm = document.getElementById('quoteForm');
if(quoteForm) {
    quoteForm.addEventListener('submit', function(e) {
        // This is just a UI feedback example. 
        // Actual submission happens via the form 'action'
        document.getElementById('formMessage').style.display = 'block';
    });
}
// Hero Slider Functionality
let currentSlide = 0;
const slides = document.querySelectorAll(".slide");

function nextSlide() {
    // Remove active class from current slide
    slides[currentSlide].classList.remove("active");
    
    // Move to next slide, or back to 0 if at the end
    currentSlide = (currentSlide + 1) % slides.length;
    
    // Add active class to the new slide
    slides[currentSlide].classList.add("active");
}

// Change slide every 5000ms (5 seconds)
setInterval(nextSlide, 5000);
const menuToggle = document.getElementById('mobile-menu');
const navList = document.getElementById('nav-list');

menuToggle.addEventListener('click', () => {
    // Toggle the 'active' class on the nav
    navList.classList.toggle('active');
    
    // Change the icon from "bars" to an "X" when open
    const icon = menuToggle.querySelector('i');
    if (navList.classList.contains('active')) {
        icon.classList.remove('fa-bars');
        icon.classList.add('fa-times');
    } else {
        icon.classList.remove('fa-times');
        icon.classList.add('fa-bars');
    }
});

// Close menu when a link is clicked (useful for one-page scrolling)
document.querySelectorAll('nav ul li a').forEach(link => {
    link.addEventListener('click', () => {
        navList.classList.remove('active');
        menuToggle.querySelector('i').classList.replace('fa-times', 'fa-bars');
    });
});
document.getElementById('quoteForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent actual submission for now to validate

    const name = document.getElementById('name');
    const email = document.getElementById('email');
    const phone = document.getElementById('phone');
    const message = document.getElementById('message');
    const formMessage = document.getElementById('formMessage');

    let isValid = true;
    let errorMessage = "";

    // 1. Name Validation (at least 3 characters)
    if (name.value.trim().length < 3) {
        isValid = false;
        name.style.border = "2px solid #ff4444";
        errorMessage += "Please enter your full name.\n";
    } else {
        name.style.border = "none";
    }

    // 2. Email Validation (Regex pattern)
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email.value)) {
        isValid = false;
        email.style.border = "2px solid #ff4444";
        errorMessage += "Please enter a valid email address.\n";
    } else {
        email.style.border = "none";
    }

    // 3. Phone Validation (Simple check for numbers)
    if (phone.value.trim().length < 10) {
        isValid = false;
        phone.style.border = "2px solid #ff4444";
        errorMessage += "Please enter a valid phone number.\n";
    } else {
        phone.style.border = "none";
    }

    // Final Action
    if (isValid) {
        // Show success message
        formMessage.style.display = "block";
        formMessage.textContent = "Thank you! Sending your request...";
        formMessage.style.color = "#4CAF50"; // Green for success

        // In a real scenario, you would use fetch() here to send data to process_form.php
        // For now, we will simulate success
        setTimeout(() => {
            this.submit(); // Actually submit the form after a short delay
        }, 2000);
    } else {
        // Show error
        formMessage.style.display = "block";
        formMessage.textContent = "Please fix the red fields above.";
        formMessage.style.color = "#ff9800"; // Warning color
    }
});
var form = document.getElementById("pro-contact-form");
var statusMessage = document.getElementById("form-status");

async function handleSubmit(event) {
  event.preventDefault();
  var data = new FormData(event.target);
  
  // Change button text to show it's working
  var btn = document.getElementById("submit-btn");
  btn.innerHTML = "Sending... <i class='fas fa-spinner fa-spin'></i>";
  btn.style.opacity = "0.7";

  fetch(event.target.action, {
    method: form.method,
    body: data,
    headers: {
        'Accept': 'application/json'
    }
  }).then(response => {
    if (response.ok) {
      statusMessage.style.color = "#00796b"; // Your Teal color
      statusMessage.innerHTML = "Success! Our engineers will contact you shortly.";
      form.reset();
      btn.innerHTML = "Sent! <i class='fas fa-check'></i>";
    } else {
      response.json().then(data => {
        if (Object.hasOwn(data, 'errors')) {
          statusMessage.innerHTML = data["errors"].map(error => error["message"]).join(", ");
        } else {
          statusMessage.innerHTML = "Oops! There was a problem submitting your form.";
        }
      })
    }
  }).catch(error => {
    statusMessage.style.color = "red";
    statusMessage.innerHTML = "Oops! Network error. Please try again.";
  });
}

form.addEventListener("submit", handleSubmit);


