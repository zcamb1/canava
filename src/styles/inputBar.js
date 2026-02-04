export const chatInputContainerStyle = {
  display: "flex",
  flexDirection: "column",
  padding: "12px",
  backgroundColor: "#FFFFFF",
  borderRadius: "20px",
  boxShadow: "0 4px 6px rgba(0, 0, 0, 0.05)",
  border: "1px solid #e1e0de",
  maxWidth: "120%",
  fontFamily:
    '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
};

export const topLayerStyle = {
  paddingTop: "6px",
  paddingLeft: "10px",
  paddingRight: "10px",
};

export const chatInputFieldStyle = {
  width: "100%",
  border: "none",
  background: "transparent",
  outline: "none",
  fontSize: "16px",
  color: "#333",
  resize: "none",
  overflowY: "auto",
};

export const bottomLayerStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  paddingTop: "0px",
  paddingLeft: "10px",
  paddingRight: "10px",
};

export const chatInputLeftStyle = {
  display: "flex",
  alignItems: "center",
  gap: "8px",
};

export const chatInputRightStyle = {
  display: "flex",
  alignItems: "center",
  gap: "16px",
};

export const stopButtonStyle = {
  backgroundColor: "#FFFFFF",
  color: "white",
  border: "2px solid #d4d4d4",
  borderRadius: "12px",
  width: "40px",
  height: "40px",
  fontSize: "20px",
  cursor: "pointer",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  transition: "background-color 0.2s, border-color 0.2s",
};

export const stopIconStyle = {
  width: "20px",
  height: "20px",
  fill: "black",
};

export const sendButtonStyle = (disabled) => ({
  backgroundColor: disabled ? "#d1d5db" : "#2563eb",
  color: "white",
  border: "none",
  borderRadius: "12px",
  width: "40px",
  height: "40px",
  fontSize: "20px",
  cursor: "pointer",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  transition: "background-color 0.2s",
});

export const sendIconStyle = {
  width: "20px",
  height: "20px",
  fill: "white",
};
