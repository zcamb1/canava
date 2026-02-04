import NewChatIcon from "../../icons/NewChatIcon";
import useNewChat from "../../hooks/useNewChat";

export default function NewChatButton({ isSidebarCollapsed }) {
  const { handleNewChat } = useNewChat();

  return (
    <button
      type="button"
      className={`flex items-center rounded-[12px] text-blue-700 font-medium mb-6 focus:outline-none
            transition-all duration-300 my-2 hover:bg-blue-100
            ${isSidebarCollapsed ? "w-10 h-10 p-1" : "w-full pl-2 pr-4 py-2"}
          `}
      onClick={handleNewChat}
      title="Start a new conversation"
    >
      <div className="border border-white rounded-full bg-blue-700 p-0.5">
        <NewChatIcon className="flex-shrink-0 w-6 h-6 text-white" />
      </div>
      <span
        className={`pl-2 whitespace-nowrap text-sm font-semibold text-blue-600 transition-all duration-300 ${
          isSidebarCollapsed ? "opacity-0 w-0 ml-0" : "opacity-100 w-auto ml-2"
        }`}
      >
        New chat
      </span>
    </button>
  );
}
