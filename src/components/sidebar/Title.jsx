export default function Title({ isSidebarCollapsed }) {
  return (
    <h2
      className={`text-[22px] font-semibold text-gray-500 tracking-wider p-2 transition-all duration-300 ${
        isSidebarCollapsed ? "opacity-0 max-h-0" : "opacity-100 max-h-full"
      }`}
    >
      PolicyBot
    </h2>
  );
}
