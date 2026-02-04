import {API_BASE_URL} from "../config";

export async function callFastAPIRagAPI(
  userid,
  conid,
  prompt,
  signal,
  onChunk
) {
  try {
    const payload = new URLSearchParams({
      query: prompt,
      userid: userid,
      conid: conid,
    });
    const apiUrl = `${API_BASE_URL}/agent_chat?${payload.toString()}`;
    const response = await fetch(apiUrl, { signal: signal });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `HTTP error! status: ${response.status}, body: ${errorText}`
      );
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      // onChunk(chunk);
      buffer += chunk;
      if (buffer.length > 10) {
        onChunk(buffer);
        buffer = "";
      }
    }

    if (buffer) {
      onChunk(buffer);
    }
  } catch (error) {
    if (error.name === "AbortError") {
      console.log("Request was aborted.");
    } else {
      console.error("Error calling FastAPI RAG API:", error);
    }
  }
}

export async function generateTitle() {
  try {
    const response = await fetch(`${API_BASE_URL}/generate_title`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    let generatedTitle = data.title.trim();

    // Capitalize the first character of the generated title
    if (generatedTitle.length > 0) {
      generatedTitle =
        generatedTitle.charAt(0).toUpperCase() + generatedTitle.slice(1);
    }

    // Limit to 50 characters to keep it concise for the sidebar
    return (
      generatedTitle.substring(0, 50) +
      (generatedTitle.length > 50 ? "..." : "")
    );
  } catch (error) {
    console.error("Error generating title with backend:", error);
    return "Untitled Chat";
  }
}
