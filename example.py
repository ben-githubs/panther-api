""" In the following example code, we create a rule, then update the rule to add a unit test. For
the unit test's body, we fetch an actual event and sanitize it a bit.
"""

import os
from panther_seim import Panther
from panther_seim.exceptions import RuleTestFailure
from panther_seim.rules import Severities, UnitTest


# DOMAIN = "acme.runpanther.net"
DOMAIN = "panther-tse.runpanther.net"
API_KEY = os.environ.get("PANTHER_API_TOKEN")
API_KEY = "EDoy6Lfsie30PfWWwJ8CC7wJEcdfP8ByapfmQB4o"

panther = Panther(API_KEY, DOMAIN)

# Let's create a new rule

rule_body = """
def rule(event):
    eventType = event.get("eventType")
    actor = event.deep_get("actor", "alternateId")
    return eventType == "user.session.start" and actor = "dee.dee@hacker.com"
"""

new_rule = panther.rules.create(
    "My.Custom.Rule.ID",  # Rule ID
    rule_body,  # Rule Bode - the python code
    Severities.INFO,  # The severity (could be an enum or a string: "INFO")
    ["Okta.SystemLog"]  # The log types for the rule to run against
)
breakpoint()

# Nice, but let's add a unit test using a real event

query_text = """
SELECT * FROM okta_systemlog
WHERE eventType = 'user.session.start'
ORDER BY p_event_time DESC
LIMIT 1
"""

# Run the query, and get the results
results = panther.search.execute(query_text)

# Make sure we actually have 
if not results:
    print("Unable to add unit test - unable to find a previous login event")
    exit()

# Otherwise, fetch first result and modify it a bit
test_event = results[0]
test_event["actor"]["alternateId"] = "dee.dee@hacker.com"

# Make the unit test
unit_test = UnitTest(
    name = "My Sample Test",
    expected_result = True,
    event = test_event
)

# Finally, update the rule. However, our test could fail, so let's be prepared for that:
try:
    panther.rules.update(new_rule["id"], tests=[unit_test])
except RuleTestFailure as e:
    print("Unable to update rule with unit test due to failing tests:")
    for test_result in e.results:
        print("\t" + test_result.name)