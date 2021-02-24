import numpy as np


class LPInput:

    def __init__(self, A: np.array, b, c):
        """
        :param A: m rows and n columns
        :param b: size m - base size
        :param c: size n - non base size
        """
        self.iter_num = 1
        self.n = len(c)
        self.m = len(b)
        self.B = np.eye(self.m)  # B0 in using eta
        self.An = A.copy()
        self.xb_star = b.copy()
        self.cn = c.copy()
        self.cb = np.zeros(self.m)
        self.xn = np.arange(1, self.n + 1)
        self.xb = np.arange(self.n + 1, self.m + self.n + 1)
        self.use_blan_rule = True
        self.is_finish = False
        self.result = None
        self.eta_matrix = []
        self.use_eta = False

    # TODO
    def check_feasible_solution(self):
        A_feasible = self.An.copy()
        A_feasible = [row.insert(0, -1) for row in A_feasible]
        LP_feasible = LPInput(A_feasible, self.b.copy(), [-1] + [0 for i in range(len(self.c))])
        sol_feasible = LP_feasible.solve()
        if sol_feasible[0] == 0:
            return True

    def calc_BTRAN(self) -> np.array:
        if self.use_eta:
            c = self.cb
            for i in range(len(self.eta_matrix) - 1, -1, -1):
                res = np.linalg.solve(np.transpose(self.eta_matrix[i]), c)
                c = res
            res = np.linalg.solve(np.transpose(self.B), c)
            c = res
            return res
        else:
            return np.linalg.solve(np.transpose(self.B), self.cb)

    def calc_FTRAN(self) -> np.array:
        c = self.An[:, self.entering_var_index_xn]
        if self.use_eta:
            for i in range(len(self.eta_matrix) - 1, -1, -1):
                res = np.linalg.solve(self.eta_matrix[i], c)
                c = res
            res = np.linalg.solve(self.B, c)
            c = res
            return res
        else:
            return np.linalg.solve(self.B, c)

    def calc_z_var_coefficients(self):
        y = self.calc_BTRAN()
        print("y", y)
        self.z_var_coefficients = self.cn - np.dot(y, self.An)

    def finish(self):
        print("finish!!!")
        self.result = np.dot(self.xb_star, self.cb)
        self.is_finish = True

    def unbounded(self):
        print("unbounded!")
        self.is_finish = True

    def dantzig_rule(self, z_var_coefficients_masked):
        self.entering_var_index_xn = np.argmin(z_var_coefficients_masked)

    def blan_rule(self, z_var_coefficients_masked):
        non_masked = np.ma.flatnotmasked_edges(z_var_coefficients_masked)
        self.entering_var_index_xn = non_masked[0]

    def pick_entering_var(self):
        self.calc_z_var_coefficients()
        if all(self.z_var_coefficients <= 0):
            self.finish()
        else:  # 1827.0
            z_var_coefficients_masked = np.ma.masked_less_equal(self.z_var_coefficients, 0)
            if self.use_blan_rule:
                self.blan_rule(z_var_coefficients_masked)
            else:
                self.dantzig_rule(z_var_coefficients_masked)
            self.entering_var = self.xn[self.entering_var_index_xn]
            print("self.entering_var", self.entering_var)

    def pick_leaving_var(self):

        self.d = self.calc_FTRAN()

        print("self.d", self.d)
        # TODO masked_less_equal or masked_less
        xb_star_div_d = np.ma.masked_less_equal(self.xb_star, 0) / np.ma.masked_less_equal(self.d, 0)
        self.t = np.min(xb_star_div_d)
        if np.ma.flatnotmasked_edges(xb_star_div_d) is None:
            self.unbounded()
        print("self.t", self.t)
        self.leaving_var_index_xb = np.argmin(xb_star_div_d)
        self.leaving_var = self.xb[self.leaving_var_index_xb]
        print("self.leaving_var", self.leaving_var)

    def update_basis(self):
        temp = self.An[:, self.entering_var_index_xn].copy()
        self.An[:, self.entering_var_index_xn] = self.B[:, self.leaving_var_index_xb].copy()
        self.B[:, self.leaving_var_index_xb] = temp

        eta_matrix_to_add = np.eye(self.m)
        eta_matrix_to_add[:, self.leaving_var_index_xb] = temp.copy()
        self.eta_matrix.append(eta_matrix_to_add)

        temp_var_index = self.xb[self.leaving_var_index_xb]
        self.xb[self.leaving_var_index_xb] = self.xn[self.entering_var_index_xn]
        self.xn[self.entering_var_index_xn] = temp_var_index
        self.xb_star = np.subtract(self.xb_star, np.dot(self.t, self.d))
        self.xb_star[self.leaving_var_index_xb] = self.t
        temp_c_val = self.cn[self.entering_var_index_xn]
        self.cn[self.entering_var_index_xn] = self.cb[self.leaving_var_index_xb]
        self.cb[self.leaving_var_index_xb] = temp_c_val

    def print(self):
        print("")
        print("self.B")
        print(self.B)
        print("self.An")
        print(self.An)
        print("self.xb")
        print(self.xb)
        print("self.xn")
        print(self.xn)
        print("self.xb_star")
        print(self.xb_star)
        print("self.cb")
        print(self.cb)
        print("self.cn")
        print(self.cn)

    def solve(self):
        """
        after init
        self.m = number of base vars
        self.n = number of non base vars = number of original vars
        :return:
        """
        while True:
            print("start iter")
            self.print()
            self.pick_entering_var()
            if self.is_finish:
                return self.result
            self.pick_leaving_var()
            if self.is_finish:
                return self.result
            self.update_basis()


A1 = np.array([[3, 2, 1, 2], [1, 1, 1, 1], [4, 3, 3, 4]])
b1 = np.array([225, 117, 420])
c1 = np.array([19, 13, 12, 17])

A2 = np.array([[1, 1, 2], [2, 0, 3], [2, 1, 3]])
b2 = np.array([4, 5, 7])
c2 = np.array([3, 2, 4])

A3 = np.array([[-1, 1], [-2, -2], [-1, 4]])
b3 = np.array([-1, -6, 2])
c3 = np.array([1, 3])

a = LPInput(A2, b2, c2)
print(a.solve())
