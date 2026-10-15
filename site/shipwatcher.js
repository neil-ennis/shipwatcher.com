document.querySelectorAll('img[id^="webca"]').forEach((image) => {
  const fallback = document.createElement("div");
  fallback.className = "ship-webcam-fallback";
  fallback.setAttribute("role", "status");
  fallback.hidden = true;
  fallback.textContent =
    "This webcam is currently unavailable. This page remains in the ShipWatcher archive.";
  image.insertAdjacentElement("afterend", fallback);

  function showFallback() {
    image.hidden = true;
    fallback.hidden = false;
  }

  image.addEventListener("error", showFallback);
  if (image.complete && image.naturalWidth === 0) showFallback();
});
