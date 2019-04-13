import scipy.optimize
import numpy as np
import pyqtgraph as pg

pg.dbg()

def map(m, pts):
    # pts1 = np.empty((pts.shape[0], pts.shape[1]+1))
    # pts1[:,:-1] = pts
    # pts1[:,-1] = 1
    return np.dot(pts, m[:, :-1].T) + m[:, -1]

def dist(m, X, Y):
    Y1 = map(m, X)
    dif = Y - Y1
    return np.linalg.norm(dif, axis=1)

best = (np.inf, None)
def err(m, X, Y):
    global best
    m = m.reshape(3, 4)
    e = np.linalg.norm(dist(m, X, Y))

    if e < best[0]:
        best = (e, m)
    
    return e


def fit_transform(guess, X, Y):
    global best
    best = (np.inf, None)
    result = scipy.optimize.minimize(err, x0=guess, args=(X, Y),
        tol=1e-12,
        options={
            'eps': 1e-11, 
            'gtol': 1e-12, 
            'disp': True,
            'maxiter': 20000,
        }, 
        method='Nelder-Mead',
        # method='Powell',
    )
    return result.x.reshape(3,4)


def solve(X, Y):
    npts, ndim = X.shape
    assert X.shape == Y.shape
    assert npts == ndim + 1

    Xa = np.empty((npts, npts))
    Xa[:, :ndim] = X
    Xa[:, ndim] = 1
    Ya = np.empty((npts, npts))
    Ya[:, :ndim] = Y
    Ya[:, ndim] = 1

    ## solve 3 sets of linear equations to determine transformation matrix elements
    matrix = np.zeros((npts, npts))
    for i in range(ndim):
        ## solve Ax = B; x is one row of the desired transformation matrix
        matrix[i] = np.linalg.solve(Xa, Ya[:,i])  
    
    return matrix[:ndim]


def solve_many(X, Y, n_iter=100):
    m = []
    for i in range(n_iter):
        inds = list(range(len(X)))
        np.random.shuffle(inds)
        Xa = X[inds[:4]]
        Ya = Y[inds[:4]]
        m.append(solve(Xa, Ya))
    m = np.mean(np.dstack(m), axis=2)
    return m


def plot_xy(x, y, plt, ax=(0,1)):
    plt.plot(x[:,ax[0]], x[:,ax[1]], pen=None, symbol='o', symbolBrush=(0, 255, 0, 100), symbolPen=None)
    plt.plot(y[:,ax[0]], y[:,ax[1]], pen=None, symbol='o', symbolBrush=(0, 0, 255, 100), symbolPen=None)
    plt.plot(np.ravel(np.array(zip(x[:,ax[0]], y[:,ax[0]]))), np.ravel(np.array(zip(x[:,ax[1]], y[:,ax[1]]))), connect='pairs')


def plot_xyz(x, y, title):
    w = pg.GraphicsLayoutWidget()
    w.show()
    w.setWindowTitle(title)
    plt1 = w.addPlot()
    plot_xy(x, y, plt1, ax=(0,1))
    plt2 = w.addPlot(row=1, col=0)
    plot_xy(x, y, plt2, ax=(0,2))
    return w


X = np.array([[15362912.,  8542584., 16714110.],
       [15464614.,  8318862., 16712858.],
       [15576906.,  8493202., 16718364.],
       [15473246.,  8395342., 16595166.],
       [15572100.,  8354122., 16600332.],
       [15494974.,  8586310., 16602382.],
       [15362154.,  8368836., 16595876.],
       [15445784.,  8526146., 16769798.],
       [15558862.,  8401362., 16770018.],
       [15408288.,  8352502., 16765834.]])

Y = np.array([[-1.91778515e-02,  1.99578199e-02,  6.75236806e-05],
       [-1.90775996e-02,  2.01811462e-02,  6.75236806e-05],
       [-1.89651609e-02,  2.00059000e-02,  6.75236806e-05],
       [-1.90679518e-02,  2.00998880e-02,  1.89979561e-04],
       [-1.89695230e-02,  2.01415448e-02,  1.90411694e-04],
       [-1.90454534e-02,  1.99107776e-02,  1.90461986e-04],
       [-1.91790648e-02,  2.01283245e-02,  1.90461986e-04],
       [-1.90928492e-02,  1.99712950e-02,  1.65719539e-05],
       [-1.89809353e-02,  2.00934867e-02,  1.65719539e-05],
       [-1.91299635e-02,  2.01437338e-02,  1.65719539e-05]])

Y[0,0] += 0.0001




# guess = solve(X[:4], Y[:4])
guess = solve_many(X, Y)

print("GUESS:")
print(guess)
guess = guess[:3]
Y_guess = map(guess, X)
print(dist(guess, X, Y))
# print(abs(guess-m) / abs(m))

m_fit = fit_transform(guess, X, Y)
Y_fit = map(m_fit, X)
print("FINAL:")
print(m_fit)
d_fit = dist(m_fit, X, Y)
print(d_fit)
print(np.linalg.norm(d_fit))
# print(abs(m_fit-m) / abs(m))

print("SUPERFINAL:")
mask = (d_fit - d_fit.mean()) < d_fit.std()*2
print(mask)
X_masked = X[mask]
Y_masked = Y[mask]
m_fit2 = fit_transform(guess,  X_masked, Y_masked)
Y_masked_fit = map(m_fit2, X_masked)
print(m_fit2)
d_fit2 = dist(m_fit2, X_masked, Y_masked)
print(d_fit2)
print(np.linalg.norm(d_fit2))
# print(abs(m_fit-m) / abs(m))

pg.mkQApp()

w1 = plot_xyz(Y, Y_guess, "Initial guess")
w2 = plot_xyz(Y, Y_fit, "Initial fit")
w3 = plot_xyz(Y_masked, Y_masked_fit, "Final fit")


