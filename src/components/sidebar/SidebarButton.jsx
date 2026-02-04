import Title from "./Title";
import SidebarIcon from "../../icons/SidebarIcon";

export default function SidebarButton({
  isSidebarCollapsed,
  setIsSidebarCollapsed,
  isSidebarLockedOpen,
  setIsSidebarLockedOpen,
}) {
  const handleSidebarClick = () => {
    const newLockedState = !isSidebarLockedOpen;
    setIsSidebarLockedOpen(newLockedState);

    if (newLockedState) {
      setIsSidebarCollapsed(false);
    } else {
      setIsSidebarCollapsed(true);
    }
  };
  return (
    <div className="flex items-center mb-6">
      <button
        type="button"
        className="p-2 rounded-full hover:bg-gray-100 focus:outline-none"
        onClick={handleSidebarClick}
        title="Toggle Sidebar"
      >
        <SidebarIcon
          className={`transform transition-transform duration-300 ${
            isSidebarCollapsed ? "rotate-0" : "rotate-180"
          }`}
        />
      </button>

      <Title isSidebarCollapsed={isSidebarCollapsed} />
    </div>
  );
}
