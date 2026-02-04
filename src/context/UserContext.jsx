import { useState, useEffect, createContext, useContext } from "react";
import { checkInAndFetchCount } from "../services/userAPI";
import { v4 as uuidv4 } from "uuid";

const UserContext = createContext();

export function UserProvider({ children }) {
  const [userId, setUserId] = useState(() => {
    const storedUserId = localStorage.getItem("chatbotUserId");
    if (storedUserId) {
      return storedUserId;
    }
    const newId = uuidv4(); // Changed from crypto.randomUUID()
    localStorage.setItem("chatbotUserId", newId);
    return newId;
  });

  useEffect(() => {
    if (userId) {
      localStorage.setItem("chatbotUserId", userId);
    }
  }, [userId]);

  const [userCount, setUserCount] = useState(0);

  useEffect(() => {
    setUserCount(checkInAndFetchCount());
    const intervalId = setInterval(checkInAndFetchCount, 5000);
    return () => clearInterval(intervalId);
  }, []);

  return (
    <UserContext.Provider value={{ userId, userCount }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}
