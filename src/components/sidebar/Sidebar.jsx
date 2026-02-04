import { useState, useEffect } from "react";
import SidebarButton from "./SidebarButton";
import NewChatButton from "./NewChat";
import ConversationList from "./ConversationList";

export default function Sidebar({ chatDisplayRef }) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(true);
  const [isSidebarLockedOpen, setIsSidebarLockedOpen] = useState(false);

  const handleSidebarMouseEnter = () => {
    if (!isSidebarLockedOpen) {
      setIsSidebarCollapsed(false);
    }
  };

  const handleSidebarMouseLeave = () => {
    if (!isSidebarLockedOpen) {
      setIsSidebarCollapsed(true);
    }
  };

  return (
    <div
      className={`flex flex-col ${
        isSidebarCollapsed ? "w-16" : "w-64"
      } bg-gray-50 border-r border-gray-200 p-4 shadow-sm transition-all duration-300 ease-in-out`}
      onMouseEnter={handleSidebarMouseEnter}
      onMouseLeave={handleSidebarMouseLeave}
    >
      {/* Sidebar button */}
      <SidebarButton
        isSidebarCollapsed={isSidebarCollapsed}
        setIsSidebarCollapsed={setIsSidebarCollapsed}
        isSidebarLockedOpen={isSidebarLockedOpen}
        setIsSidebarLockedOpen={setIsSidebarLockedOpen}
      />

      {/* New chat button*/}
      <NewChatButton isSidebarCollapsed={isSidebarCollapsed} />

      <ConversationList
        isSidebarCollapsed={isSidebarCollapsed}
        chatDisplayRef={chatDisplayRef}
      />
      {/* Settings button */}
      {/* <button
          type="button"
          className={`flex items-center rounded-full bg-transparent hover:bg-gray-100 text-gray-700 font-medium mt-auto focus:outline-none transition-all duration-300 my-1 ${isSidebarCollapsed ? 'w-10 h-10 p-2' : 'w-full pl-2 pr-4 py-2'}`}
          title="Open Settings"
          >
          <svg
            className="w-6 h-6 text-gray-700"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.564.342 1.25.21 1.724-1.065z"
            ></path>
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            ></path>
          </svg>
          <span className={`whitespace-nowrap text-sm transition-all duration-300 ${isSidebarCollapsed ? 'opacity-0 w-0 ml-0' : 'opacity-100 w-auto ml-2'}`}>
            Settings
          </span>
        </button> */}
    </div>
  );
}
