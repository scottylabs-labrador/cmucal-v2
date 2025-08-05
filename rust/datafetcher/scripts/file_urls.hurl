GET https://canvas.cmu.edu/api/v1/courses/sis_course_id:syllabus-registry-{{season}}{{year}}-{{department}}/modules
Authorization: Bearer {{token}}

HTTP/2 200

[Captures]
items_url: jsonpath "$[?(@.name == 'Available Syllabi')].items_url" nth 0
items_count: jsonpath "$[?(@.name == 'Available Syllabi')].items_count" nth 0

GET {{items_url}}?per_page={{items_count}}
Authorization: Bearer {{token}}

HTTP/2 200

[Captures]
file_urls: jsonpath "$[*].url"
title: jsonpath "$[*].title"
