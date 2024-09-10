import pandas as pd
from sqlalchemy import create_engine, text

pd.options.display.float_format = '{:,.2f}'.format

engine = create_engine('sqlite:///test_database.db', echo=False)

with engine.begin() as conn:
    clients = pd.read_csv('clients.csv')
    clients.to_sql(name='clients',  con=conn, if_exists='append', index=False)
    products = pd.read_csv('products.csv')
    products.to_sql(name='products',  con=conn, if_exists='append', index=False)
    balances = pd.read_csv('balances.csv')
    balances.to_sql(name='balances',  con=conn, if_exists='append', index=False)
    
    print(conn.execute(text("SELECT * FROM clients")).fetchone())
    print(conn.execute(text("SELECT * FROM products")).fetchone())
    print(conn.execute(text("SELECT * FROM balances")).fetchone())