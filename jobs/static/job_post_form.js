// static/job_post_form.js

document.addEventListener("DOMContentLoaded", () => {
    // Keep file input handling, animations, tooltips, etc. from previous versions...

    // File input handling (make sure updateFileName function is defined)
    function updateFileName(input, filenameDisplayId) {
        const filenameDisplay = document.getElementById(filenameDisplayId);
        if (!input || !filenameDisplay) return;
        if (input.files && input.files.length > 0) {
            filenameDisplay.textContent = input.files[0].name;
        } else if (!input.value) { // Only reset if no file actually selected
            filenameDisplay.textContent = "ფაილი არ არის არჩეული";
        }
    }
    const documentInput = document.getElementById("id_document");
    if (documentInput) {
        documentInput.addEventListener("change", function () { updateFileName(this, "document_filename"); });
        updateFileName(documentInput, "document_filename"); // Initial check
    }
    const logoInput = document.getElementById('id_company_logo');
    const logoFilename = document.getElementById('logo_filename');
    if (logoInput) {
        logoInput.addEventListener('change', function() { updateFileName(this, "logo_filename"); });
        updateFileName(logoInput, "logo_filename"); // Initial check
    }
    // End File Input Handling

    // --- Combined Product/Quantity Logic ---
    const productContainer = document.getElementById("product-container");
    const addProductButton = document.getElementById("add-product");
    const totalPriceElement = document.getElementById("total-price");
    const form = document.getElementById("job-post-form");
    const hiddenDataContainer = document.getElementById("hidden-product-data-container");

    // --- Price Update Function ---
    function updateTotalPrice() {
        let total = 0;
        productContainer.querySelectorAll(".product-group").forEach(group => {
            const select = group.querySelector(".product-select");
            const quantityInput = group.querySelector(".quantity-input");
            const selectedProduct = select.value;
            const quantity = parseInt(quantityInput.value || 0, 10);
            const pricePerUnit = PRODUCT_PRICES[selectedProduct] || 0;

            if (quantity >= 1 && pricePerUnit > 0) { // Ensure valid quantity and price
                total += quantity * pricePerUnit;
            }
        });
        totalPriceElement.textContent = `₾${total}`;
    }

    // --- Event Handlers ---
    function attachProductGroupListeners(group) {
        const select = group.querySelector(".product-select");
        const quantityInput = group.querySelector(".quantity-input");
        const minusButton = group.querySelector(".minus");
        const plusButton = group.querySelector(".plus");
        const removeButton = group.querySelector(".remove-product");

        // Update price when select changes
        select.addEventListener("change", updateTotalPrice);

        // Update price and validate input value on change/input
        quantityInput.addEventListener("input", () => {
            let value = parseInt(quantityInput.value, 10);
            if (isNaN(value) || value < 1) {
                quantityInput.value = 1; // Enforce minimum 1
            }
            updateTotalPrice();
        });
         quantityInput.addEventListener("change", () => { // Handle leaving field
            let value = parseInt(quantityInput.value, 10);
            if (isNaN(value) || value < 1) {
                quantityInput.value = 1; // Enforce minimum 1
            }
            updateTotalPrice();
         });


        // Quantity button clicks
        minusButton.addEventListener("click", () => {
            let currentValue = parseInt(quantityInput.value, 10);
            if (currentValue > 1) { // Check if > 1 before decrementing
                quantityInput.value = currentValue - 1;
                updateTotalPrice();
            }
        });
        plusButton.addEventListener("click", () => {
            quantityInput.value = parseInt(quantityInput.value, 10) + 1;
            updateTotalPrice();
        });

        // Remove button click
        if (removeButton) {
            removeButton.addEventListener("click", () => {
                group.remove();
                updateTotalPrice(); // Update price after removal
            });
        }
    }

    // --- Add Product Button ---
    addProductButton.addEventListener("click", () => {
        const firstGroup = productContainer.querySelector(".product-group");
        if (!firstGroup) return; // Should not happen, but safety check

        const newGroup = firstGroup.cloneNode(true); // Deep clone

        // Reset quantity to 1 in the clone
        const newQuantityInput = newGroup.querySelector(".quantity-input");
        newQuantityInput.value = 1;

        // Make the remove button visible
        const removeButton = newGroup.querySelector(".remove-product");
        if (removeButton) {
            removeButton.style.display = "inline-block";
        }

        // Append the new group
        productContainer.appendChild(newGroup);

        // Attach listeners to the *new* group's elements
        attachProductGroupListeners(newGroup);

        // Update total price
        updateTotalPrice();
    });

    // --- Attach Listeners to the Initial Group ---
    const initialGroup = productContainer.querySelector(".product-group");
    if (initialGroup) {
        attachProductGroupListeners(initialGroup);
    }

    // --- Form Submission Handling ---
    form.addEventListener("submit", (event) => {
        event.preventDefault(); // Stop default submission

        // Clear any previously added hidden inputs
        hiddenDataContainer.innerHTML = '';

        // Create hidden inputs based on current selections and quantities
        let hasProducts = false;
        productContainer.querySelectorAll(".product-group").forEach(group => {
            const select = group.querySelector(".product-select");
            const quantityInput = group.querySelector(".quantity-input");
            const selectedProduct = select.value;
            const quantity = parseInt(quantityInput.value || 0, 10);

            if (selectedProduct && quantity >= 1) {
                hasProducts = true;
                // Add one hidden input for *each unit* of quantity
                for (let i = 0; i < quantity; i++) {
                    const hiddenInput = document.createElement("input");
                    hiddenInput.type = "hidden";
                    hiddenInput.name = "products"; // This is the name the backend expects
                    hiddenInput.value = selectedProduct;
                    hiddenDataContainer.appendChild(hiddenInput);
                }
            }
        });

        // Basic check: ensure at least one product is selected if required
        // Add more robust validation as needed
        if (!hasProducts) {
             alert("Please select at least one product and set its quantity."); // Or show error message near products
             return; // Stop submission
        }


        // Now, submit the form programmatically
        // This will include the original form fields PLUS the hidden inputs we just added
        form.submit();
    });

    // --- Initialize Total Price on Load ---
    updateTotalPrice();
    // --- End Combined Product/Quantity Logic ---

    // Keep back/forward cache handling if needed
     window.addEventListener('pageshow', function(event) {
      if (event.persisted) {
        form.reset(); // Reset form fields might work partially
        // Manually reset file inputs and trigger price update
         updateFileName(document.getElementById("id_document"), "document_filename");
         updateFileName(document.getElementById('id_company_logo'), "logo_filename");
         // Reset dynamic products might be complex, reload might be better
         // Or manually set initial product group state and remove others
         // For simplicity after bfcache, a reload might be the most reliable
         window.location.reload();
      }
    });

}); // End DOMContentLoaded