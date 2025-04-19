// context/GcalEventsContext.tsx
import { createContext, useContext } from "react";

type GcalEventsContextType = {
  gcalEvents: any[];
  setGcalEvents: React.Dispatch<React.SetStateAction<any[]>>;
};

export const GcalEventsContext = createContext<GcalEventsContextType | null>(null);

export const useGcalEvents = () => {
  const context = useContext(GcalEventsContext);
  if (!context) {
    throw new Error("useGcalEvents must be used within GcalEventsProvider");
  }
  return context;
};
