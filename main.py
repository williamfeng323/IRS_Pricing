import utils.utils as utl
import utils.computation as cp
import numpy as np
import matplotlib.pyplot as plt

sigma_list = np.arange(0.01, 1, .01).tolist()
swap_values = list()
for v in sigma_list:
    swap_values.append(cp.calculate_swap(.02, 5, .5, sigma=v))

print(sigma_list)
print(swap_values)
plt.plot(sigma_list, swap_values, '-')
plt.savefig('sigma_sensitivity.png', bbox_inches='tight', dpi=1200)
plt.show()
#
# bond_price = cp.calculate_bond(.02, 100, 5.016438)
# print('price of the 5 bond is ' + str(bond_price))
# print('different between calculated price and actual price: ' + str(bond_price - 100.281250))
#
# bond_price = cp.calculate_bond(.01125, 100, 4.5205479)
# print('price of the 4.5 bond is ' + str(bond_price))
# print('different between calculated price and actual price: ' + str(bond_price - 96.812500))
#
# bond_price = cp.calculate_bond(.03625, 100, 3.9808219)
# print('price of the 4 bond is ' + str(bond_price))
# print('different between calculated price and actual price: ' + str(bond_price - 107.1875))
#
# bond_price = cp.calculate_bond(.01375, 100, 2.978082)
# print('price of the 3 bond is ' + str(bond_price))
# print('different between calculated price and actual price: ' + str(bond_price - 99.6875))
#
# bond_price = cp.calculate_bond(.0275, 100, 1.978082)
# print('price of the 2 bond is ' + str(bond_price))
# print('different between calculated price and actual price: ' + str(bond_price - 102.96875))
#
# bond_price = cp.calculate_bond(.035, 100, .97808)
# print('price of the 1 bond is ' + str(bond_price))
# print('different between calculated price and actual price: ' + str(bond_price - 102.5))
swap_value = cp.calculate_swap(.02, 5)
print(swap_value)
