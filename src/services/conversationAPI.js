import { v4 as uuidv4 } from "uuid";
import {API_BASE_URL} from "../config";

export async function saveConversation(
  id,
  user_id,
  title,
  msgs,
  isPinned = false
) {
  try {
    const conversationData = {
      id: id,
      user_id: user_id,
      title: title,
      messages: msgs.map((msg) => ({
        id: msg.id,
        sender: msg.sender,
        text: msg.text,
        feedback: msg.feedback || "",
        thinkingContent: msg.thinkingContent || "",
        isCopied: msg.isCopied || false,
        isLiked: msg.isLiked || false,
        isDisliked: msg.isDisliked || false,
      })),
      isPinned: isPinned,
      lastUpdated: new Date().toISOString(),
    };
    // console.log(
    //   "DEBUG (App.jsx): Sending save request for ID:",
    //   id,
    //   "with title:",
    //   title,
    //   "and messages:",
    //   msgs,
    //   "Messages",
    //   conversationData
    // );
    const response = await fetch(`${API_BASE_URL}/save_conversation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(conversationData),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    console.log("Conversation saved successfully!");
    return conversationData;
  } catch (error) {
    console.error("Error saving conversation:", error);
  }
}

export async function fetchConversation(id, user_id) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/conversation/${user_id}/${id}`
    );
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    // Ensure data.messages is an array, even if empty or null from backend
    // console.log(
    //   "DEBUG (App.jsx): Received messages from backend for ID:",
    //   id,
    //   "count:",
    //   (data.messages || []).length,
    //   "title:",
    //   data.title
    // );
    const loadedMessages = (data.messages || []).map((msg) => ({
      id: msg.id || uuidv4(),
      sender: msg.sender,
      text: msg.text,
      isStreaming: msg.isStreaming,
      feedback: msg.feedback,
      showFeedbackForm: msg.showFeedbackForm || false,
      thinkingContent: msg.thinkingContent || "",
      isThinkingOpen: msg.isThinkingOpen || false,
      isCopied: msg.isCopied || false,
      isLiked: msg.isLiked || false,
      isDisliked: msg.isDisliked || false,
    }));
    const loadedId = data.id;
    const loadedTitle = data.title;
    return { loadedMessages, loadedId, loadedTitle };
  } catch (error) {
    console.error("Error loading conversation:", error);
    const loadedMessages = [];
    const loadedId = null;
    const loadedTitle = "New Chat";
    return { loadedMessages, loadedId, loadedTitle };
  }
}

export async function handlePinConversation(
  user_id,
  convId,
  currentPinnedStatus
) {
  try {

    const response = await fetch(`${API_BASE_URL}/pin_conversation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: user_id,
        conversation_id: convId,
        is_pinned: !currentPinnedStatus, // Toggle the status
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    console.log("Conversation pin status updated successfully!");
  } catch (error) {
    console.error("Error updating pin status:", error);
  }
}

export async function handleDeleteConversation(user_id, convId) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/conversation/${user_id}/${convId}`,
      {
        method: "DELETE",
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    console.log("Conversation deleted successfully!");
    // Re-fetch conversations to update the sidebar
    const updatedConversations = await fetchConversations(user_id);
    // Sort conversations: pinned first, then by lastUpdated (desc)
    const sortedData = updatedConversations.sort((a, b) => {
      if (a.isPinned && !b.isPinned) return -1;
      if (!a.isPinned && b.isPinned) return 1;
      return new Date(b.lastUpdated) - new Date(a.lastUpdated);
    });
    return sortedData;
  } catch (error) {
    console.error("Error deleting conversation:", error);
  }
}

export async function fetchConversations(user_id) {
  try {
    const response = await fetch(`${API_BASE_URL}/conversations/${user_id}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    // Sort conversations only on initial fetch
    return data;
  } catch (error) {
    console.error("Error fetching conversations:", error);
    // Optionally display an error message to the user
  }
}

export async function submitRename(user_id, convId, newTitle) {
  try {
    const response = await fetch(`${API_BASE_URL}/rename_conversation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: user_id,
        conversation_id: convId,
        new_title: newTitle.trim(),
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    console.log("Conversation renamed successfully!");
  } catch (error) {
    console.error("Error renaming conversation:", error);
  }
}
