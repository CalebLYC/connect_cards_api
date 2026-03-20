import psycopg2
conn=psycopg2.connect('postgresql://neondb_owner:npg_MZ7LkzcG3OEi@ep-withered-surf-an7db9bq-pooler.c-6.us-east-1.aws.neon.tech/neondb')
cur=conn.cursor()
cur.execute("SELECT id, event_type, is_active, organization_id, project_id FROM webhooks")
print('WEBHOOKS:', cur.fetchall())
