import { API_BASE_URL } from "../config";

/**
 * Upload a .txt file to the server for a specific conversation
 * @param {string} conversationId - The conversation ID
 * @param {File} file - The file to upload
 * @returns {Promise<object>} Response containing file info and content
 */
export async function uploadFileToConversation(conversationId, file) {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(
      `${API_BASE_URL}/conversation/${conversationId}/upload_file`,
      {
        method: "POST",
        body: formData,
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("✅ File uploaded successfully:", data.filename);
    return data;
  } catch (error) {
    console.error("❌ Error uploading file:", error);
    throw error;
  }
}
