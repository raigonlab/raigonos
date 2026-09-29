// Left / right arrow keys step through the Collection.
document.addEventListener('keydown', function (event) {
  var link;

  if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) {
    return;
  }

  if (event.key === 'ArrowLeft') {
    link = document.querySelector('.artwork-arrow-prev');
  } else if (event.key === 'ArrowRight') {
    link = document.querySelector('.artwork-arrow-next');
  }

  if (link) {
    window.location.href = link.href;
  }
});
