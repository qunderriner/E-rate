import pandas as pd

def make_database_csv(df, states, num):
	'''
	Inputs:
		df: full dataframe
		states: list of states to include in hosted db
		num: number of random rows want to sample
	'''
	rv = pd.DataFrame(columns=df.columns)

	for state in states:
		df1 = df[df['Applicant State'] == state].sample(n=num)
		rv = rv.append(df1)

	return rv