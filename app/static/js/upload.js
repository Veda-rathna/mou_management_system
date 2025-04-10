/**
 * MOU Upload Form JavaScript
 */

import SignaturePad from "signature_pad"

document.addEventListener("DOMContentLoaded", () => {
  // Toggle between signature methods
  const signatureTypeInputs = document.querySelectorAll('input[name="signature_type"]')
  const signatureDrawContainer = document.getElementById("signatureDrawContainer")
  const signatureUploadContainer = document.getElementById("signatureUploadContainer")

  if (signatureTypeInputs.length) {
    signatureTypeInputs.forEach((input) => {
      input.addEventListener("change", function () {
        if (this.value === "draw") {
          signatureDrawContainer.style.display = "block"
          signatureUploadContainer.style.display = "none"
        } else {
          signatureDrawContainer.style.display = "none"
          signatureUploadContainer.style.display = "block"
        }
      })
    })
  }

  // Initialize signature pad if canvas exists
  const canvas = document.getElementById("signatureCanvas")
  if (canvas) {
    const signaturePad = new SignaturePad(canvas, {
      backgroundColor: "rgb(255, 255, 255)",
      penColor: "rgb(0, 0, 0)",
    })

    // Clear signature button
    const clearButton = document.getElementById("clearSignature")
    if (clearButton) {
      clearButton.addEventListener("click", () => {
        signaturePad.clear()
      })
    }

    // Resize canvas to fit container
    function resizeCanvas() {
      const ratio = Math.max(window.devicePixelRatio || 1, 1)
      canvas.width = canvas.offsetWidth * ratio
      canvas.height = canvas.offsetHeight * ratio
      canvas.getContext("2d").scale(ratio, ratio)
      signaturePad.clear() // Clear the canvas
    }

    window.addEventListener("resize", resizeCanvas)
    resizeCanvas()

    // Form submission - capture signature data
    const uploadForm = document.getElementById("uploadForm")
    const signatureDataInput = document.getElementById("signatureData")

    if (uploadForm && signatureDataInput) {
      uploadForm.addEventListener("submit", (e) => {
        // If drawing signature is selected
        if (document.getElementById("signatureDraw").checked) {
          if (signaturePad.isEmpty()) {
            e.preventDefault()
            alert("Please provide a signature before submitting.")
            return false
          }

          // Save signature data to hidden input
          signatureDataInput.value = signaturePad.toDataURL()
        } else {
          // If uploading signature is selected
          const signatureFile = document.getElementById("signature_file")
          if (!signatureFile.files.length) {
            e.preventDefault()
            alert("Please upload a signature image before submitting.")
            return false
          }
        }
      })
    }
  }

  // File upload preview
  const mouFileInput = document.getElementById("mou_file")
  const filePreview = document.getElementById("filePreview")

  if (mouFileInput && filePreview) {
    mouFileInput.addEventListener("change", function () {
      if (this.files && this.files[0]) {
        const fileName = this.files[0].name
        filePreview.textContent = fileName

        // Show file size
        const fileSize = (this.files[0].size / 1024 / 1024).toFixed(2)
        const fileSizeElement = document.createElement("span")
        fileSizeElement.classList.add("text-muted", "ms-2")
        fileSizeElement.textContent = `(${fileSize} MB)`
        filePreview.appendChild(fileSizeElement)
      } else {
        filePreview.textContent = "No file selected"
      }
    })
  }
})
