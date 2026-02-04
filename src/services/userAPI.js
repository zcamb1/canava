import {API_BASE_URL} from "../config";

export async function checkInAndFetchCount() {
  const storedUserId = localStorage.getItem("chatbotUserId");
  const currentUserId = storedUserId || crypto.randomUUID();
  if (!storedUserId) {
    localStorage.setItem("chatbotUserId", currentUserId);
  }
  try {
    await fetch(`${API_BASE_URL}/user_checkin/${currentUserId}`, {
      method: "POST",
    });
    const response = await fetch(`${API_BASE_URL}/active_users`);
    const data = await response.json();
    return data.count;
  } catch (error) {
    console.error("Failed to update active users:", error);
  }
}
