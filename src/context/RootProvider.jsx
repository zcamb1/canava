import { UserProvider } from "./UserContext";
import { MessageProvider } from "./MessageContext";
import { ConversationProvider } from "./ConversationContext";

export default function RootProvider({ children }) {
  return (
    <UserProvider>
      <ConversationProvider>
        <MessageProvider>{children}</MessageProvider>
      </ConversationProvider>
    </UserProvider>
  );
}
