import { Club, Course } from "./types";

/**
 * Calculates a similarity score between two strings
 * Used for fuzzy matching event types to option types
 */
export function calculateMatchScore(str1: string | undefined, str2: string | undefined): number {
  if (!str1 || !str2) return 0;

  // Normalize both strings
  const s1 = str1.toLowerCase().replace(/s\b/g, '').trim();
  const s2 = str2.toLowerCase().replace(/s\b/g, '').trim();

  // Direct match
  if (s1 === s2) return 1;

  // One contains the other
  if (s1.includes(s2)) return 0.8;
  if (s2.includes(s1)) return 0.8;

  // Check for word-level matches
  const words1 = s1.split(/\s+/);
  const words2 = s2.split(/\s+/);

  let matchingWords = 0;
  for (const word1 of words1) {
    if (word1.length < 3) continue; // Skip short words

    for (const word2 of words2) {
      if (word2.length < 3) continue; // Skip short words

      if (word1 === word2 || word1.includes(word2) || word2.includes(word1)) {
        matchingWords++;
        break;
      }
    }
  }

  // Calculate a score based on matching words
  const maxWords = Math.max(words1.length, words2.length);
  return maxWords > 0 ? matchingWords / maxWords : 0;
} 

/**
 * Parse event title to extract entity ID and event type
 */
export function parseEventTitle(title: string, clubs: Club[]): { entityId?: string, eventType?: string } {
  // Try to extract course ID and event type from title
  if (title.includes(":")) {
    // Format: "entityId: eventType"
    const titleParts = title.split(':');
    return {
      entityId: titleParts[0]?.trim(),
      eventType: titleParts[1]?.trim() || title
    };
  } 

  // Format without colon separator (e.g. "15-122 OH" or "ScottyLabs Meeting")
  const words = title.split(' ');

  // Check if first word looks like a course ID (contains a dash)
  if (words[0] && words[0].includes('-')) {
    return {
      entityId: words[0],
      eventType: words.slice(1).join(' ')
    };
  }

  // Try to match a club name in the title
  let matchedClub = null;
  let bestMatchLength = 0;

  for (const club of clubs) {
    if (title.includes(club.name) && club.name.length > bestMatchLength) {
      matchedClub = club;
      bestMatchLength = club.name.length;
    }
  }

  if (matchedClub) {
    // Extract the event type by removing the club name
    const clubNameIndex = title.indexOf(matchedClub.name);
    const beforeClub = title.substring(0, clubNameIndex).trim();
    const afterClub = title.substring(clubNameIndex + matchedClub.name.length).trim();

    return {
      eventType: beforeClub || afterClub
    };
  }

  // Can't identify a specific entity, use the whole title as event type
  return { eventType: title };
}

/**
 * Determine if a course event should be shown based on matching options
 */
export function shouldShowCourseEvent(course: Course, eventType?: string): boolean {
  if (!eventType) return true;

  // Find the best matching option
  let bestMatch = null;
  let bestMatchScore = 0;

  for (const option of course.options) {
    const matchScore = calculateMatchScore(eventType, option.type);

    if (matchScore > bestMatchScore) {
      bestMatch = option;
      bestMatchScore = matchScore;
    }
  }

  // If we found a good match, use its selected state
  if (bestMatch && bestMatchScore > 0.3) {
    return bestMatch.selected;
  }

  return true; // Default to visible
}

/**
 * Determine if a club event should be shown based on matching options
 */
export function shouldShowClubEvent(club: Club, eventType?: string): boolean {
  if (!eventType) return true;

  // Find the best matching option
  let bestMatch = null;
  let bestMatchScore = 0;

  for (const option of club.options) {
    const matchScore = calculateMatchScore(eventType, option.type);

    if (matchScore > bestMatchScore) {
      bestMatch = option;
      bestMatchScore = matchScore;
    }
  }

  // If we found a good match, use its selected state
  if (bestMatch && bestMatchScore > 0.3) {
    return bestMatch.selected;
  }

  // Special case for meeting events
  if (eventType.toLowerCase().includes("meeting")) {
    const anyMeetingOptionSelected = club.options.some(option => 
      option.type.toLowerCase().includes("meeting") && option.selected
    );

    if (anyMeetingOptionSelected) {
      return true;
    }
  }

  return true; // Default to visible
} 
