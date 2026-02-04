import { memo, useRef, useCallback, useState, useEffect } from "react";
import {} from "react";
import { useUser } from "../../context/UserContext";
import { useMessage } from "../../context/MessageContext";
import { useConversation } from "../../context/ConversationContext";
import { ThinkingProcess, customComponents } from "./ThinkingProcess";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import BotIcon from "../../icons/BotIcon";
import FeedbackIcon from "../../icons/FeedbackIcon";
import RunningLine from "../../icons/RunningLine";
import botIcon from "../../images/botIcon.png";
import "../../styles/animations.css";
import { useVirtualizer } from "@tanstack/react-virtual";
import {
  feedbackContainerStyle,
  topFeedbackLayerStyle,
  feedbackInputFieldStyle,
  bottomFeedbackLayerStyle,
  feedbackInputLeftStyle,
  feedbackInputRightStyle,
  cancelButtonStyle,
  submitButtonStyle,
} from "../../styles/chatDisplay.js";
import {
  ThumbsUp,
  ThumbsDown,
  Clipboard,
  RotateCcw,
  Check,
} from "lucide-react";

const classNames = (...classes) => {
  return classes.filter(Boolean).join(" ");
};

function ChatDisplay({ chatDisplayRef }) {
  const parentRef = useRef();
  const [isAtBottom, setIsAtBottom] = useState(true);
  const {
    messages,
    toggleThinkingTabFunc,
    handleThumbsUpFunc,
    handleThumbsDownFunc,
    handleCopyResponseFunc,
    handleResetResponseFunc,
    handleToggleFeedbackFormFunc,
    handleOnChangeFeedbackFunc,
    updateFeedbackFunc,
  } = useMessage();
  const { userId } = useUser();
  const {
    conversations,
    currentConversationId,
    currentConversationTitle,
    currentGreeting,
    saveConversationFunc,
  } = useConversation();

  const handleResetResponse = async (messageId) => {
    handleResetResponseFunc(userId, currentConversationId, messageId);
  };

  const handleInputHeight = (e) => {
    e.target.style.height = "auto";
    e.target.style.height = `${e.target.scrollHeight}px`;
  };

  const handleSubmitFeedback = async (currentMessId, feedbackText) => {
    if (currentConversationId && messages.length > 0) {
      const currentConv = conversations.find(
        (conv) => conv.id === currentConversationId
      );
      const isCurrentPinned = currentConv ? currentConv.isPinned : false;
      const newFeedback = await updateFeedbackFunc(currentMessId, feedbackText);

      console.log(
        "DEBUG (App.jsx): Saving current chat by taking user feedback:",
        currentConversationId,
        "Feedback",
        feedbackText,
        "Title:",
        currentConversationTitle,
        "Messages count:",
        newFeedback.length,
        "Messages",
        newFeedback,
        "Current ID",
        currentMessId
      );

      await saveConversationFunc(
        currentConversationId,
        userId,
        currentConversationTitle,
        newFeedback,
        isCurrentPinned,
        false
      );
    }
  };

  const rowVirtualizer = useVirtualizer({
    count: messages.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 120,
    overscan: 10,
  });

  const virtualRows = rowVirtualizer.getVirtualItems();

  const scrollToBottomSmooth = () => {
    const el = parentRef.current;
    if (!el) return;
    const target = el.scrollHeight - el.clientHeight;
    el.scrollTo({ top: target, behavior: "smooth" });
  };

  return (
    <div
      ref={chatDisplayRef}
      className={`flex-grow flex flex-col items-center px-4 overflow-y-auto pt-24 scroll-smooth ${
        messages.length === 0 ? "justify-center" : ""
      }`}
    >
      {messages.length === 0 ? (
        <div className="text-4xl font-light text-blue-600">
          {currentGreeting.slice(0, -1)}, _
          {currentGreeting[currentGreeting.length - 1]}
        </div>
      ) : (
        <div
          className="w-full max-w-xl sm:max-w-2xl md:max-w-4xl lg:max-w-5xl xl:max-w-6xl"
          ref={parentRef}
        >
          <div
            style={{
              height: rowVirtualizer.getTotalSize(),
              width: "100%",
              position: "relative",
            }}
          >
            {virtualRows.map((virtualRow) => {
              const message = messages[virtualRow.index];

              return (
                <div
                  key={message.id}
                  data-index={virtualRow.index}
                  ref={(el) => {
                    if (el) rowVirtualizer.measureElement(el);
                  }}
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    width: "100%",
                    transform: `translateY(${virtualRow.start}px)`,
                  }}
                  className={`flex mb-4 items-start group ${
                    message.sender === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  {/* Bot icon and running circle animation */}
                  {message.sender === "bot" && (
                    <div
                      className={classNames(
                        "relative flex-shrink-0 w-12 h-12 rounded-full bg-white flex items-center justify-center text-white text-lg ml-2 overflow-hidden",
                        message.isStreaming && "animate-pulse-bot" // Apply pulse animation to the icon container
                      )}
                    >
                      {/* Running line circle SVG */}
                      {/* {message.isStreaming && (
                    <RunningLine
                      svg_props="absolute inset-0 w-full h-full z-10"
                      circle_props="animate-running-line-circle"
                    />
                  )} */}
                      {/* Original Bot icon SVG */}
                      {/* <BotIcon className="w-8 h-8 z-10" /> */}
                      <img
                        src={botIcon}
                        alt="icon"
                        className="w-10 h-10 object-contain z-0"
                      />
                    </div>
                  )}
                  {/* Message content */}
                  <div className="flex flex-col space-y-2">
                    {/* Thinking Process */}
                    {message.sender === "bot" && (
                      <>
                        {!message.thinkingContent && (
                          <div className="text-sm text-gray-400 italic animate-pulse mt-4 ml-2 mr-2">
                            Deep thinking...
                          </div>
                        )}
                        {message.thinkingContent && (
                          <ThinkingProcess
                            content={message.thinkingContent}
                            isOpen={message.isThinkingOpen}
                            onToggle={() => toggleThinkingTabFunc(message.id)}
                          />
                        )}
                      </>
                    )}
                    {/* Message bubble */}
                    <div
                      className={classNames(
                        message.sender === "user"
                          ? "bg-blue-600 text-white rounded-xl py-2 px-3 prose prose-lg"
                          : "bg-white text-gray-800 rounded-xl ml-4"
                      )}
                    >
                      {message.sender === "bot" ? (
                        <div className="prose prose-lg max-w-none text-gray-800 [&>p]:my-2 [&>ul]:my-2 [&>ol]:my-2 [&>li]:my-1">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={customComponents}
                          >
                            {message.text}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        message.text
                      )}

                      {/* Bot actions */}
                      {message.sender === "bot" &&
                        !message.isStreaming &&
                        message.text.length > 0 && (
                          <div
                            className={classNames(
                              "flex space-x-3 mt-2 text-gray-500 text-sm transition-opacity duration-200",
                              message.isLiked || message.isDisliked
                                ? "opacity-100"
                                : "opacity-100"
                            )}
                          >
                            <button
                              className={classNames(
                                "p-1 rounded-full hover:bg-gray-100",
                                message.isLiked
                                  ? "text-blue-500"
                                  : "text-gray-500"
                              )}
                              title="Like"
                              onClick={() => handleThumbsUpFunc(message.id)}
                            >
                              <ThumbsUp
                                className="w-4 h-4"
                                fill={message.isLiked ? "currentColor" : "none"}
                              />
                            </button>
                            <button
                              className={classNames(
                                "p-1 rounded-full hover:bg-gray-100",
                                message.isDisliked
                                  ? "text-red-500"
                                  : "text-gray-500"
                              )}
                              title="Dislike"
                              onClick={() => handleThumbsDownFunc(message.id)}
                            >
                              <ThumbsDown
                                className="w-4 h-4"
                                fill={
                                  message.isDisliked ? "currentColor" : "none"
                                }
                              />
                            </button>
                            <button
                              className="p-1 rounded-full hover:bg-gray-100"
                              title="Copy"
                              onClick={() =>
                                handleCopyResponseFunc(message.id, message.text)
                              }
                            >
                              {message.isCopied ? (
                                <Check className="w-4 h-4" />
                              ) : (
                                <Clipboard className="w-4 h-4" />
                              )}
                            </button>
                            <button
                              className="p-1 rounded-full hover:bg-gray-100"
                              title="Reset Response"
                              onClick={() => handleResetResponse(message.id)}
                            >
                              <RotateCcw className="w-4 h-4" />
                            </button>
                            {/* Feedback Button */}
                            <button
                              onClick={() =>
                                handleToggleFeedbackFormFunc(message.id)
                              }
                              className="p-1 rounded-full hover:bg-gray-100"
                              title="Give feedback"
                            >
                              <FeedbackIcon className="icon" />
                            </button>
                          </div>
                        )}
                      {message.showFeedbackForm &&
                        message.sender === "bot" &&
                        !message.isStreaming && (
                          <div style={feedbackContainerStyle}>
                            <div style={topFeedbackLayerStyle}>
                              <textarea
                                row="1"
                                placeholder="Tell us what you think..."
                                value={message.feedback || ""}
                                onChange={(e) =>
                                  handleOnChangeFeedbackFunc(e, message.id)
                                }
                                onInput={handleInputHeight}
                                onKeyPress={(e) => {
                                  if (e.key === "Enter" && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSubmitFeedback(
                                      message.id,
                                      message.feedback
                                    );
                                    handleToggleFeedbackFormFunc(message.id);
                                  }
                                }}
                                style={feedbackInputFieldStyle}
                              ></textarea>
                            </div>

                            <div style={bottomFeedbackLayerStyle}>
                              <div style={feedbackInputLeftStyle}></div>
                              <div style={feedbackInputRightStyle}>
                                <button
                                  onClick={() =>
                                    handleToggleFeedbackFormFunc(message.id)
                                  }
                                  style={cancelButtonStyle}
                                >
                                  Cancel
                                </button>
                                <button
                                  onClick={() => {
                                    handleSubmitFeedback(
                                      message.id,
                                      message.feedback
                                    ),
                                      handleToggleFeedbackFormFunc(message.id);
                                  }}
                                  style={submitButtonStyle(!message.feedback)}
                                  disabled={!message.feedback}
                                >
                                  Submit
                                </button>
                              </div>
                            </div>
                          </div>
                        )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export default memo(ChatDisplay);
