import { useUser } from "../context/UserContext";
import { useMessage } from "../context/MessageContext";
import { useConversation } from "../context/ConversationContext";

export default function UserNewChat() {
  const { userId } = useUser();
  const { messages, setEmptyMessageFunc } = useMessage();
  const {
    conversations,
    currentConversationId,
    currentConversationTitle,
    initNewConversationFunc,
    saveConversationFunc,
  } = useConversation();

  const handleNewChat = async () => {
    // If there's an active conversation with messages, save it before starting a new one
    // Only save if it's NOT the conversation being actively deleted.
    // The `handleDeleteConversation` will handle clearing state if it's the current one.
    if (currentConversationId && messages.length > 0) {
      const idToSave = currentConversationId;
      const titleToSave = currentConversationTitle;
      const currentConv = conversations.find((conv) => conv.id === idToSave);
      const isCurrentPinned = currentConv ? currentConv.isPinned : false;

      console.log(
        "DEBUG (App.jsx): Saving current chat before new chat. ID:",
        idToSave,
        "Title:",
        titleToSave,
        "Messages count:",
        messages.length
      );
      await saveConversationFunc(
        idToSave,
        userId,
        titleToSave,
        messages,
        isCurrentPinned,
        false
      );
    }
    initNewConversationFunc();
    setEmptyMessageFunc();
  };

  return { handleNewChat };
}
