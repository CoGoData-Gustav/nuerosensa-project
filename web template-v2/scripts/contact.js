// Form validation
document.getElementById('contactForm').addEventListener('submit', function(event) {
    var name = document.getElementById('name').value;
    var email = document.getElementById('email').value;
    var message = document.getElementById('message').value;

    if(name === '' || email === '' || message === '') {
        alert('Please fill out all fields.');
        event.preventDefault();  // Prevent form submission
    }
});

// Responsive menu toggle
document.getElementById('menuToggle').addEventListener('click', function() {
    var nav = document.getElementById('navbar').querySelector('ul');
    if(nav.style.display === 'flex' || nav.style.display === 'block') {
        nav.style.display = 'none';
    } else {
        nav.style.display = 'flex';
    }
});
