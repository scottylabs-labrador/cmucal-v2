GET {{file_url}}
Authorization: Bearer {{token}}

HTTP/2 200

[Asserts]
jsonpath "$.filename" exists

[Captures]
final_url: jsonpath "$.url"
