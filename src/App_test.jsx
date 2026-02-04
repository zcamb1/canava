import { useRef } from "react";
import Sidebar from "./components/sidebar/Sidebar";
import MainContent from "./components/chat/MainContent";

const App = () => {
  const chatDisplayRef = useRef(null);
  return (
    <div className="flex h-screen bg-white font-inter">
      <Sidebar chatDisplayRef={chatDisplayRef} />
      <MainContent chatDisplayRef={chatDisplayRef} />
    </div>
  );
};

export default App;
