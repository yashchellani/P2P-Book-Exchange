import React, { createContext, useState } from 'react';

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [user_id, setUser_id] = useState(null);

  return (
    <AppContext.Provider value={{ user_id, setUser_id }}>
      {children}
    </AppContext.Provider>
  );
};
