

  document.addEventListener("DOMContentLoaded", function () {
    const dynamicRowsContainer = document.getElementById("dynamic-rows-container");
    const newRowButton = document.getElementById("new-row-button");
    const totalHoursInput = document.querySelector(".total-hours-input");
    const hoursField = document.querySelector('input[name="hours[]"]');

    let rowCounter = 0;
    const selectedUserIds = new Set(); // Store selected user IDs

    hoursField.addEventListener("input", function() {
      // Update the value of the total hours input
      updateTotalHours();
  });
  function updateTotalHours() {
    // Get all the hours input fields
    const allHoursInputs = document.querySelectorAll('input[name^="hours"]');
    
    // Calculate the total hours
    const totalHours = Array.from(allHoursInputs)
        .map(input => parseFloat(input.value) || 0)
        .reduce((total, hours) => total + hours, 0);
    
    // Update the value of the total hours input
    totalHoursInput.value = totalHours.toFixed(2); // Displaying with two decimal places, adjust as needed
}

// Add event listener for each hours input field
document.querySelectorAll('input[name^="hours"]').forEach(input => {
    input.addEventListener("input", updateTotalHours);
});

// Event listener for the "New" button
newRowButton.addEventListener("click", function () {
    createRowWithData();
    updateTotalHours(); // Update total hours when a new row is added
});

// Event listener for remove button in each row
dynamicRowsContainer.addEventListener("click", function (event) {
    const target = event.target;
    if (target.classList.contains("remove-btn")) {
        dynamicRowsContainer.removeChild(target.closest(".template-row"));
        updateTotalHours(); // Update total hours when a row is removed
    }
});

    // Function to create a new row with data from user selection and hours
 // Function to create a new row with data from user selection and hours
function createRowWithData() {
  rowCounter++;

  const selectedUserField = document.querySelector(`select[name="selected_user[]"]`);
  const hoursInputField = document.querySelector(`input[name="hours[]"]`);
  console.log("hou:", hoursInputField);

  // Get the selected user ID and name
  const userId = selectedUserField.value;
  const userName = selectedUserField.options[selectedUserField.selectedIndex].text;

  // Get the entered hours
  const hours = hoursInputField.value;

  // Add the selected user to the set of selected users
  selectedUserIds.add(userId);

  // Remove the selected user from the dropdown options
  selectedUserField.remove(selectedUserField.selectedIndex);

  const newRow = document.createElement("div");
  newRow.className = "row template-row";
  newRow.innerHTML = `
      <div class="col mt-2">
          <label for="addHours" class="selected-user">Select User</label>
          <select class="form-select" aria-label="Default select example" name="selected_user_${rowCounter}">
              <option value="${userId}" selected>${userName}</option>
          </select>
      </div>
      <div class="col mt-2">
          <label for="addHours" class="mx-3">Add Hours:</label>
          <div class="col-sm-10">
              <input type="number" class="form-control" name="hours_${rowCounter}" value="${hours}">
          </div>
      </div>
      <div class="col mt-4">
          <button type="button" class="remove-btn">Remove</button>
      </div>
  `;

  dynamicRowsContainer.appendChild(newRow);

  // Add event listener for the remove button
  const removeRowButton = newRow.querySelector(".remove-btn");
  removeRowButton.addEventListener("click", function () {
      dynamicRowsContainer.removeChild(newRow);

      // Remove the user from the set of selected users and re-add to the dropdown options
      selectedUserIds.delete(userId);
      selectedUserField.appendChild(new Option(userName, userId));

      // Update the total hours when a row is removed
      updateTotalHours();
  });

  // Clear the user selection and hours fields after adding a row
  selectedUserField.value = "";
  hoursInputField.value = "";
}



 

    // Function to handle form submission
    function handleFormSubmit() {
        const selectedUserField = document.querySelector(`select[name="selected_user[]"]`);
        const hoursField = document.querySelector(`input[name="hours[]"]`);
        const totalUserTime = totalHoursInput.value;

        if (selectedUserField.value && hoursField.value) {
            // If there is a selected user and hours, create a row and submit the form
            createRowWithData();
        } else if (selectedUserIds.size > 0) {
            // If there are multiple users, and the "New" button has been used, submit the form
        } else {
            // If no user is selected, show an error message or take appropriate action
            alert("Please select at least one user and provide hours.");
        }
    }

    // Add event listener for form submission
    const submitButton = document.querySelector("button[name='action'][value='request']");
    submitButton.addEventListener("click", handleFormSubmit);

// Inside your JavaScript code
function createCard(allotmentId, users, allotment) {
  const newCard = document.createElement("div");
  newCard.className = "card";

  const cardRow = document.createElement("div");
  cardRow.className = "row";

  // Create a container for card content with overflow
  const cardContentContainer = document.createElement("div");
  cardContentContainer.className = "card-content-container"; // Add 'overflow-auto' class

  const leftColumn = document.createElement("div");
  leftColumn.className = "col-md-7 border-end"; // Add 'border-end' class for vertical line

  // Left column content
  const userRows = users
    .map(
      (user, index) => `
      <div class="row mt-2" data-allotment-id="${allotmentId}">
        <div class="col-md-2 mx-4">${index + 1}</div>
        <div class="col-md-4 inline-container">
          <img class="ellipse" src="/static/assets/img/836.jpg" alt="User Image" width="26" height="26" />
          <span>${user.name}</span>
        </div>
        <div class="col-md-2">
          <span class="editable-value user_time" name="user_time_${index}" data-user-id="${user.id}" data-field="user_time">${user.user_time}</span>
          <input type="number" class="editable-input user_time" style="display: none" data-user-id="${user.id}" data-field="user_time" />
        </div>
        <div class="col-md-2">
          <span class="editable-value user_alloted" name="user_alloted_${index}" data-user-id="${user.id}" data-field="user_alloted">${user.user_alloted}</span>
          <input type="number" class="editable-input user_alloted" style="display: none" data-user-id="${user.id}" data-field="user_alloted" />
        </div>
      </div>
      <hr />
    `
    )
    .join("");

  leftColumn.innerHTML = `
    <input type="hidden" name="allotment_id" class="allotmentID" value="${allotmentId}" />
    ${userRows}
  `;

  const rightColumn = document.createElement("div");
  rightColumn.className = "col-md-5";

  // Format the date as "12 Oct 2023"
  const formattedDate = new Date(allotment.created_at).toLocaleDateString('en-US', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });


 // Calculate the total user time for this group of users
 const totalUserTime = users.reduce((total, user) => total + parseFloat(user.user_time), 0);
 const totalAllottedTime = users.reduce((total, user) => {
  const allottedTime = parseFloat(user.user_alloted);
  return isNaN(allottedTime) ? total : total + allottedTime;
}, 0);


 // Right column content
 rightColumn.innerHTML = `
   <div class="col-md-12 mt-2">
     <div class="row total-requested-time mb-3">
       <div class="col-md-6">Total Requested Time</div>
       <div class="col-md-6">
         <div class="time-div">
           <span class="hrs">${totalUserTime} hrs</span>
         </div>
       </div>
     </div>
     <div class="row total-requested-time">
       <div class="col-md-6">Total Allotment Time</div>
       <div class="col-md-6">
         <div class="time-div">
           <span class="all-hrs">${totalAllottedTime} hrs</span>
         </div>
       </div>
     </div>
     <div class="row mt-5">
       <div class="col-md-6 requested-date">Requested Date</div>
       <div class="col-md-6 oct-2023">${formattedDate}</div>
     </div>
     <div class="row mt-5 request-status">
       <div class="col-md-6">Request Status</div>
       {% if request.session.adminId %}
       <div class="col-md-6">
         <select class="status-select ${allotment.status === 'APPROVED' ? 'btn-approved' : 'btn-pending'}">
           <option value="PENDING" ${allotment.status === "PENDING" ? 'selected' : ''}>PENDING</option>
           <option value="APPROVED" ${allotment.status === "APPROVED" ? 'selected' : ''}>APPROVED</option>
         </select>
       </div>
       {% else %}
       <div class="col-md-6">
         <div class="status-select ${allotment.status === 'APPROVED' ? 'btn-approved1' : 'btn-pending1'}">
           ${allotment.status}
         </div>
       </div>
       {% endif %}
     </div>
     <div class="row mt-5 button-container">
       <div class="col-md-6">
         {% if request.session.adminId %}
         <button class="btn-delete" data-allotment-id="${allotmentId}">Delete</button>
         {% endif %}
       </div>
       <div class="col-md-6">
        ${
            (allotment.status === 'APPROVED' && managerId) ? 
            '' : 
            `<button class="btn-edit mb-3" id="editButton">Edit</button>`
        }
        <button class="btn-save mb-3" style="display: none" data-allotment-id="${allotmentId}" id="saveButton">Save</button>
    </div>
     </div>
   </div>
 `;

 cardRow.appendChild(leftColumn);
 cardRow.appendChild(rightColumn);

 // Add the card content container to hold the overflow
 cardContentContainer.appendChild(cardRow);
 newCard.appendChild(cardContentContainer);

 cardContainer.appendChild(newCard);
}

// Your Django context variables
const adminId = "{{ request.session.adminId }}";
const managerId = "{{ request.session.managerId }}"; 

const cardContainer = document.getElementById("card-container");

// Inside your event listener
cardContainer.addEventListener("click", function (event) {
  const target = event.target;

  if (target.classList.contains("btn-edit") || target.classList.contains("btn-save")) {
      const parentCard = target.closest(".card");

      if (!parentCard) {
          console.log("Parent card not found");
          return;
      }

      const editableValuesAlloted = parentCard.querySelectorAll(".editable-value.user_alloted");
      const editableInputsAlloted = parentCard.querySelectorAll(".editable-input.user_alloted");

      const editableValuesTime = parentCard.querySelectorAll(".editable-value.user_time");
      const editableInputsTime = parentCard.querySelectorAll(".editable-input.user_time");

      // Toggle between "Edit" and "Save" modes
      if (target.textContent === "Edit") {
          // Change button text to "Save"
          target.textContent = "Save";
          target.className = "btn-save mb-3";

          if (adminId) {
              // Admin role can edit "user_alloted" and "req-status"
              toggleEdit(editableValuesAlloted, editableInputsAlloted);
              const statusSelect = parentCard.querySelector(".status-select");
              statusSelect.disabled = false; // Enable the status dropdown
          } else if (managerId) {
              // Manager role can edit "user_time"
              toggleEdit(editableValuesTime, editableInputsTime);
          }
      } else if (target.textContent === "Save") {
          // Change button text back to "Edit"
          target.textContent = "Edit";
          target.className = "btn-edit mb-3";

          if (adminId) {
              // Admin role saves the edited "user_alloted" values and status
              saveEdits(editableValuesAlloted, editableInputsAlloted, parentCard);
          } else if (managerId) {
              // Manager role saves the edited "user_time" values
              saveEdits(editableValuesTime, editableInputsTime, parentCard);
          }
      }
  } else if (target.classList.contains("btn-delete")) {
      // Handle "Delete" button click
      if (adminId) {
          // Admin role can perform delete
          const allotmentId = target.getAttribute("data-allotment-id");

          if (!allotmentId) {
              console.error("Allotment ID is missing or invalid.");
              return;
          }

          // Confirm the deletion with a dialog
          if (confirm("Are you sure you want to delete this allotment?")) {
              // Send a request to the Django view to delete the allotment
              const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
              fetch(`/delete-allotment/${allotmentId}/`, {
                  method: "POST",
                  headers: {
                      "X-CSRFToken": csrfToken, // Include the CSRF token in the headers
                      "Content-Type": "application/json", // Set content type to JSON
                  },
              })
              .then((response) => response.json())
              .then((data) => {
                  if (data.success) {
                      // Handle success, e.g., remove the deleted card from the UI
                      target.closest(".card").remove();
                      alert("Allotment deleted successfully!");
                  } else {
                      // Handle error, e.g., display an error message
                      alert("Error: " + data.error);
                  }
              });
          }
      }
  }
});


function toggleEdit(editableValues, editableInputs) {
    editableValues.forEach((value, index) => {
        value.style.display = "none";
        editableInputs[index].style.display = "inline-block";
        editableInputs[index].value = value.textContent;
    });
}

function saveEdits(editableValues, editableInputs, parentCard) {
    const updatedData = [];

    editableValues.forEach((value, index) => {
      const userId = value.getAttribute("data-user-id");
      const newValue = editableInputs[index].value;
      const field = editableInputs[index].getAttribute("data-field"); // Get the field name
  
      updatedData.push({ userId, field, newValue });
  });
  

    const allotmentId = parentCard.querySelector(".allotmentID").value;
    const newStatus = parentCard.querySelector(".status-select").value;

    // Prepare the data to send to the server
    const requestData = {
        allotment_id: allotmentId,
        user_data: updatedData,
        new_status: newStatus,
    };
  
    

    // Send a POST request to the Django view to save the updates
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const headers = {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken, // Include the CSRF token in the headers
  };
    fetch("/update-allotment/", {
        method: "POST",
        headers: headers, 
        body: JSON.stringify(requestData),
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.success) {
            alert("Changes saved successfully!");
            location.reload(); 
        } else {
            alert("Error: " + data.error);
        }
    });
}

  // Your existing code for parsing data and grouping
  const allotmentUsersData = JSON.parse('{{ allotment_users|escapejs }}');
  console.log(allotmentUsersData);

  const allotmentsData = JSON.parse('{{ allotments|escapejs }}');
  console.log(allotmentsData);

  const userData = JSON.parse('{{ user_info_json|escapejs }}');
  console.log(userData);

  // Create a map to group users by allotment_id
  const usersByAllotment = new Map();

  // Assuming you have loaded allotmentUsersData, allotmentsData, and userData

  allotmentUsersData.forEach((allotmentUserData) => {
    const userId = allotmentUserData.user_id;
    const allotmentId = allotmentUserData.allotment_id;

    // Find user data based on user ID
    const user = userData.find((user) => user.id === userId);

    if (user) {
      // If the allotment_id key doesn't exist in the map, create it with an array
      user.user_alloted = allotmentUserData.user_alloted;
      if (!usersByAllotment.has(allotmentId)) {
        usersByAllotment.set(allotmentId, []);
      }

      // Push the user data to the array under the corresponding allotment_id
      usersByAllotment.get(allotmentId).push({ ...user, user_time: allotmentUserData.user_time });
     
    }
  });

  // Now, you can access and use the grouped user data for each allotment_id
  // ...

  // Now, you can access and use the grouped user data for each allotment_id
  usersByAllotment.forEach((users, allotmentId) => {
    const allotment = allotmentsData.find((allotment) => allotment.id === allotmentId);

    if (allotment) {
      // Access allotment data here
      console.log(`Allotment ID: ${allotmentId}`);
      console.log(`Allotment Status: ${allotment.status}`);
      console.log(`Allotment Created At: ${allotment.created_at}`); // Add this line to display created_at

      // Access user data for this allotment and display user_time
      users.forEach((user_details) => {
        console.log(`User Name: ${user_details.name}`);
        console.log(`Profile Image: ${user_details.profile_image}`);
        console.log(`User Time: ${user_details.user_time}`);
        console.log(`User Alloted: ${user_details.user_alloted}`);
  
      });

      // Create cards for each group of users and allotment data
      createCard(allotmentId, users, allotment);
    }
  });

  // Group users by allotment_id
  const groupedUsers = {};
  allotmentUsersData.forEach(user => {
    const allotmentId = user.allotment_id;
    if (!groupedUsers[allotmentId]) {
      groupedUsers[allotmentId] = [];
    }
    groupedUsers[allotmentId].push(user);
  });

  // Create cards for each group of users
  for (const allotmentId in groupedUsers) {
    createCard(allotmentId, groupedUsers[allotmentId]);

  }


    });
    







