/**
 * Admin Dashboard JavaScript
 */

import * as bootstrap from "bootstrap"

document.addEventListener("DOMContentLoaded", () => {
  // Initialize tooltips
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  var tooltipList = tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))

  // Initialize popovers
  var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
  var popoverList = popoverTriggerList.map((popoverTriggerEl) => new bootstrap.Popover(popoverTriggerEl))

  // Filter form submission
  const filterForm = document.querySelector('form[action*="dashboard"]')
  if (filterForm) {
    // Add event listeners for filter changes to auto-submit
    const filterSelects = filterForm.querySelectorAll("select")
    filterSelects.forEach((select) => {
      select.addEventListener("change", () => {
        filterForm.submit()
      })
    })
  }

  // MOU details page - copy link functionality
  const uploadLinkInput = document.getElementById("uploadLink")
  if (uploadLinkInput) {
    const copyButton = uploadLinkInput.nextElementSibling
    copyButton.addEventListener("click", () => {
      uploadLinkInput.select()
      document.execCommand("copy")

      // Show copied feedback
      const originalText = copyButton.textContent
      copyButton.textContent = "Copied!"
      setTimeout(() => {
        copyButton.textContent = originalText
      }, 2000)
    })
  }

  // Handle confirmation modals
  const confirmationModals = document.querySelectorAll(".confirmation-modal")
  confirmationModals.forEach((modal) => {
    const confirmButton = modal.querySelector(".btn-confirm")
    const form = modal.querySelector("form")

    if (confirmButton && form) {
      confirmButton.addEventListener("click", (e) => {
        e.preventDefault()
        form.submit()
      })
    }
  })
})
