import os
import json

current_dir = os.path.dirname(__file__)
target_path = os.path.abspath(os.path.join(current_dir, '../../../rust/all_courses.json'))

def get_course_data():
    """
    Reads course data from a JSON file, processes it to ensure unique courses,
    and writes the output to a new JSON file.
    """
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"File not found: {target_path}")
    
    # Load the input JSON file
    with open(target_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Dictionary to store unique courses by course number
    unique_courses = {}

    for entry in data:
        course = entry.get("course", {})
        metadata = entry.get("metadata", {})
        
        course_number = course.get("number")
        crosslisted = metadata.get("crosslisted", [])
        
        components = course.get("components", [])
        title = components[0].get("title") if components else ""

        # Use course_number as the unique key
        if course_number and course_number not in unique_courses:
            unique_courses[course_number] = {
                "course_number": course_number,
                "title": title,
                "crosslisted": crosslisted
            }

    # Convert dictionary values to list
    return list(unique_courses.values())

    output_data = list(unique_courses.values())

    # Write to output JSON file
    with open('courses_output.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)


