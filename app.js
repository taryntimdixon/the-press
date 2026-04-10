document.addEventListener("DOMContentLoaded", () => {

  // 🔥 Replace any author text anywhere on page
  document.body.innerHTML = document.body.innerHTML.replace(
    /By\s+[A-Z][a-z]+\s+[A-Z][a-z]+/g,
    "Written and investigated by AI"
  );

  // 🔥 Fix missing images
  document.querySelectorAll("img").forEach(img => {
    img.onerror = function () {
      this.src = "https://via.placeholder.com/800x500?text=The+Press";
    };
  });

});
