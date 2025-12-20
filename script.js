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