import pandas as pd 

# df1 = pd.read_csv('db/users_data.csv')
# df2 = pd.read_csv('db/test.csv')

sc = {'chat_id': 366321052, 'user_id': 366321052, 'current_status': 'language', 'lang': None, 'birthdays': '{}'}
df = pd.DataFrame(sc, index=[0])
print(df)
# df["chat_id"] = []
# df["user_id"] = []
# df["current_status"] = []
# df["last_message"] = []
# df["lang"] = []
# df["username"] = []
# df.to_csv("db/users_data.csv", index=False)
