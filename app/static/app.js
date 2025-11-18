/**
 * Horoscope Generator Application
 * Alpine.js based single-page application for generating personalized horoscopes
 */

function horoscopeApp() {
  return {
    // Form data
    formData: {
      name: "",
      dob: "",
      code: "",
      horoscope_type: "HoroscopeBasic",
    },

    // UI State
    isLoading: false,
    showSuccess: false,
    showError: false,
    errorMessage: "",
    loadingProgress: 0,
    pdfBlob: null,

    // Validation errors
    errors: {
      name: "",
      dob: "",
      code: "",
    },

    // Notifications
    notifications: [],
    notificationIdCounter: 0,

    /**
     * Initialize the application
     */
    initApp() {
      console.log("ČísLenka app initialized");
      // Set default horoscope type to HoroscopeBasic
      this.formData.horoscope_type = "HoroscopeBasic";
    },

    /**
     * Validate the form data
     * @returns {boolean} True if form is valid
     */
    validateForm() {
      this.errors = {
        name: "",
        dob: "",
        code: "",
      };

      let isValid = true;

      // Validate name
      if (!this.formData.name.trim()) {
        this.errors.name = "Jméno je povinné.";
        isValid = false;
      } else if (this.formData.name.trim().length < 2) {
        this.errors.name = "Jméno musí mít alespoň 2 znaky.";
        isValid = false;
      } else if (this.formData.name.trim().length > 50) {
        this.errors.name = "Jméno je příliš dlouhé (max 50 znaků).";
        isValid = false;
      }

      // Validate date of birth (DD.MM.YYYY format)
      if (!this.formData.dob.trim()) {
        this.errors.dob = "Datum narození je povinné.";
        isValid = false;
      } else if (!this.isValidDateFormat(this.formData.dob)) {
        this.errors.dob = "Neplatný formát data. Použijte DD.MM.YYYY.";
        isValid = false;
      } else if (!this.isValidDate(this.formData.dob)) {
        this.errors.dob = "Zadejte platné datum narození.";
        isValid = false;
      }

      // Validate access code
      if (!this.formData.code.trim()) {
        this.errors.code = "Přístupový kód je povinný.";
        isValid = false;
      } else if (this.formData.code.trim().length < 3) {
        this.errors.code = "Přístupový kód je příliš krátký.";
        isValid = false;
      }

      return isValid;
    },

    /**
     * Validate date format (DD.MM.YYYY)
     * @param {string} dateStr - Date string to validate
     * @returns {boolean} True if format is valid
     */
    isValidDateFormat(dateStr) {
      const regex = /^(\d{2})\.(\d{2})\.(\d{4})$/;
      return regex.test(dateStr);
    },

    /**
     * Validate date is a real date
     * @param {string} dateStr - Date string in DD.MM.YYYY format
     * @returns {boolean} True if date is valid
     */
    isValidDate(dateStr) {
      const parts = dateStr.split(".");
      const day = parseInt(parts[0], 10);
      const month = parseInt(parts[1], 10);
      const year = parseInt(parts[2], 10);

      // Check if date is in the past
      const inputDate = new Date(year, month - 1, day);
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      if (inputDate >= today) {
        return false;
      }

      // Basic date validation
      const date = new Date(year, month - 1, day);
      return (
        date.getFullYear() === year &&
        date.getMonth() === month - 1 &&
        date.getDate() === day &&
        year > 1900 &&
        year < 2025
      );
    },

    /**
     * Simulate progress bar animation
     */
    startProgressAnimation() {
      this.loadingProgress = 0;
      const interval = setInterval(() => {
        if (this.loadingProgress < 90) {
          // Increment with decreasing speed
          const increment = Math.random() * (15 - this.loadingProgress / 10);
          this.loadingProgress =
            Math.round(Math.min(this.loadingProgress + increment, 90) * 10) /
            10;
        } else {
          clearInterval(interval);
        }
      }, 500);

      return interval;
    },

    /**
     * Submit the form and generate horoscope
     */
    async submitForm() {
      // Validate form
      if (!this.validateForm()) {
        console.log("Form validation failed");
        // Show warning notification for incomplete form
        let missingFields = [];
        if (!this.formData.name.trim()) missingFields.push("Jméno");
        if (!this.formData.dob.trim()) missingFields.push("Datum narození");
        if (!this.formData.code.trim()) missingFields.push("Přístupový kód");

        const fieldsList = missingFields.join(", ");
        this.showWarningNotification(
          `Prosím vyplňte povinná pole: ${fieldsList}`
        );
        return;
      }

      // Set loading state
      this.isLoading = true;
      this.showSuccess = false;
      this.showError = false;
      this.errorMessage = "";

      // Start progress animation
      const progressInterval = this.startProgressAnimation();

      try {
        // Prepare request data
        const payload = {
          name: this.formData.name.trim(),
          dob: this.formData.dob.trim(),
          code: this.formData.code.trim(),
          horoscope_type: this.formData.horoscope_type,
        };

        console.log("Sending request:", payload);

        // Send POST request
        const response = await fetch("/api/horoscope/horoscope-pdf", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        // Complete progress bar
        clearInterval(progressInterval);
        this.loadingProgress = 100;

        if (!response.ok) {
          // Handle error response
          let errorMsg = "Chyba při generování horoskopu.";

          try {
            const errorData = await response.json();
            if (errorData.detail) {
              errorMsg = this.formatErrorMessage(errorData.detail);
            }
          } catch {
            // If response is not JSON, use status text
            errorMsg = response.statusText || "Chyba při generování horoskopu.";
          }

          throw new Error(errorMsg);
        }

        // Get PDF blob
        this.pdfBlob = await response.blob();

        // Show success state
        this.isLoading = false;
        this.showSuccess = true;
        this.showSuccessNotification(
          "Vaš horoskop byl úspěšně vygenerován! 🎉"
        );

        console.log("Horoscope generated successfully");
      } catch (error) {
        console.error("Error:", error);

        clearInterval(progressInterval);
        this.isLoading = false;
        this.showError = true;
        this.errorMessage =
          error.message || "Došlo k neznámé chybě. Prosím zkuste znovu.";
        this.showErrorNotification(this.errorMessage);
      }
    },

    /**
     * Format error message for display
     * @param {string|array} detail - Error detail from API
     * @returns {string} Formatted error message
     */
    formatErrorMessage(detail) {
      if (Array.isArray(detail)) {
        // If it's a validation error array
        return detail
          .map((err) => {
            if (err.msg) return err.msg;
            return JSON.stringify(err);
          })
          .join(", ");
      }

      if (typeof detail === "string") {
        return detail;
      }

      return "Chyba při generování horoskopu.";
    },

    /**
     * Download the generated PDF
     */
    downloadPDF() {
      if (!this.pdfBlob) {
        console.error("No PDF blob available");
        return;
      }

      // Create download link
      const url = window.URL.createObjectURL(this.pdfBlob);
      const link = document.createElement("a");
      link.href = url;

      // Create filename with name and current date
      const date = new Date();
      const dateStr = date.toISOString().split("T")[0];
      const filename = `horoscope_${this.formData.name.trim()}_${dateStr}.pdf`;

      // Encode filename to UTF-8
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      console.log("PDF downloaded:", filename);
    },

    /**
     * Reset form and return to initial state
     */
    resetForm() {
      this.formData = {
        name: "",
        dob: "",
        code: "",
        horoscope_type: "HoroscopeBasic",
      };

      this.errors = {
        name: "",
        dob: "",
        code: "",
      };

      this.isLoading = false;
      this.showSuccess = false;
      this.showError = false;
      this.errorMessage = "";
      this.loadingProgress = 0;
      this.pdfBlob = null;

      console.log("Form reset");
    },

    /**
     * Show a notification
     * @param {string} message - Notification message
     * @param {string} type - Type of notification (success, error, warning, info)
     * @param {number} duration - Duration in milliseconds (default: 5000)
     */
    showNotification(message, type = "info", duration = 5000) {
      const id = this.notificationIdCounter++;
      const notification = {
        id,
        message,
        type,
        duration,
        visible: true,
      };

      this.notifications.push(notification);
      // Force Alpine.js to detect the change
      this.notifications = [...this.notifications];

      // Auto-remove notification after duration
      setTimeout(() => {
        this.removeNotification(id);
      }, duration);

      return id;
    },

    /**
     * Remove a notification by ID
     * @param {number} id - Notification ID
     */
    removeNotification(id) {
      const index = this.notifications.findIndex((n) => n.id === id);
      if (index !== -1) {
        this.notifications.splice(index, 1);
        // Force Alpine.js to detect the change
        this.notifications = [...this.notifications];
      }
    },

    /**
     * Show success notification
     * @param {string} message - Success message
     */
    showSuccessNotification(message) {
      this.showNotification(message, "success", 5000);
    },

    /**
     * Show error notification
     * @param {string} message - Error message
     */
    showErrorNotification(message) {
      this.showNotification(message, "error", 6000);
    },

    /**
     * Show warning notification
     * @param {string} message - Warning message
     */
    showWarningNotification(message) {
      this.showNotification(message, "warning", 5000);
    },

    /**
     * Show info notification
     * @param {string} message - Info message
     */
    showInfoNotification(message) {
      this.showNotification(message, "info", 4000);
    },

    /**
     * Validate name field on blur
     */
    validateNameField() {
      this.errors.name = "";
      const name = this.formData.name.trim();

      if (!name) {
        this.errors.name = "Jméno je povinné.";
        this.showWarningNotification("Prosím zadejte Vaše jméno");
      } else if (name.length < 2) {
        this.errors.name = "Jméno musí mít alespoň 2 znaky.";
        this.showWarningNotification("Jméno je příliš krátké");
      } else if (name.length > 50) {
        this.errors.name = "Jméno je příliš dlouhé (max 50 znaků).";
        this.showWarningNotification("Jméno je příliš dlouhé");
      }
    },

    /**
     * Validate date of birth field on blur
     */
    validateDobField() {
      this.errors.dob = "";
      const dob = this.formData.dob.trim();

      if (!dob) {
        this.errors.dob = "Datum narození je povinné.";
        this.showWarningNotification("Prosím zadejte Vaše datum narození");
      } else if (!this.isValidDateFormat(dob)) {
        this.errors.dob = "Neplatný formát data. Použijte DD.MM.YYYY.";
        this.showWarningNotification(
          "Neplatný formát. Použijte DD.MM.YYYY"
        );
      } else if (!this.isValidDate(dob)) {
        this.errors.dob = "Zadejte platné datum narození.";
        this.showWarningNotification("Datum je neplatné nebo v budoucnosti");
      }
    },

    /**
     * Validate access code field on blur
     */
    validateCodeField() {
      this.errors.code = "";
      const code = this.formData.code.trim();

      if (!code) {
        this.errors.code = "Přístupový kód je povinný.";
        this.showWarningNotification("Prosím zadejte přístupový kód");
      } else if (code.length < 3) {
        this.errors.code = "Přístupový kód je příliš krátký.";
        this.showWarningNotification("Přístupový kód je příliš krátký");
      }
    },
  };
}
