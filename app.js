document.addEventListener("DOMContentLoaded", () => {

  // 🔥 FIX AUTHOR NAME EVERYWHERE
  document.querySelectorAll(".byline").forEach(el => {
    el.textContent = "Written and investigated by AI";
  });

  // 🔥 FIX MISSING IMAGES
  document.querySelectorAll("img").forEach(img => {
    img.onerror = function () {
      this.src = "https://via.placeholder.com/800x500?text=The+Press";
    };
  });

});
