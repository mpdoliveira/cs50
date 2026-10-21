function highlightActiveNav() {
    const current = window.location.pathname.split('/').pop() || 'index.html';
    const page_links = document.querySelectorAll('.nav-link');

    page_links.forEach(link => {
        const href = link.getAttribute('href');
        if (href === current) {
            link.classList.add('active');
            link.textContent = '• ' + link.textContent + ' •';
            link.setAttribute('aria-current', 'page');
        }
        else {
            link.classList.remove('active');
        }
    });
}

function galeria() {
    const container = document.querySelector('#image-container');

    if (!container) {
        return;
    }

    const imageList = window.GLOBAL_IMAGE_FILENAMES;
    const imageHTML = imageList.map((filename, i) => {
        const imagePath = `images/${filename}`;
        const activeClass = i === 0? 'active' : '';

        return `
            <div class="carousel-item ${activeClass}">
                <img src="${imagePath}" class="d-block w-100" alt="${filename}">
            </div>
        `;
    }).join('');

    const buttonsHTML = `
        <button class="carousel-control-prev" type="button" data-bs-target="#image-container" data-bs-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Previous</span>
        </button>
        <button class="carousel-control-next" type="button" data-bs-target="#image-container" data-bs-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Previous</span>
        </button>
    `
    container.innerHTML = `<div class="carousel-inner">${imageHTML}</div>${buttonsHTML}`;
}

document.addEventListener('DOMContentLoaded', function() {
    highlightActiveNav();
});
