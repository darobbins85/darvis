document.addEventListener('DOMContentLoaded', function() {
    const clickButton = document.getElementById('clickButton');
    let clickCount = 0;
    
    clickButton.addEventListener('click', function() {
        clickCount++;
        
        if (clickCount === 1) {
            this.textContent = 'Thanks for clicking!';
            this.style.backgroundColor = '#27ae60';
        } else if (clickCount === 2) {
            this.textContent = 'Click again!';
            this.style.backgroundColor = '#e74c3c';
        } else if (clickCount === 3) {
            this.textContent = 'One more time!';
            this.style.backgroundColor = '#f39c12';
        } else {
            this.textContent = 'Reset!';
            this.style.backgroundColor = '#9b59b6';
            setTimeout(() => {
                clickCount = 0;
                this.textContent = 'Click Me!';
                this.style.backgroundColor = '#3498db';
            }, 1000);
        }
    });
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add current year to footer
    const footer = document.querySelector('footer p');
    if (footer) {
        const currentYear = new Date().getFullYear();
        footer.textContent = `© ${currentYear} Simple Website`;
    }
});