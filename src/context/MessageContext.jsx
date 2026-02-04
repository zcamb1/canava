import { useState, useRef, createContext, useContext } from "react";
import { v4 as uuidv4 } from "uuid";
import { callFastAPIRagAPI, generateTitle } from "../services/messageAPI";

const MessageContext = createContext();

export function MessageProvider({ children }) {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const textareaRef = useRef(null);
  const [abortController, setAbortController] = useState(null);
  const scrollTimeoutRef = useRef(null);
  const forceScrollToBottomRef = useRef(false);

  const handleStopGenerationFunc = () => {
    setIsLoading(false);
    setMessages((prevMessages) => {
      const updatedMessages = prevMessages.slice(0, prevMessages.length - 2);
      return updatedMessages;
    });
    if (abortController) {
      abortController.abort();
    }
  };

  const handleIconStreamingFunc = () => {
    setMessages((prevMessages) => {
      const updated = [...prevMessages];
      updated[updated.length - 1] = {
        ...updated[updated.length - 1],
        isStreaming: false,
      };
      // console.log("Icon", updated);
      return updated;
    });
  };

  const updateUserMessageFunc = (inputText) => {
    const userMessage = {
      id: uuidv4(),
      sender: "user",
      text: inputText.trim(),
      feedback: "",
      thinkingContent: "",
      isCopied: false,
      isLiked: false,
      isDisliked: false,
    };
    setMessages([...messages, userMessage]);
  };

  const callFastAPIRagAPIFunc = async (userid, conid, prompt) => {
    setIsLoading(true);
    const controller = new AbortController();
    const signal = controller.signal;
    setAbortController(controller);
    const newBotMessageId = uuidv4();
    setMessages((prevMessages) => [
      ...prevMessages,
      {
        id: newBotMessageId,
        sender: "bot",
        text: "",
        isStreaming: true,
        feedback: "",
        showFeedbackForm: false,
        thinkingContent: "",
        isCopied: false,
        isLiked: false,
        isDisliked: false,
      },
    ]);

    let fullRawStreamedContent = "";
    await callFastAPIRagAPI(userid, conid, prompt, signal, (chunk) => {
      fullRawStreamedContent += chunk;
      // console.log(chunk);
      const thinkRegex = /<think>(.*?)<\/think>/s;

      let extractedThinking = "";
      let mainAnswer = "";
      let shouldBeOpen = true;

      const match = fullRawStreamedContent.match(thinkRegex);
      if (match) {
        extractedThinking = match[1].trim();
        mainAnswer = fullRawStreamedContent.replace(thinkRegex, "").trim();
        shouldBeOpen = false; // Close tab once </think> is found
      } else {
        // If <think> tag is present but not closed, content goes to thinking
        if (fullRawStreamedContent.includes("<think>")) {
          extractedThinking = fullRawStreamedContent
            .replace("<think>", "")
            .trim();
          mainAnswer = ""; // Main answer is empty until </think> is found
          shouldBeOpen = true; // Keep tab open
        } else {
          // No <think> tag found yet, or it was never present, all content goes to main answer
          mainAnswer = fullRawStreamedContent.trim();
          extractedThinking = "";
          shouldBeOpen = false; // Tab should be closed if no thinking or thinking is done
        }
      }

      // Update the specific bot message in the messages array using its ID
      setMessages((prevMessages) => {
        // const newMessages = [...prevMessages];
        // const targetMessageIndex = newMessages.findIndex(
        //   (msg) => msg.id === newBotMessageId
        // );

        // if (
        //   targetMessageIndex !== -1 &&
        //   newMessages[targetMessageIndex]?.sender === "bot"
        // ) {
        //   newMessages[targetMessageIndex].text = mainAnswer;
        //   newMessages[targetMessageIndex].thinkingContent = extractedThinking;
        //   newMessages[targetMessageIndex].isThinkingOpen = shouldBeOpen;
        // }
        // return newMessages;
        
        const lastMessage = prevMessages[prevMessages.length - 1];
        const updatedMessage = {
          ...lastMessage,
          text: mainAnswer,
          thinkingContent: extractedThinking,
          isThinkingOpen: shouldBeOpen,
        };
        return [...prevMessages.slice(0, -1), updatedMessage];
      });
    });
    const newTitle = await generateTitle();
    setIsLoading(false);
    setAbortController(null);
    handleIconStreamingFunc();
    return newTitle;
  };

  const toggleThinkingTabFunc = (messageId) => {
    setMessages((prevMessages) => {
      const newMessages = prevMessages.map((msg) => {
        if (msg.id === messageId && msg.sender === "bot") {
          const newState = !msg.isThinkingOpen;
          return { ...msg, isThinkingOpen: newState };
        }
        return msg;
      });
      return newMessages;
    });
  };

  const handleThumbsUpFunc = (messageId) => {
    setMessages((prevMessages) =>
      prevMessages.map((msg) => {
        if (msg.id === messageId) {
          return { ...msg, isLiked: !msg.isLiked, isDisliked: false };
        }
        return msg;
      })
    );
    // console.log(`DEBUG: Thumbs Up clicked for message ID: ${messageId}`);
  };

  const handleThumbsDownFunc = (messageId) => {
    setMessages((prevMessages) =>
      prevMessages.map((msg) => {
        if (msg.id === messageId) {
          return { ...msg, isDisliked: !msg.isDisliked, isLiked: false };
        }
        return msg;
      })
    );
    // console.log(`DEBUG: Thumbs Down clicked for message ID: ${messageId}`);
  };

  const handleCopyResponseFunc = (messageId, textToCopy) => {
    const textArea = document.createElement("textarea");
    textArea.value = textToCopy;
    textArea.style.position = "fixed"; // Avoid scrolling to bottom
    textArea.style.left = "-9999px"; // Move off-screen
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      const successful = document.execCommand("copy");
      if (successful) {
        console.log("Copied to clipboard!");
        // Update message state to show copied feedback
        setMessages((prevMessages) =>
          prevMessages.map((msg) =>
            msg.id === messageId ? { ...msg, isCopied: true } : msg
          )
        );
        // Revert icon after 2 seconds
        setTimeout(() => {
          setMessages((prevMessages) =>
            prevMessages.map((msg) =>
              msg.id === messageId ? { ...msg, isCopied: false } : msg
            )
          );
        }, 2000);
      } else {
        console.error("Failed to copy.");
      }
    } catch (err) {
      console.error("Oops, unable to copy", err);
    }
    document.body.removeChild(textArea);
  };

  const handleResetResponseFunc = async (userid, conid, messageId) => {
    // console.log(`DEBUG: Resetting response for message ID: ${messageId}`);
    setIsLoading(true);

    // Find the original user message that triggered this bot response
    const messageIndex = messages.findIndex((msg) => msg.id === messageId);
    if (messageIndex === -1 || messages[messageIndex].sender !== "bot") {
      console.error(
        "Could not find bot message to reset or it's not a bot message."
      );
      setIsLoading(false);
      return;
    }

    const previousUserMessage = messages[messageIndex - 1]; // Assuming user message is directly before bot's
    if (!previousUserMessage || previousUserMessage.sender !== "user") {
      console.error("Could not find the preceding user message for reset.");
      setIsLoading(false);
      return;
    }

    // Remove the current bot message (and any subsequent messages if they exist, though they shouldn't in a linear chat)
    setMessages((prevMessages) => {
      const newMessages = prevMessages.slice(0, messageIndex); // Keep messages up to the user's last message
      return newMessages;
    });
    await callFastAPIRagAPIFunc(userid, conid, previousUserMessage.text);
  };

  const handleToggleFeedbackFormFunc = (messageId) => {
    setMessages((prevMessages) =>
      prevMessages.map((msg) =>
        msg.id === messageId
          ? { ...msg, showFeedbackForm: !msg.showFeedbackForm }
          : { ...msg, showFeedbackForm: false }
      )
    );
  };

  const handleOnChangeFeedbackFunc = (e, messageId) => {
    setMessages((prevMessages) =>
      prevMessages.map((msg) =>
        msg.id === messageId ? { ...msg, feedback: e.target.value } : msg
      )
    );
  };

  const updateFeedbackFunc = async (messageId, feedbackText) => {
    const updatedFeedback = messages.map((msg) =>
      msg.id === messageId ? { ...msg, feedback: feedbackText } : msg
    );

    setMessages(updatedFeedback);

    return updatedFeedback;
  };

  const setEmptyMessageFunc = () => {
    setMessages([]);
  };

  const setMessageFunc = (mess) => {
    setMessages(
      mess.map((msg) => ({
        id: msg.id || uuidv4(),
        sender: msg.sender,
        text: msg.text,
        isStreaming: msg.isStreaming,
        feedback: msg.feedback,
        showFeedbackForm: msg.showFeedbackForm || false,
        thinkingContent: msg.thinkingContent || "",
        isCopied: msg.isCopied || false,
        isLiked: msg.isLiked || false,
        isDisliked: msg.isDisliked || false,
      }))
    );
  };

  return (
    <MessageContext.Provider
      value={{
        messages,
        textareaRef,
        isLoading,
        forceScrollToBottomRef,
        scrollTimeoutRef,
        handleStopGenerationFunc,
        updateUserMessageFunc,
        callFastAPIRagAPIFunc,
        toggleThinkingTabFunc,
        handleThumbsUpFunc,
        handleThumbsDownFunc,
        handleCopyResponseFunc,
        handleResetResponseFunc,
        handleToggleFeedbackFormFunc,
        handleOnChangeFeedbackFunc,
        updateFeedbackFunc,
        setEmptyMessageFunc,
        setMessageFunc,
      }}
    >
      {children}
    </MessageContext.Provider>
  );
}

export function useMessage() {
  return useContext(MessageContext);
}
