import { useUser } from "../../context/UserContext";
import { useMessage } from "../../context/MessageContext";
import { useConversation } from "../../context/ConversationContext";
import { MoreVertical, Pin, Edit, Trash2 } from "lucide-react";
import { scrollToBottomImmediatelyFunc } from "../../hooks/scrolling";
import useNewChat from "../../hooks/useNewChat";
import { useEffect } from "react";

export default function ConversationList({
  isSidebarCollapsed,
  chatDisplayRef,
}) {
  const {
    messages,
    isLoading,
    forceScrollToBottomRef,
    scrollTimeoutRef,
    setMessageFunc,
  } = useMessage();
  const { userId } = useUser();
  const {
    contextMenuRef,
    conversations,
    activeContextMenu,
    currentConversationTitle,
    currentConversationId,
    pinnedConversations,
    recentConversations,
    isConversationsLoading,
    isRenameConvOpen,
    renameConversationId,
    renameCurrentTitle,
    renameNewTitle,
    saveConversationFunc,
    setActiveContextMenuFunc,
    setCurrentConversationIdFunc,
    setCurrentConversationTitleFunc,
    fetchConversationFunc,
    handlePinConversationFunc,
    fetchConversationsFunc,
    setIsConversationsLoadingFunc,
    handleDeleteConversationFunc,
    handleRenameConversationFunc,
    setRenameNewTitleFunc,
    setIsRenameConvOpenFunc,
    submitRenameFunc
  } = useConversation();
  const { handleNewChat } = useNewChat();
  const { scrollToBottomImmediately } = scrollToBottomImmediatelyFunc(
    chatDisplayRef,
    messages,
    isLoading,
    forceScrollToBottomRef,
    scrollTimeoutRef
  );

  useEffect(() => {
    if (userId) {
      fetchConversations(userId);
    }
  }, [userId]);

  useEffect(() => {
    if (currentConversationId && messages.length > 0) {
      const handler = setTimeout(() => {
        const currentConv = conversations.find(
          (conv) => conv.id === currentConversationId
        );
        const isCurrentPinned = currentConv ? currentConv.isPinned : false;
        const titleToSave = currentConversationTitle;
        console.log(
          "DEBUG (App.jsx): Auto-saving conversation with title:",
          titleToSave,
          "and messages count:",
          messages.length,
          "for ID:",
          currentConversationId
        );
        saveConversationFunc(
          currentConversationId,
          userId,
          currentConversationTitle,
          messages,
          isCurrentPinned,
          false
        );
      }, 500);

      return () => {
        clearTimeout(handler);
      };
    }
  }, [currentConversationId, currentConversationTitle]);

  const fetchConversations = async () => {
    setIsConversationsLoadingFunc(true);
    const data = await fetchConversationsFunc(userId);
    if (!currentConversationId && data.length > 0) {
      loadConversation(data[0].id);
    } else if (!currentConversationId && data.length === 0) {
      handleNewChat();
    }
    setIsConversationsLoadingFunc(false);
  };

  const loadConversation = async (id) => {
    // Before loading a new conversation, save the current one if it exists and has messages
    if (
      currentConversationId &&
      messages.length > 0 &&
      currentConversationId !== id
    ) {
      console.log(
        "DEBUG (App.jsx): Saving current chat before loading new one. ID:",
        currentConversationId,
        "Title:",
        currentConversationTitle,
        "Messages count:",
        messages.length
      );
      const currentConv = conversations.find(
        (conv) => conv.id === currentConversationId
      );
      const isCurrentPinned = currentConv ? currentConv.isPinned : false;
      await saveConversationFunc(
        currentConversationId,
        userId,
        currentConversationTitle,
        messages,
        isCurrentPinned,
        false
      );
    }
    setActiveContextMenuFunc(null); // Close any open context menus

    const existingConvInState = conversations.find((conv) => conv.id === id);

    if (
      existingConvInState &&
      existingConvInState.messages &&
      existingConvInState.messages.length > 0
    ) {
      // If found in state and has messages, use it directly
      console.log(
        "DEBUG (App.jsx): Loading conversation from local state:",
        id,
        "with title:",
        existingConvInState.title,
        "and messages count:",
        existingConvInState.messages.length
      );
      setMessageFunc(existingConvInState.messages);
      setCurrentConversationIdFunc(existingConvInState.id);
      setCurrentConversationTitleFunc(existingConvInState.title);
      scrollToBottomImmediately();
      return;
    }

    console.log("DEBUG (App.jsx): Fetching conversation from backend:", id);
    const { loadedMessages, loadedId, loadedTitle } =
      await fetchConversationFunc(id, userId);
    setMessageFunc(loadedMessages);
    setCurrentConversationIdFunc(loadedId);

    setCurrentConversationTitleFunc(loadedTitle);
  };

  const handleDeleteConversation = (id) => {
    if (currentConversationId === id) {
      handleNewChat();
    }
    handleDeleteConversationFunc(userId, id);
  };

  return (
    <div
      className={`flex flex-col h-screen mt-2 transition-all duration-300 ${
        isSidebarCollapsed
          ? "max-h-0 opacity-0 overflow-hidden"
          : "max-h-full opacity-100"
      }`}
    >
      {pinnedConversations.length > 0 && (
        <>
          <ul className="overflow-y-auto max-h-[25vh] scrollbar-thin scrollbar-hide space-y-1 mb-8 pt-12">
            <li>
              <h3
                className={`text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 transition-all duration-300 ${
                  isSidebarCollapsed
                    ? "opacity-0 max-h-0"
                    : "opacity-100 max-h-full"
                }`}
              >
                Pinned
              </h3>
            </li>
            {pinnedConversations.map((conv) => (
              <li
                key={conv.id}
                className="flex items-center justify-between group relative"
              >
                <button
                  type="button"
                  className={`flex-grow text-left py-2 px-3 rounded-lg text-sm truncate
                  ${
                    currentConversationId === conv.id
                      ? "bg-blue-100 text-blue-800 font-semibold"
                      : "hover:bg-gray-100 text-gray-700"
                  }
                  focus:outline-none`}
                  onClick={() => loadConversation(conv.id)}
                  title={`Load conversation: ${conv.title}`}
                >
                  <Pin className="w-3 h-3 inline-block mr-1 text-gray-500" />
                  {conv.title}
                </button>
                <button
                  type="button"
                  className="ml-2 p-1 rounded-full hover:bg-gray-200 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity focus:outline-none"
                  onClick={(e) => {
                    e.stopPropagation(); // Prevent loading conversation
                    setActiveContextMenuFunc(
                      activeContextMenu === conv.id ? null : conv.id
                    );
                  }}
                  title="Conversation Options"
                >
                  <MoreVertical className="w-4 h-4" />
                </button>

                {activeContextMenu === conv.id && (
                  <div
                    ref={contextMenuRef}
                    className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-20 border border-gray-200"
                  >
                    <button
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() =>
                        handlePinConversationFunc(
                          userId,
                          conv.id,
                          conv.isPinned
                        )
                      }
                    >
                      <Pin className="w-4 h-4 mr-2" />{" "}
                      {conv.isPinned ? "Unpin" : "Pin"}
                    </button>
                    <button
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() =>
                        handleRenameConversationFunc(conv.id, conv.title)
                      }
                    >
                      <Edit className="w-4 h-4 mr-2" /> Rename
                    </button>
                    <button
                      className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                      onClick={() => handleDeleteConversation(conv.id)}
                    >
                      <Trash2 className="w-4 h-4 mr-2" /> Delete
                    </button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </>
      )}

      {/* Recent Conversations List */}
      {isConversationsLoading ? (
        <div className="text-gray-500 text-sm">Loading conversations...</div>
      ) : recentConversations.length === 0 ? (
        <div className="text-gray-500 text-sm">No recent chats.</div>
      ) : (
        <ul className="flex-1 overflow-y-auto max-h-[35vh] scrollbar-thin scrollbar-hide space-y-1 relative pt-12">
          <li>
            <h3
              className={`text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 transition-all duration-300 ${
                isSidebarCollapsed
                  ? "opacity-0 max-h-0"
                  : "opacity-100 max-h-full"
              }`}
            >
              Recent
            </h3>
          </li>
          {recentConversations.map((conv) => (
            <li
              key={conv.id}
              className="flex items-center justify-between group relative"
            >
              <button
                type="button"
                className={`flex-grow text-left py-2 px-3 rounded-lg text-sm truncate
                ${
                  currentConversationId === conv.id
                    ? "bg-blue-100 text-blue-800 font-semibold"
                    : "hover:bg-gray-100 text-gray-700"
                }
                focus:outline-none`}
                onClick={() => loadConversation(conv.id)}
                title={`Load conversation: ${conv.title}`}
              >
                {conv.title}
              </button>
              <button
                type="button"
                className="ml-2 p-1 rounded-full hover:bg-gray-200 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity focus:outline-none"
                onClick={(e) => {
                  e.stopPropagation(); // Prevent loading conversation
                  setActiveContextMenuFunc(
                    activeContextMenu === conv.id ? null : conv.id
                  );
                }}
                title="Conversation Options"
              >
                <MoreVertical className="w-4 h-4" />
              </button>

              {activeContextMenu === conv.id && (
                <div
                  ref={contextMenuRef}
                  className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-30 border border-gray-200"
                >
                  <button
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() =>
                      handlePinConversationFunc(userId, conv.id, conv.isPinned)
                    }
                  >
                    <Pin className="w-4 h-4 mr-2" />{" "}
                    {conv.isPinned ? "Unpin" : "Pin"}
                  </button>
                  <button
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() =>
                      handleRenameConversationFunc(conv.id, conv.title)
                    }
                  >
                    <Edit className="w-4 h-4 mr-2" /> Rename
                  </button>
                  <button
                    className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                    onClick={() => handleDeleteConversation(conv.id)}
                  >
                    <Trash2 className="w-4 h-4 mr-2" /> Delete
                  </button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}

      {isRenameConvOpen && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl w-96">
            <h2 className="text-lg font-semibold mb-4">Rename Conversation</h2>
            <p className="text-sm text-gray-600 mb-2">
              Current Title:{" "}
              <span className="font-medium">{renameCurrentTitle}</span>
            </p>
            <input
              type="text"
              className="w-full p-2 border border-gray-300 rounded-md mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={renameNewTitle}
              onChange={(e) => setRenameNewTitleFunc(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  submitRenameFunc(userId, renameConversationId, renameNewTitle);
                }
              }}
              placeholder="Enter new title"
            />
            <div className="flex justify-end space-x-3">
              <button
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 focus:outline-none"
                onClick={() => setIsRenameConvOpenFunc(false)}
              >
                Cancel
              </button>
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={() => submitRenameFunc(userId, renameConversationId, renameNewTitle)}
                disabled={
                  renameNewTitle.trim() === "" ||
                  renameNewTitle.trim() === renameCurrentTitle
                }
              >
                Rename
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
