export const feedbackContainerStyle = {
  display: "flex",
  flexDirection: "column",
  padding: "6px",
  backgroundColor: "#ffffff",
  borderRadius: "10px",
  border: "2px solid #e1e0de",
  maxWidth: "120%",
  marginTop: "10px",
  fontFamily:
    '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
};

export const topFeedbackLayerStyle = {
  paddingLeft: "10px",
  paddingRight: "10px",
};

export const feedbackInputFieldStyle = {
  paddingTop: "10px",
  paddingLeft: "10px",
  borderRadius: "10px",
  // border: '1px solid #e1e0de',
  boder: "none",
  width: "100%",
  background: "#ffffff",
  outline: "none",
  fontSize: "16px",
  color: "#333",
  resize: "none",
  overflowY: "auto",
};

export const bottomFeedbackLayerStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  paddingTop: "4px",
  paddingLeft: "10px",
  paddingRight: "10px",
  paddingBottom: "4px",
};

export const feedbackInputLeftStyle = {
  display: "flex",
  alignItems: "center",
  gap: "8px",
};

export const feedbackInputRightStyle = {
  display: "flex",
  alignItems: "center",
  gap: "8px",
};

export const cancelButtonStyle = {
  backgroundColor: "#4b5563",
  color: "#ffffff",
  borderRadius: "6px",
  border: "1px solid #e1e0de",
  width: "80px",
  height: "30px",
  fontSize: "16px",
  cursor: "pointer",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  transition: "background-color 0.2s",
};

export const submitButtonStyle = (disabled) => ({
  backgroundColor: disabled ? "#d1d5db" : "#2563eb",
  color: "#ffffff",
  border: "1px solid #e1e0de",
  borderRadius: "6px",
  width: "80px",
  height: "30px",
  fontSize: "16px",
  cursor: "pointer",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  transition: "background-color 0.2s",
});
