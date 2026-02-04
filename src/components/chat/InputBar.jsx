import { memo } from "react";
import { useState, useRef, useEffect, useCallback } from "react";
import { useUser } from "../../context/UserContext";
import { useMessage } from "../../context/MessageContext";
import { useConversation } from "../../context/ConversationContext";
import { v4 as uuidv4 } from "uuid";
import StopGenIcon from "../../icons/StopGenIcon";
import SendIcon from "../../icons/SendIcon";
import AttachIcon from "../../icons/AttachIcon";
import { uploadFileToConversation } from "../../services/uploadAPI";
import { scrollToBottomImmediatelyFunc } from "../../hooks/scrolling";
import {
  chatInputContainerStyle,
  topLayerStyle,
  chatInputFieldStyle,
  bottomLayerStyle,
  chatInputLeftStyle,
  chatInputRightStyle,
  stopButtonStyle,
  stopIconStyle,
  sendButtonStyle,
  sendIconStyle,
} from "../../styles/inputBar.js";

function InputBar({ chatDisplayRef }) {
  const {
    messages,
    textareaRef,
    isLoading,
    forceScrollToBottomRef,
    scrollTimeoutRef,
    handleStopGenerationFunc,
    updateUserMessageFunc,
    callFastAPIRagAPIFunc,
  } = useMessage();
  const { userId } = useUser();
  const {
    conversations,
    currentConversationId,
    currentConversationTitle,
    setCurrentConversationIdFunc,
    saveConversationFunc,
    setCurrentConversationTitleFunc
  } = useConversation();
  const [inputText, setInputText] = useState("");
  const [uploadedFile, setUploadedFile] = useState(null);
  const [fileContent, setFileContent] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);
  const MAX_HEIGHT = 200;

  const { scrollToBottomImmediately } = scrollToBottomImmediatelyFunc(
    chatDisplayRef,
    messages,
    isLoading,
    forceScrollToBottomRef,
    scrollTimeoutRef
  );

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "40px";
      const newHeight = Math.min(textarea.scrollHeight, MAX_HEIGHT);
      textarea.style.height = `${newHeight}px`;
      textarea.style.overflowY =
        textarea.scrollHeight > MAX_HEIGHT ? "auto" : "hidden";
    }
  }, [inputText]);

  const handleInputChange = useCallback((e) => {
    setInputText(e.target.value);
  }, []);

  const handleInputHeight = (e) => {
    e.target.style.height = "auto";
    e.target.style.height = `${e.target.scrollHeight}px`;
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleStopGeneration = () => {
    const userMessageText = messages[messages.length - 2]?.text || "";
    setInputText(userMessageText);
    handleStopGenerationFunc();
  };

  const handleFileButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (file) {
      // Check if file is .txt
      if (!file.name.endsWith('.txt')) {
        alert('Hiện tại chỉ hỗ trợ file .txt');
        return;
      }
      
      setIsUploading(true);
      
      try {
        // Get or create conversation ID for upload
        const conversationId = currentConversationId || uuidv4();
        if (!currentConversationId) {
          setCurrentConversationIdFunc(conversationId);
        }
        
        // Upload file to server
        const response = await uploadFileToConversation(conversationId, file);
        
        // Set file info and content from server response
        setUploadedFile({
          name: response.filename,
          size: file.size,
          path: response.file_path
        });
        setFileContent(response.content);
        
        console.log('✅ File uploaded successfully:', response.filename);
      } catch (error) {
        console.error('❌ Error uploading file:', error);
        alert(`Lỗi khi upload file: ${error.message}`);
      } finally {
        setIsUploading(false);
      }
    }
    // Reset input value to allow selecting the same file again
    e.target.value = '';
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    setFileContent("");
  };

  const handleSendMessage = async () => {
    if (inputText.trim() === "" && !uploadedFile) return;
    
    const newConversationId = currentConversationId || uuidv4();
    setCurrentConversationIdFunc(newConversationId);
    scrollToBottomImmediately();
    
    // Combine file content with user input if file exists
    let finalPrompt = inputText.trim();
    if (uploadedFile && fileContent) {
      finalPrompt = `[File: ${uploadedFile.name}]\n\nNội dung file:\n${fileContent}\n\n---\n\nCâu hỏi: ${inputText.trim()}`;
    }
    
    setInputText("");
    setUploadedFile(null);
    setFileContent("");

    const titleForInitialSave = currentConversationTitle;
    const currentConv = conversations.find(
      (conv) => conv.id === newConversationId
    );
    const isCurrentPinned = currentConv ? currentConv.isPinned : false;

    updateUserMessageFunc(inputText);
    // Save the user message immediately. The title might be temporary for the first message.
    await saveConversationFunc(
      newConversationId,
      userId,
      titleForInitialSave,
      messages,
      isCurrentPinned,
      true
    );

    const newTitle = await callFastAPIRagAPIFunc(userId, newConversationId, finalPrompt);
    setCurrentConversationTitleFunc(newTitle);
  };

  return (
    <div className="w-full max-w-xl sm:max-w-2xl md:max-w-4xl lg:max-w-5xl xl:max-w-6xl mx-auto px-0 pb-4 ">
      <div style={chatInputContainerStyle}>
        {/* Uploading indicator */}
        {isUploading && (
          <div style={{
            padding: '8px 12px',
            margin: '8px 12px 0',
            backgroundColor: '#fef3c7',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px',
            color: '#92400e',
          }}>
            <span>⏳</span>
            <span>Đang upload file...</span>
          </div>
        )}

        {/* File preview area */}
        {uploadedFile && !isUploading && (
          <div style={{
            padding: '8px 12px',
            margin: '8px 12px 0',
            backgroundColor: '#f3f4f6',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '14px',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>📄</span>
              <span style={{ color: '#374151' }}>{uploadedFile.name}</span>
              <span style={{ color: '#9ca3af', fontSize: '12px' }}>
                ({(uploadedFile.size / 1024).toFixed(1)} KB)
              </span>
              <span style={{ color: '#10b981', fontSize: '12px' }}>✓ Uploaded</span>
            </div>
            <button
              onClick={handleRemoveFile}
              style={{
                padding: '4px 8px',
                backgroundColor: '#ef4444',
                color: 'white',
                borderRadius: '4px',
                border: 'none',
                cursor: 'pointer',
                fontSize: '12px',
              }}
            >
              ✕
            </button>
          </div>
        )}

        {/* Input area  */}
        <div style={topLayerStyle}>
          <textarea
            row="1"
            ref={textareaRef}
            placeholder="Ask me anything"
            value={inputText}
            onChange={handleInputChange}
            onInput={handleInputHeight}
            onKeyPress={handleKeyPress}
            style={chatInputFieldStyle}
          ></textarea>
        </div>

        <div style={bottomLayerStyle}>
          <div style={chatInputLeftStyle}>
            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
            {/* Attach file button */}
            <button
              onClick={handleFileButtonClick}
              disabled={isLoading || isUploading}
              style={{
                padding: '8px',
                backgroundColor: 'transparent',
                border: 'none',
                cursor: (isLoading || isUploading) ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                opacity: (isLoading || isUploading) ? 0.5 : 1,
              }}
              title={isUploading ? "Đang upload..." : "Đính kèm file .txt"}
            >
              <AttachIcon style={{ width: '20px', height: '20px', color: '#6b7280' }} />
            </button>
          </div>
          <div style={chatInputRightStyle}>
            {isLoading ? (
              <button onClick={handleStopGeneration} style={stopButtonStyle}>
                <StopGenIcon style={stopIconStyle} />
              </button>
            ) : (
              <button
                onClick={handleSendMessage}
                disabled={!inputText.trim() && !uploadedFile}
                style={sendButtonStyle(!inputText.trim() && !uploadedFile)}
              >
                <SendIcon style={sendIconStyle} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default memo(InputBar);