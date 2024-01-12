document.addEventListener("DOMContentLoaded", function() {
    var lazyImages = [].slice.call(document.querySelectorAll("img.lazy-load"));
  
    lazyImages.forEach(function(img) {
      img.src = img.dataset.src;
    });
  });
  