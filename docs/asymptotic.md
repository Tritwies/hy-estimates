# Asymptotic analysis in the proof assistant

One of the original motivations for this proof assistant was to create an environment in which one can manipulate asymptotic estimates such as the following:

- $X \lesssim Y$ (also written $X = O(Y)$), which asserts that $|X| \leq CY$ for some absolute constant $C$.
- $X \ll Y$ (also written $X = o(Y)$), which asserts that for every constant $\varepsilon >0$, one has $|X| \leq \varepsilon Y$ if a suitable asymptotic parameter is large enough.
- $X \asymp Y$ (also written $X = \Theta(Y)$), which asserts that $X \lesssim Y \lesssim X$.

This is implemented within `sympy` as follows.  One first defines a new type of sympy expression, which I call `OrderOfMagnitude`, and corresponds to the space ${\mathcal O}$ discussed in [this blog post](https://terrytao.wordpress.com/2025/05/04/orders-of-infinity/).  These expressions are not numbers, but still support several algebraic operations, such as addition, multiplication, raising to numerical real exponents, and order comparison.  However, we caution that there is no notion of zero or subtraction in ${\mathcal O}$ (though for technical `sympy` reasons we implement a purely formal subtraction operation with no mathematical content).

There is then an operation `Theta` that maps positive real `sympy` expressions to `OrderOfMagnitude` expressions, which then allows one to interpret the above asymptotic statements:

- $X \lesssim Y$ is formalized as `lesssim(X,Y)`, which is syntactic sugar for `Theta(Abs(X)) <= Theta(Y)`.
- $X \ll Y$ is formalized as `ll(X,Y)`, which is syntactic sugar for `Theta(Abs(X)) < Theta(Y)`.
- $X \asymp Y$ is formalized as `asymp(X,Y)`, which is syntactic sugar for `Eq(Theta(X), Theta(Y))`.

Various laws of asymptotic arithmetic have been encoded within the syntax of `sympy`, for instance `Theta(C)` simplifies to `Theta(1)` for any numerical constant `C`, `Theta(X+Y)` simplifies to `Max(Theta(X),Theta(Y))`, and so forth.

Expressions can be marked as "fixed" (resp. "bounded"), in which case they will be marked has having order of magnitude equal to (resp. at most) `Theta(1)` for the purposes of logarithmic linear programming.

**Technical note**: to avoid some unwanted applications of `sympy`'s native simplifier (in particular, those applications that involve subtraction, which we leave purely formal for orders of magnitude), and to force certain type inferences to work, `OrderOfMagnitude` overrides the usual `Add`, `Mul`, `Pow`, `Max`, and `Min` operations with custom alternatives `OrderAdd`, `OrderMul`, `OrderPow`, `OrderMax`, `OrderMin`.

**Technical note**: We technically permit `Theta` to take non-positive values, but a warning will be sent if this happens and an `Undefined()` element will be generated.  (`sympy`'s native simplifier will sometimes trigger this warning.)  Similarly for other undefined operations, such as `OrderMax` or `OrderMin` applied to an empty tuple.

**A "gotcha"**: One should avoid using python's native `max` or `min` command with orders of magnitude, or even `sympy`'s alternative `Max` and `Min` commands.  Use `OrderMax` and `OrderMin` instead.

An abstract order of magnitude can be created using the `OrderSymbol(name)` constructor, similar to the `Symbol()` constructor in `sympy` (but with attributes such as `is_positive` set to false, with the exception of the default flag `is_commutative`).

Here is a simple example of the proof assistant establishing an asymptotic estimate. Informally, one is given a positive integer $N$ and positive reals $x,y$ such that $x \leq 2N^2$ and $y < 3kN$ with $k$ bounded, and the task is to conclude that $xy \lesssim N^4$.

```
>>> from estimates.main import *
>>> p = loglinarith_exercise()
Starting proof.  Current proof state:
N: pos_int
x: pos_real
y: pos_real
hk: Bounded(k)
h1: x <= 2*N**2
h2: y < 3*N*k
|- Theta(x)*Theta(y) <= Theta(N)**4
>>> p.use(LogLinarith(verbose=True))
Identified the following disjunctions of asymptotic inequalities that we need to obtain a contradiction from:
['Theta(N)**1 >= Theta(1)']
['Theta(x)**1 * Theta(N)**-2 <= Theta(1)']
['Theta(k)**1 >= Theta(1)']
['Theta(x)**1 * Theta(y)**1 * Theta(N)**-4 > Theta(1)']
['Theta(y)**1 * Theta(N)**-1 * Theta(k)**-1 <= Theta(1)']
['Theta(k)**1 <= Theta(1)']
Checking feasibility of the following inequalities:
Theta(N)**1 >= Theta(1)
Theta(x)**1 * Theta(N)**-2 <= Theta(1)
Theta(k)**1 >= Theta(1)
Theta(x)**1 * Theta(y)**1 * Theta(N)**-4 > Theta(1)
Theta(y)**1 * Theta(N)**-1 * Theta(k)**-1 <= Theta(1)
Theta(k)**1 <= Theta(1)
Infeasible by multiplying the following:
Theta(N)**1 >= Theta(1) raised to power 1
Theta(x)**1 * Theta(N)**-2 <= Theta(1) raised to power -1
Theta(x)**1 * Theta(y)**1 * Theta(N)**-4 > Theta(1) raised to power 1
Theta(y)**1 * Theta(N)**-1 * Theta(k)**-1 <= Theta(1) raised to power -1
Theta(k)**1 <= Theta(1) raised to power -1
Proof complete!
```


## `Theta(expr) -> OrderOfMagnitude`

Returns the order of magnitude associated to a non-negative quantity `expr`.

## `Fixed(expr:Expr)`

Marks an expression as fixed (independent of parameters).

## `Bounded(expr:Expr)`

Marks an expression as bounded (ranging in a compact set for all choices of parameters).

## `is_fixed(expr:Expr, hypotheses:set[Basic]) -> Bool`

Tests if an expression is fixed, given the known hypotheses.

## `is_bounded(expr:Expr, hypotheses:set[Basic]) -> Bool`

Tests if an expression is bounded, given the known hypotheses.
