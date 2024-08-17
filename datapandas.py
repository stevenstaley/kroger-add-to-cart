from sqlalchemy import create_engine
import pandas as pd

cnx = create_engine('sqlite:///kroger.db').connect()
sql = pd.read_sql('allitems', cnx)

print(sql['image'])