---
title: N-Body Gravitational Simulation
date: 2026-06-01
summary: A Python simulation of gravitational N-body dynamics using symplectic integration.
tags: [python, simulation, mechanics]
---

## Overview

A small Python project simulating gravitational interactions between $N$ bodies using a **leapfrog (velocity-Verlet) integrator**, chosen over Runge-Kutta methods because it's symplectic — it conserves energy over long timescales instead of slowly leaking or gaining it.

## The physics

Each body $i$ feels a gravitational force from every other body $j$:

$$\mathbf{F}_i = -Gm_i \sum_{j \neq i} \frac{m_j (\mathbf{r}_i - \mathbf{r}_j)}{|\mathbf{r}_i - \mathbf{r}_j|^3}$$

Naive implementation is $O(N^2)$ per timestep — fine up to a few thousand bodies, but a Barnes-Hut tree approximation would be the next step for anything larger.

## What's in the repo

- `simulate.py` — core integrator
- `plot.py` — trajectory visualization with `matplotlib`
- A three-body figure-eight orbit as a validation test case

## Status

Working for small $N$; next step is adding adaptive timestepping for close encounters.

*(Replace this with your actual project details, and link to your GitHub repo here once it's public.)*
