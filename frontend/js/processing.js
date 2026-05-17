const progressFill =
  document.getElementById("progressFill");

const progressText =
  document.getElementById("progressText");

let progress = 0;

async function processImage() {

  const uploadedImage =
    localStorage.getItem("uploadedImage");

  const response =
    await fetch(uploadedImage);

  const blob =
    await response.blob();

  const formData = new FormData();

  formData.append(
    "file",
    blob,
    "image.png"
  );

  const interval = setInterval(() => {

    progress += Math.floor(
      Math.random() * 10
    );

    if (progress > 90) {
      progress = 90;
    }

    progressFill.style.width =
      progress + "%";

    progressText.innerText =
      progress + "%";

  }, 300);

  try {

    const apiResponse =
      await fetch(
        "http://127.0.0.1:8000/remove-bg",
        {
          method: "POST",
          body: formData
        }
      );

    const resultBlob =
      await apiResponse.blob();

    // Convert blob to base64
    const reader = new FileReader();

    reader.onloadend = function () {

      localStorage.setItem(
        "resultImage",
        reader.result
      );

      clearInterval(interval);

      progress = 100;

      progressFill.style.width = "100%";

      progressText.innerText = "100%";

      setTimeout(() => {

        window.location.href =
          "result.html";

      }, 1000);
    };

    reader.readAsDataURL(resultBlob);

  } catch (error) {

    console.error(error);

    alert("Processing failed");
  }
}

processImage();