import { apiGet } from "./api";
import { AuthStatus } from "../types";

export const checkGoogleAuthStatus = () =>
  apiGet<AuthStatus>("/google/calendar/status");

export const listGoogleCalendars = () =>
  apiGet<any[]>("/google/calendar/list");