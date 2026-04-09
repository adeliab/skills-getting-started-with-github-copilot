document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message and reset dropdown
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";
        activityCard.setAttribute("data-activity", name);

        const spotsLeft = details.max_participants - details.participants.length;

        const activityTitle = document.createElement("h4");
        activityTitle.textContent = name;
        activityCard.appendChild(activityTitle);

        const description = document.createElement("p");
        description.textContent = details.description;
        activityCard.appendChild(description);

        const schedule = document.createElement("p");
        schedule.innerHTML = `<strong>Schedule:</strong> ${details.schedule}`;
        activityCard.appendChild(schedule);

        const availability = document.createElement("p");
        availability.innerHTML = `<strong>Availability:</strong> ${spotsLeft} spots left`;
        activityCard.appendChild(availability);

        const participantsSection = document.createElement("div");
        participantsSection.className = "participants-section";

        const participantsHeading = document.createElement("p");
        participantsHeading.innerHTML = "<strong>Participants</strong>";
        participantsSection.appendChild(participantsHeading);

        if (details.participants.length) {
          const participantsList = document.createElement("ul");
          participantsList.className = "participants-list";

          details.participants.forEach((participant) => {
            const participantItem = document.createElement("li");
            participantItem.className = "participant-item";

            const participantName = document.createElement("span");
            participantName.textContent = participant;
            participantItem.appendChild(participantName);

            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
            deleteButton.className = "participant-delete-button";
            deleteButton.title = `Remove ${participant}`;
            deleteButton.textContent = "✕";
            deleteButton.addEventListener("click", () => {
              unregisterParticipant(name, participant);
            });

            participantItem.appendChild(deleteButton);
            participantsList.appendChild(participantItem);
          });

          participantsSection.appendChild(participantsList);
        } else {
          const noParticipants = document.createElement("p");
          noParticipants.className = "no-participants";
          noParticipants.textContent = "No participants signed up yet.";
          participantsSection.appendChild(noParticipants);
        }

        activityCard.appendChild(participantsSection);
        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  async function unregisterParticipant(activity, email) {
    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/participants/${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "Unable to remove participant.";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to remove participant. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error removing participant:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Update the activity card directly
        const activityCard = document.querySelector(`[data-activity="${activity}"]`);
        if (activityCard) {
          const participantsSection = activityCard.querySelector('.participants-section');
          const noParticipants = participantsSection.querySelector('.no-participants');
          if (noParticipants) {
            noParticipants.remove();
            const participantsList = document.createElement('ul');
            participantsList.className = 'participants-list';
            participantsSection.appendChild(participantsList);
          }
          const participantsList = participantsSection.querySelector('.participants-list');
          const participantItem = document.createElement('li');
          participantItem.textContent = email;
          const deleteButton = document.createElement('button');
          deleteButton.type = "button";
          deleteButton.className = "participant-delete-button";
          deleteButton.title = `Remove ${email}`;
          deleteButton.textContent = "✕";
          deleteButton.addEventListener("click", () => {
            unregisterParticipant(activity, email);
          });
          participantItem.appendChild(deleteButton);
          participantsList.appendChild(participantItem);
          // Update availability
          const spotsLeftP = activityCard.querySelector('p:nth-of-type(4)');
          const spotsLeftText = spotsLeftP.textContent;
          const currentSpots = parseInt(spotsLeftText.match(/(\d+) spots left/)[1]);
          spotsLeftP.textContent = spotsLeftP.textContent.replace(`${currentSpots} spots left`, `${currentSpots - 1} spots left`);
        }
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
