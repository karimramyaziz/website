---
title: Visualizing the Mandelbrot Set Boundary
date: 2026-06-15
summary: A Python renderer exploring escape-time coloring and boundary zoom regions of the Mandelbrot set.
tags: [python, complex-analysis, fractals]
---

## Overview

A small project rendering the Mandelbrot set using the escape-time algorithm, with an interest in how boundary regions relate to the set's connectedness (a consequence of it being the connectedness locus of quadratic polynomials $z \mapsto z^2 + c$).

## The math

A point $c \in \mathbb{C}$ is in the Mandelbrot set if the orbit of $0$ under

$$z_{n+1} = z_n^2 + c$$

stays bounded. In practice, if $|z_n| > 2$ for any $n$, the orbit is guaranteed to escape to infinity, which is what makes the escape-time algorithm tractable.

## What's in the repo

- `mandelbrot.py` — core escape-time computation, vectorized with `numpy`
- `render.py` — coloring schemes (smooth iteration count vs. discrete banding)
- A few saved high-resolution renders of boundary zoom regions

## Status

Working renderer; next step is arbitrary-precision arithmetic (`mpmath`) to push zoom depth further before floating-point precision breaks down.

*(Replace this with your actual project details, and link to your GitHub repo here once it's public.)*
