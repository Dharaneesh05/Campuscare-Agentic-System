import sqlite3
import json

conn = sqlite3.connect('/home/dharane/.n8n/database.sqlite')
cursor = conn.cursor()
cursor.execute('SELECT nodes FROM workflow_entity WHERE id="SEyJhYhg6FocqNgR"')
row = cursor.fetchone()
nodes = json.loads(row[0])

for n in nodes:
    if n.get("name") == "Send Email":
        n["parameters"]["jsonBody"] = n["parameters"]["jsonBody"].replace(
            "to: 'dharaneeshc2006@gmail.com'",
            "to: $('Webhook Receiver').item.json.body.department_notification.to || 'dharaneeshc2006@gmail.com'"
        )
        print("Updated Send Email node!")
        print("Preview:", n["parameters"]["jsonBody"][:240])

new_nodes_json = json.dumps(nodes)
cursor.execute('UPDATE workflow_entity SET nodes = ? WHERE id = "SEyJhYhg6FocqNgR"', (new_nodes_json,))
cursor.execute('UPDATE workflow_history SET nodes = ? WHERE workflowId = "SEyJhYhg6FocqNgR"', (new_nodes_json,))
conn.commit()
print("Saved dynamic recipient to n8n SQLite successfully!")
