// 🔥 Replace this with your Render backend URL
const API_URL = "https://your-render-app.onrender.com";

const progressFill = document.getElementById("progressFill");
const progressText = document.getElementById("progressText");

let progress = 0;

function resetProgress() {
  progress = 0;
  progressFill.style.width = "0%";
  progressText.innerText = "0%";
}

async function processImage() {

  const uploadedImage = localStorage.getItem("uploadedImage");

  if (!uploadedImage) {
    alert("No image found. Please upload again.");
    return;
  }

  const response = await fetch(uploadedImage);
  const blob = await response.blob();

  const formData = new FormData();
  formData.append("file", blob, "image.png");

  resetProgress();

  // =========================
  // FAKE PROGRESS ANIMATION
  // =========================
  const interval = setInterval(() => {
    progress += Math.floor(Math.random() * 8);

    if (progress > 90) progress = 90;

    progressFill.style.width = progress + "%";
    progressText.innerText = progress + "%";
  }, 300);

  try {

    const apiResponse = await fetch(`${API_URL}/remove-bg`, {
      method: "POST",
      body: formData
    });

    if (!apiResponse.ok) {
      throw new Error("Server error: " + apiResponse.status);
    }

    const resultBlob = await apiResponse.blob();

    clearInterval(interval);

    // complete progress
    progress = 100;
    progressFill.style.width = "100%";
    progressText.innerText = "100%";

    const reader = new FileReader();

    reader.onloadend = function () {
      localStorage.setItem("resultImage", reader.result);

      setTimeout(() => {
        window.location.href = "result.html";
      }, 800);
    };

    reader.readAsDataURL(resultBlob);

  } catch (error) {

    console.error(error);

    clearInterval(interval);

    alert(
      "Processing failed. Please check if backend is deployed on Render and URL is correct."
    );

    resetProgress();
  }
}

processImage();
