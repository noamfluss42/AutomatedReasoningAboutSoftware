import numpy as np
import pprint
import scipy.linalg
from numpy.linalg import norm
from LP.input_test import *


class LPInput:
    THREADHOLD_BASIS_REFACTORING = 10
    EPSILON = 0.0000001

    def __init__(self, A: np.array, b, c, start_feasible=False, use_bland_rule=True):
        """
        :param A: m rows and n columns
        :param b: size m - base size
        :param c: size n - non base size
        """
        self.n = len(c)
        self.m = len(b)
        self.b_original = b.copy()
        self.B = np.eye(self.m)  # B0 in using eta
        self.B0 = np.eye(self.m)
        self.An = A.copy()
        self.xb_star = b.copy()
        self.cn = c.copy()
        self.cb = np.zeros(self.m)
        self.xn = np.arange(1, self.n + 1)
        self.xb = np.arange(self.n + 1, self.m + self.n + 1)
        self.use_bland_rule = use_bland_rule
        self.is_finish = False
        self.result = None
        self.eta_matrix = []
        self.eta_matrix_changed_col = []
        self.use_eta = True
        self.L = np.eye(self.m)
        self.U = np.eye(self.m)
        self.P = np.eye(self.m)
        self.start_feasible = start_feasible

    # TODO
    def check_feasible_solution(self):
        A_feasible = np.insert(self.An, 0, -1, axis=1)
        z = np.insert(np.zeros(self.n), 0, -1)
        feasible_lp = LPInput(A_feasible, self.xb_star, z, True)
        feasible_res = feasible_lp.solve()
        if feasible_res >= 0:
            return feasible_lp
        else:
            return None

    def set_base_by_feasible(self, feasible_lp):
        feasible_lp_x0_index = np.argmin(feasible_lp.xn)
        self.An = np.delete(feasible_lp.An, feasible_lp_x0_index, 1)
        # TODO b_original and B)
        self.B = feasible_lp.B  # B0 in using eta
        self.B0 = feasible_lp.B
        self.basis_refactoring()
        self.xb_star = feasible_lp.xb_star

        feasible_lp_xn = feasible_lp.xn[feasible_lp.xn != 1] - 1
        feasible_lp_xb = feasible_lp.xb - 1
        cn_copy = self.cn.copy()
        cb_copy = self.cb.copy()

        for i in range(self.n):
            if feasible_lp_xn[i] in self.xn:
                index_n = np.where(self.xn == feasible_lp_xn[i])
                self.cn[i] = cn_copy[index_n]
            else:
                index_b = np.where(self.xb == feasible_lp_xn[i])
                self.cn[i] = cb_copy[index_b]

        for i in range(self.m):
            if feasible_lp_xb[i] in self.xn:
                index_n = np.where(self.xn == feasible_lp_xb[i])
                self.cb[i] = cn_copy[index_n]
            else:
                index_b = np.where(self.xb == feasible_lp_xb[i])
                self.cb[i] = cb_copy[index_b]
        self.xn = feasible_lp_xn
        self.xb = feasible_lp_xb

    def finish(self):
        print("finish!!!")
        self.result = np.dot(self.xb_star, self.cb)
        self.is_finish = True

    def unbounded(self):
        print("unbounded!")
        self.is_finish = True
        self.result = np.inf

    def basis_refactoring(self):
        self.P, self.L, self.U = scipy.linalg.lu(self.B)
        self.B0 = self.B
        self.eta_matrix = []

    # TODO without copy
    def calc_BTRAN_eta(self, E, c, changed_col_index):
        res = c.copy()
        changed_col = E[:, changed_col_index].copy()
        diagonal_element = 1 / E[changed_col_index, changed_col_index]
        changed_col *= -1 * diagonal_element
        changed_col[changed_col_index] = diagonal_element
        res[changed_col_index] = np.dot(c, changed_col)
        return res

    def calc_BTRAN_per(self, P, c):
        res = np.empty(len(c))
        for i in range(len(P)):
            res[i] = c[np.argmax(P[i])]
        return res

    def calc_BTRAN_B0(self, c) -> np.array:
        for col_index in range(self.m):
            E = np.eye(self.m)
            E[:, col_index] = self.U[:, col_index]
            c = self.calc_BTRAN_eta(E, c, col_index)
        for col_index in range(self.m - 1, -1, -1):
            E = np.eye(self.m)
            E[:, col_index] = self.L[:, col_index]
            c = self.calc_BTRAN_eta(E, c, col_index)
        return self.calc_BTRAN_per(self.P, c)

    def calc_BTRAN(self) -> np.array:
        c = self.cb.copy()
        if self.use_eta:
            for i in range(len(self.eta_matrix) - 1, -1, -1):
                res = np.linalg.solve(np.transpose(self.eta_matrix[i]), c)
                c = res
            res = self.calc_BTRAN_B0(c)
            return res
        else:
            return np.linalg.solve(np.transpose(self.B), c)

    def calc_FTRAN_eta(self, E, c, changed_col_index):
        res = E[:, changed_col_index].copy()
        diagonal_element = 1 / E[changed_col_index, changed_col_index] * c[changed_col_index]
        res *= -1 * diagonal_element
        res += c
        res[changed_col_index] = diagonal_element
        return res

    def calc_FTRAN_per(self, P, c):
        res = np.empty(len(c))
        for i in range(len(P)):
            res[np.argmax(P[i])] = c[i]
        return res

    def calc_FTRAN_B0(self, c) -> np.array:
        c = self.calc_FTRAN_per(self.P, c)
        for col_index in range(self.m):
            E = np.eye(self.m)
            E[:, col_index] = self.L[:, col_index]
            c = self.calc_FTRAN_eta(E, c, col_index)
        for col_index in range(self.m - 1, -1, -1):
            E = np.eye(self.m)
            E[:, col_index] = self.U[:, col_index]
            c = self.calc_FTRAN_eta(E, c, col_index)
        return c

    def calc_FTRAN(self) -> np.array:
        c = self.An[:, self.entering_var_index_xn].copy()
        if self.use_eta:
            res = self.calc_FTRAN_B0(c)
            c = res
            for i in range(len(self.eta_matrix)):
                res = np.linalg.solve(self.eta_matrix[i], c)
                c = res
            return res
        else:
            return np.linalg.solve(self.B, c)

    def calc_z_var_coefficients(self):
        y = self.calc_BTRAN()
        self.z_var_coefficients = self.cn - np.dot(y, self.An)

    def dantzig_rule(self, z_var_coefficients_masked):
        self.entering_var_index_xn = np.argmax(z_var_coefficients_masked)

    def blan_rule(self, z_var_coefficients_masked):
        non_masked = np.ma.flatnotmasked_edges(z_var_coefficients_masked)
        self.entering_var_index_xn = non_masked[0]

    def pick_entering_var(self):
        if self.start_feasible:
            self.entering_var_index_xn = 0
            self.entering_var = 1
            return
        self.calc_z_var_coefficients()
        if all(self.z_var_coefficients <= 0):
            self.finish()
        else:  # 1827.0
            z_var_coefficients_masked = np.ma.masked_less_equal(self.z_var_coefficients, 0)
            if self.use_bland_rule:
                self.blan_rule(z_var_coefficients_masked)
            else:
                self.dantzig_rule(z_var_coefficients_masked)
            self.entering_var = self.xn[self.entering_var_index_xn]

    def pick_leaving_var(self):
        self.d = self.calc_FTRAN()
        if self.start_feasible:
            xb_star_div_d = self.xb_star / np.ma.masked_equal(self.d, 0)
        else:
            xb_star_div_d = self.xb_star / np.ma.masked_less_equal(self.d, 0)

        xb_star_div_d = np.ma.masked_less(xb_star_div_d, 0)
        if np.ma.flatnotmasked_edges(xb_star_div_d) is None:
            self.unbounded()
        if self.start_feasible:
            self.t = np.max(xb_star_div_d)
            self.leaving_var_index_xb = np.argmax(xb_star_div_d)
            self.start_feasible = False
        else:
            self.t = np.min(xb_star_div_d)
            self.leaving_var_index_xb = np.argmin(xb_star_div_d)
        self.leaving_var = self.xb[self.leaving_var_index_xb]

    def update_basis(self):
        temp = self.An[:, self.entering_var_index_xn].copy()
        self.An[:, self.entering_var_index_xn] = self.B[:, self.leaving_var_index_xb].copy()
        self.B[:, self.leaving_var_index_xb] = temp

        eta_matrix_to_add = np.eye(self.m)
        eta_matrix_to_add[:, self.leaving_var_index_xb] = self.d.copy()
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
        pprint.pprint(self.B)
        print("self.An")
        pprint.pprint(self.An)
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

    def check_epsilon_close(self):
        if norm(np.dot(self.B, self.xb_star) - self.b_original) > LPInput.EPSILON:
            self.basis_refactoring()

    def solve(self):
        """
        after init
        self.m = number of base vars
        self.n = number of non base vars = number of original vars
        :return:
        """
        if not self.start_feasible and not all(self.xb_star >= 0):
            feasible_lp = self.check_feasible_solution()
            if feasible_lp is None:
                return None
            self.set_base_by_feasible(feasible_lp)

        while True:
            self.pick_entering_var()
            if self.is_finish:
                return self.result
            self.pick_leaving_var()
            if self.is_finish:
                return self.result
            self.update_basis()
            if len(self.eta_matrix) > LPInput.THREADHOLD_BASIS_REFACTORING:
                self.basis_refactoring()
            self.check_epsilon_close()



print("start list",len(d_list))

for d_index in range(len(d_list)):
    print("\nstart",d_index + 1)
    d = d_list[d_index]
    a = LPInput(d[0], d[1], d[2],use_bland_rule=True)
    print(a.solve())
