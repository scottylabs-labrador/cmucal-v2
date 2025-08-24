import { apiGet, apiPost } from "./api";
import { TagType } from "../types";

export const fetchTags = (eventId:number) =>
  apiGet<TagType[]>(`/events/${eventId}/tags`);