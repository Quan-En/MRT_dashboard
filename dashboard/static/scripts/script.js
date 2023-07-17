window.addEventListener('DOMContentLoaded', function() {
    var tableContainer = document.querySelector('.table-container');
    var tableHeader = document.querySelector('.sticky-header');

    tableContainer.addEventListener('scroll', function() {
        tableHeader.style.transform = 'translateY(' + this.scrollTop + 'px)';
    });
});


