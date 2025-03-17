/**
 * Formats a date range into a human-readable string
 */
export function formatDateRange(startDate: string, endDate: string): string {
    const start = new Date(startDate);
    const end = new Date(endDate);
  
    const formatTime = (date: Date) => {
      return date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      });
    };
  
    // If same day
    if (start.toDateString() === end.toDateString()) {
      return `${start.toLocaleDateString('en-US', { 
        weekday: 'short',
        month: 'short', 
        day: 'numeric'
      })} · ${formatTime(start)} - ${formatTime(end)}`;
    } else {
      return `${start.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric'
      })} ${formatTime(start)} - ${end.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric'
      })} ${formatTime(end)}`;
    }
  } 