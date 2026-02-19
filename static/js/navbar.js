document.querySelector('.hamburger').addEventListener('click', function() {
    this.classList.toggle('active');
    document.querySelector('.nav-menu-mobile').classList.toggle('active');
});

document.querySelectorAll('.nav-menu-mobile a').forEach(link => {
    link.addEventListener('click', function() {
        document.querySelector('.hamburger').classList.remove('active');
        document.querySelector('.nav-menu-mobile').classList.remove('active');
    });
});
