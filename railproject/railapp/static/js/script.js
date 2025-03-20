// Railway Management System JavaScript

document.addEventListener("DOMContentLoaded", () => {
  // Initialize tooltips
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  var tooltipList = tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))

  // Passenger form handling
  const addPassengerBtn = document.getElementById("add-passenger")
  if (addPassengerBtn) {
    addPassengerBtn.addEventListener("click", () => {
      const totalForms = document.querySelector("#id_passengers-TOTAL_FORMS")
      const formNum = Number.parseInt(totalForms.value)

      // Clone the first form
      const formTemplate = document.querySelector(".passenger-form:first-child").cloneNode(true)

      // Update form IDs and names
      const inputs = formTemplate.querySelectorAll("input, select")
      inputs.forEach((input) => {
        input.value = ""
        input.id = input.id.replace("-0-", `-${formNum}-`)
        input.name = input.name.replace("-0-", `-${formNum}-`)
      })

      // Update labels
      const labels = formTemplate.querySelectorAll("label")
      labels.forEach((label) => {
        label.setAttribute("for", label.getAttribute("for").replace("-0-", `-${formNum}-`))
      })

      // Add the new form
      document.querySelector("#passenger-forms").appendChild(formTemplate)

      // Update total forms
      totalForms.value = formNum + 1
    })
  }

  // PNR status form validation
  const pnrForm = document.getElementById("pnr-form")
  if (pnrForm) {
    pnrForm.addEventListener("submit", (e) => {
      const pnrInput = document.getElementById("pnr-input")
      if (!pnrInput.value.trim()) {
        e.preventDefault()
        alert("Please enter a PNR number")
      }
    })
  }

  // Train search form validation
  const searchForm = document.querySelector('form[action="/search/"]')
  if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
      const source = document.getElementById("id_source")
      const destination = document.getElementById("id_destination")

      if (source.value === destination.value && source.value !== "") {
        e.preventDefault()
        alert("Source and destination stations cannot be the same")
      }
    })
  }

  // Booking cancellation confirmation
  const cancelButtons = document.querySelectorAll(".cancel-booking-btn")
  cancelButtons.forEach((button) => {
    button.addEventListener("click", (e) => {
      if (!confirm("Are you sure you want to cancel this booking? This action cannot be undone.")) {
        e.preventDefault()
      }
    })
  })

  // Date validation for journey date
  const journeyDateInput = document.getElementById("id_journey_date")
  if (journeyDateInput) {
    journeyDateInput.addEventListener("change", function () {
      const selectedDate = new Date(this.value)
      const today = new Date()
      today.setHours(0, 0, 0, 0)

      if (selectedDate < today) {
        alert("Journey date cannot be in the past")
        this.value = ""
      }
    })
  }
})

