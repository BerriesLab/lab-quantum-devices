from numpy import linspace, zeros, exp, asarray
import matplotlib.pyplot as plt


def ode_FE(f, u0, dt, T):

    """ To solve (a system of) ODE of type: u'(t)=f(u,t)
        T: is the maximum time of the simulation
        dt: is the time interval between cell edges
        u0: is the initial condition (1d or 2d vector)
        f: is the function """

    f_ = lambda u, t: asarray(f(u, t))      # Ensure that any list/tuple returned from f_ is wrapped as array
    N_t = int(round(T/dt))                  # define number of (time) steps
    u = zeros((N_t+1, len(u0)))             # make array of u
    t = linspace(0, N_t*dt, len(u))         # make array of t

    u[0] = u0                               # initialize u
    for n in range(N_t):
        u[n+1] = u[n] + dt*f_(u[n], t[n])   # compute u with forward Euler scheme

    return u, t


def demo_population_growth():
    """Test case: u'=r*u, u(0)=100."""

    def f(u, t):
        return 0.1*u

    u, t = ode_FE(f=f, u0=100, dt=0.5, T=20)
    plt.plot(t, u, 'o')
    plt.plot(t, 100*exp(0.1*t), '-')
    plt.show()


if __name__ == '__main__':
    demo_population_growth()
