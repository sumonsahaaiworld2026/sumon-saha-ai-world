const resultImage =
  document.getElementById("resultImage");

const downloadBtn =
  document.getElementById("downloadBtn");

const image =
  localStorage.getItem("resultImage");

if (image) {

  resultImage.src = image;

  downloadBtn.href = image;

} else {

  alert("No image found");

  window.location.href =
    "index.html";
}