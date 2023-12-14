
// Function to reset the filter and show all rows
function clearFilter() {
 

  // Redirect to the desired URL
  window.location.href = "/timesheet/"; // Replace with your desired URL
}

// Add event listener for the "Clear Filter" button
document.getElementById("clearFilter").addEventListener("click", function () {
  console.log("Clear Filter button clicked"); // Log a message when the button is clicked
  clearFilter();
});

// Add event listener for the "Apply Filter" button
document.getElementById("applyFilterButton").addEventListener("click", function (event) {
  event.preventDefault(); // Prevent the default form submission behavior

  // ... (your existing filter code, as shown in the previous response)

  // Show or hide the filterResultContainer based on whether any rows match the filter criteria
  const filterResultContainer = document.getElementById("filterResultContainer");
  filterResultContainer.style.display = atLeastOneRowDisplayed ? "block" : "none";
});








