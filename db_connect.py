import psycopg2
conn = psycopg2.connect(database="ddk3lh7bab56tv",user="ertuuktkzrmdyo",password="23ed549c19ea7b9919bd6ef6bb7c2e82aeac506db1260e0395cb92e16c2f9b88",host="ec2-54-157-78-113.compute-1.amazonaws.com",port="5432")
cur = conn.cursor()
cur.execute("SELECT date FROM play_list")
rows = cur.fetchall()
for r in rows:
    print(r)