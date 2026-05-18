const fileInput =
  document.getElementById("fileInput");

const previewImage =
  document.getElementById("previewImage");

const uploadBtn =
  document.getElementById("uploadBtn");

const uploadContent =
  document.getElementById("uploadContent");

let selectedFile = null;

/* IMAGE SELECT */

fileInput.addEventListener("change", () => {

  const file = fileInput.files[0];

  if (!file) return;

  selectedFile = file;

  const reader = new FileReader();

  reader.onload = function (e) {

    previewImage.src = e.target.result;

    previewImage.style.display = "block";

    uploadContent.style.display = "none";

    uploadBtn.style.display = "block";

    // Store image safely
    localStorage.setItem(
      "uploadedImage",
      e.target.result
    );
  };

  reader.readAsDataURL(file);
});

/* PROCESS BUTTON */

uploadBtn.addEventListener("click", () => {

  if (!selectedFile) {
    alert("Please upload an image");
    return;
  }

  window.location.href =
    "/frontend/processing.html";
});
