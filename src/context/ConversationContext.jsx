import { useState, useRef, createContext, useContext, useEffect } from "react";
import {
  saveConversation,
  fetchConversation,
  handlePinConversation,
  fetchConversations,
  handleDeleteConversation,
  submitRename,
} from "../services/conversationAPI";
import { v4 as uuidv4 } from "uuid";

const ConversationContext = createContext();

export function ConversationProvider({ children }) {
  const contextMenuRef = useRef(null);
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [currentConversationTitle, setCurrentConversationTitle] =
    useState("New Chat");
  const [isConversationsLoading, setIsConversationsLoading] = useState(true);
  const [activeContextMenu, setActiveContextMenu] = useState(null);
  const greetings = [
    "Hi there!",
    "Hello again!",
    "Welcome back!",
    "How can I help?",
    "What's on your mind?",
    "Back at it.",
  ];
  const [isRenameConvOpen, setIsRenameConvOpen] = useState(false);
  const [renameConversationId, setRenameConversationId] = useState(null);
  const [renameCurrentTitle, setRenameCurrentTitle] = useState("");
  const [renameNewTitle, setRenameNewTitle] = useState("");
  const [currentGreeting, setCurrentGreeting] = useState("");
  const pinnedConversations = conversations.filter((conv) => conv.isPinned);
  const recentConversations = conversations.filter((conv) => !conv.isPinned);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        contextMenuRef.current &&
        !contextMenuRef.current.contains(event.target)
      ) {
        setActiveContextMenu(null);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const setCurrentConversationIdFunc = (newConversationId) => {
    setCurrentConversationId(newConversationId);
  };

  const setCurrentConversationTitleFunc = (newConversationTitle) => {
    setCurrentConversationTitle(newConversationTitle);
  };

  const setIsConversationsLoadingFunc = (value) => {
    setIsConversationsLoading(value);
  };

  const sortConversationsFunc = (convs) => {
    return [...convs].sort((a, b) => {
      if (a.isPinned && !b.isPinned) return -1;
      if (!a.isPinned && b.isPinned) return 1;
      return new Date(b.lastUpdated) - new Date(a.lastUpdated);
    });
  };

  const saveConversationFunc = async (
    id,
    user_id,
    title,
    msgs,
    isPinned = false,
    shouldReSort = false
  ) => {
    const conversationData = saveConversation(
      id,
      user_id,
      title,
      msgs,
      isPinned
    );

    setConversations((prevConversations) => {
      const existingIndex = prevConversations.findIndex(
        (conv) => conv.id === id
      );
      let updatedConvs;
      if (existingIndex > -1) {
        // Update existing conversation
        updatedConvs = prevConversations.map((conv, index) =>
          index === existingIndex
            ? {
                ...conv,
                title: title,
                lastUpdated: conversationData.lastUpdated,
                isPinned: isPinned,
              }
            : conv
        );
      } else {
        // Add new conversation
        updatedConvs = [
          {
            id,
            title,
            lastUpdated: conversationData.lastUpdated,
            isPinned,
            messages: [],
          },
          ...prevConversations,
        ];
      }

      if (shouldReSort) {
        return sortConversationsFunc(updatedConvs);
      }
      return updatedConvs;
    });
  };

  const initNewConversationFunc = () => {
    const randomIndex = Math.floor(Math.random() * greetings.length);
    setCurrentGreeting(greetings[randomIndex]);
    setCurrentConversationId(uuidv4()); // Changed from crypto.randomUUID()
    setCurrentConversationTitle("New Chat"); // Reset title for the new chat
    setActiveContextMenu(null);
  };

  const setActiveContextMenuFunc = (value) => {
    setActiveContextMenu(value);
  };

  const fetchConversationFunc = (id, user_id) => {
    return fetchConversation(id, user_id);
  };

  const handlePinConversationFunc = async (
    user_id,
    convId,
    currentPinnedStatus
  ) => {
    setActiveContextMenu(null);
    await handlePinConversation(user_id, convId, currentPinnedStatus);
    setConversations((prevConversations) => {
      const updated = prevConversations.map((conv) =>
        conv.id === convId ? { ...conv, isPinned: !currentPinnedStatus } : conv
      );
      return sortConversationsFunc(updated);
    });
  };

  const handleDeleteConversationFunc = async (user_id, id) => {
    setActiveContextMenu(null);
    const sortedData = await handleDeleteConversation(user_id, id);
    setConversations(sortedData);
  };

  const handleRenameConversationFunc = (convId, currentTitle) => {
    setActiveContextMenu(null);
    setRenameConversationId(convId);
    setRenameCurrentTitle(currentTitle);
    setRenameNewTitle(currentTitle);
    setIsRenameConvOpen(true);
  };

  const setRenameNewTitleFunc = (value) => {
    setRenameNewTitle(value);
  };

  const setIsRenameConvOpenFunc = (value) => {
    setIsRenameConvOpen(value);
  };

  const submitRenameFunc = async (user_id, convId, newTitle) => {
    if (!renameConversationId || renameNewTitle.trim() === "") return;
    await submitRename(user_id, convId, newTitle);
    if (currentConversationId === renameConversationId) {
      setCurrentConversationTitle(renameNewTitle.trim());
    }

    setConversations((prevConversations) => {
      const updatedConvs = prevConversations.map((conv) =>
        conv.id === renameConversationId
          ? { ...conv, title: renameNewTitle.trim() }
          : conv
      );
      return updatedConvs;
    });
    setIsRenameConvOpen(false);
    setRenameConversationId(null);
    setRenameCurrentTitle("");
    setRenameNewTitle("");
  };

  const fetchConversationsFunc = async (user_id) => {
    const data = await fetchConversations(user_id);
    setConversations(sortConversationsFunc(data));
    return data;
  };

  return (
    <ConversationContext.Provider
      value={{
        contextMenuRef,
        conversations,
        currentConversationId,
        currentConversationTitle,
        isConversationsLoading,
        currentGreeting,
        pinnedConversations,
        recentConversations,
        activeContextMenu,
        isRenameConvOpen,
        renameConversationId,
        renameCurrentTitle,
        renameNewTitle,
        setCurrentConversationIdFunc,
        setCurrentConversationTitleFunc,
        saveConversationFunc,
        initNewConversationFunc,
        setActiveContextMenuFunc,
        fetchConversationFunc,
        handlePinConversationFunc,
        setIsConversationsLoadingFunc,
        fetchConversationsFunc,
        handleDeleteConversationFunc,
        handleRenameConversationFunc,
        setRenameNewTitleFunc,
        setIsRenameConvOpenFunc,
        submitRenameFunc,
      }}
    >
      {children}
    </ConversationContext.Provider>
  );
}

export function useConversation() {
  return useContext(ConversationContext);
}
