type GCalEvent = {
    id?: string;
    title?: string;
    start: string;
    end: string;
    location?: string;
    allDay?: boolean;
};
  
type FullCalendarEvent = {
    id: string;
    title: string;
    start: string | Date;
    end: string | Date;
    allDay?: boolean;
    classNames?: string[];
};

// need to add more fields to this, such as location, description, source, etc.
export function formatGCalEvent(event: GCalEvent): FullCalendarEvent {
    return {
        id: `${event.title}-${event.start}`,
        title: event.title || "Untitled Event",
        start: event.allDay ? event.start : new Date(event.start),
        end: event.allDay ? event.end : new Date(event.end),
        allDay: event.allDay,
        classNames: ["gcal-event"],
    };
}

// note: probably need to change this to use the same format as gcal events
export function formatCMUCalEvent(event: any) {
    return {
        ...event,
        classNames: ["cmucal-event"],
    };
}
