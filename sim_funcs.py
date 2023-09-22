import numpy as np
from scipy.integrate import odeint
from math import fabs, pi

## Define the state derivative 
def get_xdot(x, t, A, B, controlLaw, Umax, Kp, Kd):
    x = np.array(x).reshape(2,1)
    if controlLaw == "PD":
        u = PD(x, Kp, Kd)
    elif controlLaw == "bang_bang":
        u = bang_bang(x, Umax)
    u = filter_U(u, Umax)
    u = np.array(u).reshape(1,1)
    xdot = A@x + B@u
    return [xdot[0, 0], xdot[1, 0]]

def get_xdot_const(x, t, A, B, controlLaw, Umax, Kp, Kd):
    x = np.array(x).reshape(2,1)
    if controlLaw == "PD":
        u = PD(x, Kp, Kd)
    elif controlLaw == "bang_bang":
        u = bang_bang(x, Umax)
    u = filter_U(u, Umax)
    u = np.array(u).reshape(1,1)
    xdot = A@x + B@u
    xdot = np.ones(np.size(xdot))
    return [xdot[0, 0], xdot[1, 0]]

# Define Control Laws
def PD(x, Kp, Kd):
    theta = x[0]
    theta_dot = x[1]
    u = Kp * theta + Kd * theta_dot
    return u

def bang_bang(x, Umax):
    u = Umax
    if x[0] > 0:
        u = -Umax
    elif x[0] == 0:
        u = 0
    return u

def filter_U(u, Umax):
    u = max(-Umax, u)
    u = min(Umax, u)
    return u

def run_sim(controlLaw, Umax, Kp, Kd, I, theta0, thetadot0, tf, truncate):
    ## Inialize Simulation
    t0 = 0
    dt = 0.01
    time = list(np.arange(t0, tf, dt))
    Nt = len(time)

    # Define Open-Loop Dynamics
    A = np.array([[0, 1], [0, 0]])
    B = np.array([[0], [1/I]])

    # Propogate ODE
    x0 = [theta0, thetadot0]
    X = odeint(get_xdot, x0, time, args=(A, B, controlLaw, Umax, Kp, Kd))
    U = [None]*len(X)

    for i,x in enumerate(X):
        if controlLaw == "PD":
            u = PD(x, Kp, Kd)
        elif controlLaw == "bang_bang":
            u = bang_bang(x, Umax)
        U[i] = filter_U(u, Umax)

    if truncate:
        for i,x in enumerate(X[:, 0]):
            [angle, count] = transform_to_pipi(x)
            X[i, 0] = angle

    return time, X, U

# Generate a set of Initial Conditions
def gen_X0s(theta_min, theta_max, theta_dot_min, theta_dot_max, Nx):
    Theta0s = list(np.linspace(theta_min, theta_max, Nx))
    Theta_dot0s = list(np.linspace(theta_dot_min, theta_dot_max, Nx))
    return Theta0s, Theta_dot0s

def gen_phase_data(controlLaw, Umax, Kp, Kd, I ,Theta0s, Theta_dot0s, tf):
    # Init output data structure
    N_theta0 = len(Theta0s)
    N_theta_dot0 = len(Theta_dot0s)
    phase_data = np.empty((N_theta0, N_theta_dot0), dtype=object)

    # Iterate through initial conditions and save sim results
    for i, theta0 in enumerate(Theta0s):
        for j, thetadot0 in enumerate(Theta_dot0s):
            [time, X, U] = run_sim(controlLaw, Umax, Kp, Kd, I, theta0, thetadot0, tf, False)
            phase_data[i, j] = X
    
    return phase_data

def truncated_remainder(dividend, divisor):
    divided_number = dividend / divisor
    divided_number = \
        -int(-divided_number) if divided_number < 0 else int(divided_number)

    remainder = dividend - divisor * divided_number

    return remainder

def transform_to_pipi(input_angle):
    revolutions = int((input_angle + np.sign(input_angle) * pi) / (2 * pi))

    p1 = truncated_remainder(input_angle + np.sign(input_angle) * pi, 2 * pi)
    p2 = (np.sign(np.sign(input_angle)
                + 2 * (np.sign(fabs((truncated_remainder(input_angle + pi, 2 * pi))
                                    / (2 * pi))) - 1))) * pi

    output_angle = p1 - p2

    return output_angle, revolutions

