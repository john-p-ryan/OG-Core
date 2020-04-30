import numpy as np
import pandas as pd
import pytest
import os
from ogusa import fiscal
from ogusa.parameters import Specifications
CUR_PATH = os.path.abspath(os.path.dirname(__file__))

# Read in test data from file
df = pd.read_csv(os.path.join(CUR_PATH, 'test_io_data',
                              'get_D_G_path_data.csv'))
Y = df['Y'].values
TR = df['TR'].values
Revenue = df['Revenue'].values
Gbaseline = df['Gbaseline'].values
D1 = df['D1'].values
D2 = df['D2'].values
D3 = df['D3'].values
G1 = df['G1'].values
G2 = df['G2'].values
G3 = df['G3'].values
D_d1 = df['D_d1'].values
D_d2 = df['D_d2'].values
D_d3 = df['D_d3'].values
D_f1 = df['D_f1'].values
D_f2 = df['D_f2'].values
D_f3 = df['D_f3'].values
nb1 = df['new_borrow1'].values
nb2 = df['new_borrow2'].values
nb3 = df['new_borrow3'].values
ds1 = df['debt_service1'].values
ds2 = df['debt_service2'].values
ds3 = df['debt_service3'].values
nbf1 = df['new_borrow_f1'].values
nbf2 = df['new_borrow_f2'].values
nbf3 = df['new_borrow_f3'].values
expected_tuple1 = (D1, G1, D_d1, D_f1, nb1, ds1, nbf1)
expected_tuple2 = (D2, G2, D_d2, D_f2, nb2, ds2, nbf2)
expected_tuple3 = (D3, G3, D_d3, D_f3, nb3, ds3, nbf3)


@pytest.mark.parametrize(
    ('baseline_spending,Y,TR,Revenue,Gbaseline,budget_balance,expected_tuple'),
    [(False, Y, TR, Revenue, Gbaseline, False, expected_tuple1),
     (True, Y, TR, Revenue, Gbaseline, False, expected_tuple2),
     (False, Y, TR, Revenue, Gbaseline, True, expected_tuple3)],
    ids=['baseline_spending = False', 'baseline_spending = True',
         'balanced_budget = True'])
def test_D_G_path(baseline_spending, Y, TR, Revenue, Gbaseline,
                  budget_balance, expected_tuple):
    p = Specifications()
    new_param_values = {
        'T': 320,
        'S': 80,
        'debt_ratio_ss': 1.2,
        'tG1': 20,
        'tG2': 256,
        'alpha_T': [0.09],
        'alpha_G': [0.05],
        'rho_G': 0.1,
        'g_y_annual': 0.03,
        'baseline_spending': baseline_spending,
        'budget_balance': budget_balance
    }
    p.update_specifications(new_param_values, raise_errors=False)
    r_gov = np.ones(p.T + p.S) * 0.03
    p.g_n = np.ones(p.T + p.S) * 0.02
    D0 = 0.59
    G0 = 0.05
    dg_fixed_values = (Y, Revenue, TR, D0, G0)
    test_tuple = fiscal.D_G_path(r_gov, dg_fixed_values, Gbaseline, p)
    for i, v in enumerate(test_tuple):
        assert np.allclose(v[:p.T], expected_tuple[i][:p.T])


D1 = 1.411506406
D_d1 = 0.846903844
D_f1 = 0.564602563
new_borrowing1 = 0.072076633
debt_service1 = 0.042345192
new_borrowing_f1 = 0.028830653
expected_tuple1 = (D1, D_d1, D_f1, new_borrowing1, debt_service1,
                   new_borrowing_f1)
expected_tuple2 = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)


@pytest.mark.parametrize(
    ('budget_balance,expected_tuple'),
    [(False, expected_tuple1), (True, expected_tuple2)],
    ids=['balanced_budget = False', 'balanced_budget = True'])
def test_get_D_ss(budget_balance, expected_tuple):
    r_gov = 0.03
    Y = 1.176255339
    p = Specifications()
    p.debt_ratio_ss = 1.2
    p.budget_balance = budget_balance
    p.g_n_ss = 0.02
    test_tuple = fiscal.get_D_ss(r_gov, Y, p)

    for i, v in enumerate(test_tuple):
        assert np.allclose(v, expected_tuple[i])


expected_G1 = 0.729731441
expected_G2 = 0.0


@pytest.mark.parametrize(
    ('budget_balance,expected_G'),
    [(False, expected_G1), (True, expected_G2)],
    ids=['balanced_budget = False', 'balanced_budget = True'])
def test_get_G_ss(budget_balance, expected_G):
    total_revenue = 2.3
    TR = 1.6
    new_borrowing = 0.072076633
    debt_service = 0.042345192
    p = Specifications()
    p.budget_balance = budget_balance
    test_G = fiscal.get_G_ss(
        total_revenue, TR, new_borrowing, debt_service, p)

    assert np.allclose(test_G, expected_G)


p1 = Specifications()
p1.r_gov_scale = 0.5
p1.r_gov_shift = 0.0
p2 = Specifications()
p2.r_gov_scale = 0.5
p2.r_gov_shift = 0.01
p3 = Specifications()
p3.r_gov_scale = 0.5
p3.r_gov_shift = 0.03
r = 0.04
r_gov1 = 0.02
r_gov2 = 0.01
r_gov3 = 0.0


@pytest.mark.parametrize(
    'r,p,r_gov_expected', [(r, p1, r_gov1), (r, p2, r_gov2),
                           (r, p3, r_gov3)],
    ids=['Scale only', 'Scale and shift', 'r_gov < 0'])
def test_get_r_gov(r, p, r_gov_expected):
    r_gov = fiscal.get_r_gov(r, p)
    assert np.allclose(r_gov, r_gov_expected)
