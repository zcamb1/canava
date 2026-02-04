import {useEffect, memo } from "react";
import InputBar from "./InputBar";
import ChatDisplay from "./ChatDisplay";
import { useUser } from "../../context/UserContext";
import { useMessage } from "../../context/MessageContext";

function MainContent({ chatDisplayRef }) {
  const { userId, userCount } = useUser();
  const { messages } = useMessage();

  useEffect(() => {
    if (!chatDisplayRef.current) return;
    chatDisplayRef.current.scrollTop = chatDisplayRef.current.scrollHeight;
  }, [messages.length]);

  return (
    <div className="flex flex-col flex-grow relative bg-white">
      <ChatDisplay chatDisplayRef={chatDisplayRef} />
      <InputBar chatDisplayRef={chatDisplayRef} />
      {userId && (
        <div className="bottom-2 left-4 text-xs text-gray-400 flex justify-between">
          <div className="ml-4 mb-2">User ID: {userId}</div>
          <div className="mr-4 mb-2">Active users: {userCount}</div>
        </div>
      )}
    </div>
  );
}

export default memo(MainContent);