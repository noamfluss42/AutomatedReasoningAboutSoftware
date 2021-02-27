import numpy as np

# 1827
A1 = np.array([[3, 2, 1, 2], [1, 1, 1, 1], [4, 3, 3, 4]])
b1 = np.array([225, 117, 420])
c1 = np.array([19, 13, 12, 17])
d1 = [A1, b1, c1]
# 10.5
A2 = np.array([[1, 1, 2], [2, 0, 3], [2, 1, 3]])
b2 = np.array([4, 5, 7])
c2 = np.array([3, 2, 4])
d2 = [A2, b2, c2]
# inf
A3 = np.array([[-1, 1], [-2, -2], [-1, 4]])
b3 = np.array([-1, -6, 2])
c3 = np.array([1, 3])
d3 = [A3, b3, c3]
# -8
A4 = np.array([[-1, 0], [0, -1]])
b4 = np.array([-3, -5])
c4 = np.array([-1, -1])
d4 = [A4, b4, c4]

# # unbounded example
A6 = np.array([[2, -2, 1, 0],
               [4, 0, 0, 1]])
c6 = np.array([4, 6, 0, 0])
b6 = np.array([6, 16])
d6 = [A6, b6, c6]
# 70
A7 = np.array([[1, 1, 1, 0, 0],
               [2, 3, 0, 1, 0],
               [1, 5, 0, 0, 1]])
c7 = np.array([6, 8, 0, 0, 0])
b7 = np.array([10, 25, 35])
d7 = [A7, b7, c7]

# 3
A8 = np.array([[1, 2, 3, 0],
               [-1, 2, 6, 0],
               [0, 4, 9, 0],
               [0, 0, 3, 1]])
b8 = np.array([3, 2, 5, 1])
c8 = np.array([1, 1, 1, 0])
d8 = [A8, b8, c8]

# 4
A9 = np.array([[-1, -1, 5], [-1, 1, 4]])
b9 = np.array([4, 6])
c9 = np.array([-1, -1, 5])
d9 = [A9, b9, c9]

# 2
A9_0 = np.array([[2, -1], [1, -5]])
b9_0 = np.array([2, -4])
c9_0 = np.array([2, -1])
d9_0 = [A9_0, b9_0, c9_0]

# 0
A10 = np.array([[-1, 2, -1], [-1, 1, -5]])
b10 = np.array([2, -4])
c10 = np.array([-1, 0, 0])
d10 = [A10, b10, c10]

# inf
A11 = np.array([[-1, -1, 3, 0]])
b11 = np.array([0])
c11 = np.array([0, 5, -1, 4])
d11 = [A11, b11, c11]

# 0.5, danzing does not stop
A12 = np.array([[0.5, -11 / 2, -5 / 2, 9], [1 / 2, -3 / 2, -1 / 2, 1], [1, 1, 1, 1]])
b12 = np.array([0, 0, 1])
c12 = np.array([10, -57, -9, -24])
d12 = [A12, b12, c12]
# 4
A13 = np.array([[4, 3], [4, 1], [4, 2]])
b13 = np.array([12, 8, 8])
c13 = np.array([2, 1])
d13 = [A13, b13, c13]

# None
A14 = np.array([[-1], [1]])
b14 = np.array([-3, 2])
c14 = np.array([1])
d14 = [A14, b14, c14]

d_list = [d1, d2, d4, d6, d7, d8, d9, d9_0, d10, d11, d12, d13,d14]
