GET https://enr-apps.andrew.cmu.edu/open/SOC/SOCServlet/courseDetails?COURSE={{course}}&SEMESTER={{season}}{{year}}

HTTP/1.1 200

[Captures]
schedule: xpath "/html/body/div/div[1]/div/table/tbody"
special_permission: xpath "string(/html/body/div/div[2]/div[2]/dl/dd)"

description: xpath "string(/html/body/div/div[3]/div/p)"
prerequisites: xpath "string(/html/body/div/div[4]/div[1]/dl/dd)"
corequisites: xpath "string(/html/body/div/div[4]/div[2]/dl/dd)"
crosslisted: xpath "string(/html/body/div/div[5]/div[1]/dl/dd)"
notes: xpath "string(/html/body/div/div[5]/div[2]/dl/dd)"

# for related_urls and reservations
raw_body: body
