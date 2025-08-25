import { apiGet, apiPost, api } from "./api";
import { TagType, EventPayloadType, GCalLinkPayloadType, ReadIcalLinkResponse } from "../types";
import type { AxiosResponse } from "axios";

export const fetchTagsForEvent = (eventId:number) =>
  apiGet<TagType[]>(`/events/${eventId}/tags`);

export const fetchAllTags = () => apiGet<TagType[]>(`/events/tags`);

export const createEvent = async (payload: EventPayloadType): Promise<any> => {
  try {
    const res = await api.post<void>("/events/create_event", payload);
    return res;
  } catch (error) {
    console.error("Failed to remove organization from schedule:", error);
    throw error;
  }
};

export const readIcalLink = async (payload : GCalLinkPayloadType) => {
  try {
    const res: AxiosResponse<ReadIcalLinkResponse> = await api.get<ReadIcalLinkResponse>('/events/read_gcal_link', { params: payload });
    return res;
  } catch (error) {
    console.error("Failed to read iCal link:", error);
    throw error;
  }
};