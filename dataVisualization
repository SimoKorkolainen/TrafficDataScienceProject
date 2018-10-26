import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def readFile():
	df = pd.read_csv("combined.csv")
	return df

def main():
	df=readFile()
	print(df.head(20))

	plt.scatter(df['t2m'], df['n_speeding_cars'], s = 30, color = '#539caf', alpha = 0.1)
	plt.xlabel('Temperature')
	plt.ylabel('Number of speeding cars')

	plt.savefig('SpeedersTemp')
	plt.clf()

	plt.xlabel('Rain (10 min avg)')
	plt.ylabel('Number of speeding cars')
	plt.scatter(df['ri_10min'],df['n_speeding_cars'], s = 30, color = '#539caf', alpha = 0.1)

	plt.savefig('SpeedersRain')
	plt.clf()

	plt.xlabel('Wind speed (10 min avg)')
	plt.ylabel('Number of speeding cars')
	plt.scatter(df['wg_10min'],df['n_speeding_cars'], s = 30, color = '#539caf', alpha = 0.1)

	plt.savefig('SpeedersWind')
	plt.clf()

	countSpeeding = np.zeros((24))
	countTotal = np.zeros((24))
	for i in range(24):
		countSpeeding[i] = np.sum(df.ix[df['hour'] == i, 'n_speeding_cars'])
		countTotal[i] = np.sum(df.ix[df['hour'] == i, 'n_cars'])

	plt.xlabel('Hour')
	plt.ylabel('Number of speeding cars')
	plt.bar(np.arange(24), countSpeeding)
	plt.savefig('NumberOfSpeeders')
	plt.clf()

	plt.xlabel('Hour')
	plt.ylabel('Number of cars')
	plt.bar(np.arange(24), countTotal)
	plt.savefig('NumberOfCars')
	plt.clf()
	
main()
