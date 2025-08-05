import { createContext, useContext } from "react";

export type ModalView = "details" | "update" | "pre_upload" | "upload" | null;

type EventStateContextType = {
  selectedEvent: number|null;
  setSelectedEvent: (id: number|null) => void;
  modalView: ModalView;
  setModalView: (view: ModalView) => void;
  modalData: Record<string, any>;
  setModalData: (data: Record<string, any>) => void;
};

export const EventStateContext = createContext<EventStateContextType | null>(null);

export const useEventState = () => {
  const context = useContext(EventStateContext);
  if (!context) {
    throw new Error("useEventState must be used within a EventStateContext.Provider");
  }

  const openDetails = (event_id: number) => {
    context.setSelectedEvent(event_id);
    context.setModalView("details");
  };
  const openUpdate = (event_id: number) => {
    // context.setSelectedEvent(event_id);// no need since always routed from the details modal
    context.setModalView("update");
  };
  const openPreUpload = () => {
    context.setSelectedEvent(null);
    context.setModalView("pre_upload");
  }
  const openUpload = (selectedCategory: any) => {
    // context.setSelectedEvent(null); // no need since always routed from pre-upload
    context.setModalData({"selectedCategory": selectedCategory})
    context.setModalView("upload");
  };
  const closeModal = () => {
    context.setSelectedEvent(null);
    context.setModalView(null);
  };

  return {
    selectedEvent: context.selectedEvent,
    modalView: context.modalView,
    modalData: context.modalData,
    openDetails,
    openUpdate,
    openPreUpload,
    openUpload,
    closeModal
  }
};