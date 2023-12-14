// // Function to handle the Edit button click event
// function handleEditButtonClick(leftColumn, rightColumn) {
//   return function () {
//     // Toggle the visibility of the editable input field
//     const editableInput = leftColumn.querySelector(".editable-input");
//     editableInput.style.display = editableInput.style.display === "none" ? "block" : "none";

//     // Toggle the visibility of the dropdown menu
//     const statusDropdown = rightColumn.querySelector("#statusDropdown");
//     const dropdownMenu = rightColumn.querySelector(".dropdown-menu");
//     if (statusDropdown.getAttribute("data-status") === "APPROVED") {
//       statusDropdown.setAttribute("data-status", "PENDING"); // Change to your desired default status
//       statusDropdown.textContent = "PENDING"; // Change to your desired default status label
//     }
//     dropdownMenu.style.display = dropdownMenu.style.display === "none" ? "block" : "none";
//   };
// }


