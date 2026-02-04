import { useEffect, useCallback } from "react";

export function scrollToBottomImmediatelyFunc(
  chatDisplayRef,
  messages,
  isLoading,
  forceScrollToBottomRef,
  scrollTimeoutRef
) {
  const smoothScrollToBottom = useCallback(
    (force = false) => {
      if (!chatDisplayRef.current) return;

      const chatDisplay = chatDisplayRef.current;
      const isNearBottom =
        chatDisplay.scrollHeight -
          chatDisplay.scrollTop -
          chatDisplay.clientHeight <
        100;

      if (force || isNearBottom) {
        const lastMessage = messages[messages.length - 1];
        const isStreaming = isLoading && lastMessage?.sender === "bot";

        if (force || !isStreaming) {
          // Immediate scroll for new messages, page load, or forced scroll
          requestAnimationFrame(() => {
            if (chatDisplayRef.current) {
              chatDisplayRef.current.scrollTop =
                chatDisplayRef.current.scrollHeight;
            }
          });
        } else {
          // Throttled smooth scroll during streaming
          if (scrollTimeoutRef.current) {
            clearTimeout(scrollTimeoutRef.current);
          }
          scrollTimeoutRef.current = setTimeout(() => {
            if (chatDisplayRef.current) {
              chatDisplayRef.current.scrollTo({
                top: chatDisplayRef.current.scrollHeight,
                behavior: "smooth",
              });
            }
          }, 10);
        }
      }
    },
    [messages, isLoading]
  );

  useEffect(() => {
    if (forceScrollToBottomRef.current) {
      smoothScrollToBottom(true);
      forceScrollToBottomRef.current = false;
    } else {
      smoothScrollToBottom();
    }
  }, [messages, smoothScrollToBottom]);

  const scrollToBottomImmediately = () => {
    forceScrollToBottomRef.current = true;
  };

  return { scrollToBottomImmediately };
}
