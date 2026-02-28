"""Pathfinding algorithms for motion planning."""
from __future__ import annotations

from typing import Callable, List

import numpy as np


def reconstruct_path(came_from, current):
    """Reconstruct a path from the came_from dictionary."""
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]


def generate_even_sphere_points(n_points: int, sphere_radius: float):
    """Generate points with an even distribution of directions but random lengths."""
    phi = np.pi * (3.0 - np.sqrt(5.0))  # golden angle in radians

    directions = []
    for i in range(n_points):
        y = 1 - (i / float(n_points - 1)) * 2  # y goes from 1 to -1
        radius = np.sqrt(1 - y * y)  # radius at y

        theta = phi * i  # golden angle increment

        x = np.cos(theta) * radius
        z = np.sin(theta) * radius

        directions.append(np.array([x, y, z]))

    radii = sphere_radius * np.cbrt(np.random.random(n_points))
    return np.array(directions) * radii[:, np.newaxis]


def generate_biased_sphere_points(
    n_points: int, sphere_radius: float, bias_direction: np.ndarray, concentration=1.0
):
    """
    Generate random points within a sphere with directional bias.

    Parameters
    ----------
    n_points : int
        Number of points to generate.
    sphere_radius : float
        Radius of the containing sphere.
    bias_direction : np.ndarray
        Unit vector indicating preferred direction.
    concentration : float
        Controls spread (higher = more concentrated around bias direction).

    Returns
    -------
    np.ndarray
        Array of points (n_points, 3).
    """
    bias_direction = bias_direction / np.linalg.norm(bias_direction)

    # Generate points using von Mises-Fisher distribution
    # This provides a directionally biased distribution on a sphere
    def sample_vmf(mu, kappa, size):
        dim = len(mu)

        # Generate base distribution
        base = np.random.normal(0, 1, (size, dim))
        base /= np.linalg.norm(base, axis=1)[:, np.newaxis]

        dot_products = base @ mu

        # Apply concentration with element-wise multiplication
        result = base + kappa * (dot_products[:, np.newaxis] * mu - base)
        return result / np.linalg.norm(result, axis=1)[:, np.newaxis]

    # Sample directions with bias
    directions = sample_vmf(bias_direction, concentration, n_points)

    # Random radial distance (uniform within sphere)
    radii = sphere_radius * np.cbrt(np.random.random(n_points))

    # Combine directions and radii
    return directions * radii[:, np.newaxis]


def a_star_ish(
    start: np.ndarray,
    finish: np.ndarray,
    edge_cost: Callable,
    max_cost: int = 4000,
    callback: Callable = None,
) -> List[np.ndarray]:
    """Find a path between *start* and *finish*. Return the path or raise a ValueError.

    Parameters
    ----------
    start : np.ndarray
        Initial position.
    finish : np.ndarray
        Final position.
    edge_cost : Callable
        Function that takes two points and returns the cost of moving between them.
        If the cost is np.inf, the edge is treated as impossible.
    max_cost : int
        Maximum number of iterations before giving up.
    callback : Callable
        Used for debugging and visualization. Called with the current path at each iteration.

    Returns
    -------
    List[np.ndarray]
        The path from start to finish.

    Raises
    ------
    ValueError
        If pathfinding fails or exceeds max cost.
    """

    def heuristic(x, y):
        return np.linalg.norm(y - x)

    radius = np.linalg.norm(finish - start) / 5
    radius = max(radius, 100e-6)
    concentration_max = np.log(max_cost + 1)
    count = 10

    def neighbors(pt, cost_so_far):
        yield (radius * (finish - pt) / np.linalg.norm(finish - pt)) + pt
        cost_scale = np.log(1 + cost_so_far)
        concentration = max(0.2, concentration_max - (1.0 * cost_scale))
        points = generate_biased_sphere_points(
            count, radius**cost_scale, finish - pt, concentration
        )
        yield from (points + pt)
        yield finish

    open_set = {tuple(start): start}
    came_from = {}
    g_score = {tuple(start): 0}
    f_score = {tuple(start): heuristic(start, finish)}
    cost = 0

    while open_set:
        curr_key = min(open_set, key=lambda x: f_score[x])
        current = open_set.pop(curr_key)
        if np.all(current == finish):
            return reconstruct_path(came_from, curr_key)

        for neighbor in neighbors(current, cost):
            print(f"cost {cost}, neighbor {neighbor}")
            cost += 1
            if cost > max_cost:
                raise ValueError(f"Pathfinding exceeded maximum cost of {max_cost}")
            neigh_key = tuple(neighbor)
            this_cost = edge_cost(current, neighbor)
            tentative_g_score = g_score[curr_key] + this_cost
            if (
                neigh_key not in g_score
                or tentative_g_score < g_score[neigh_key]
                or np.all(neighbor == finish)
            ):
                came_from[neigh_key] = curr_key
                g_score[neigh_key] = tentative_g_score
                f_score[neigh_key] = tentative_g_score + 2 * heuristic(neighbor, finish)
                if f_score[neigh_key] < np.inf and neigh_key not in open_set:
                    open_set[neigh_key] = neighbor
            if callback is not None:
                callback(reconstruct_path(came_from, neigh_key)[::-1])

    raise ValueError("Pathfinding failed; no valid paths found.")


def simplify_path(path, edge_cost: Callable, viz_callback: Callable | None = None):
    """Simplify the given path by iteratively removing unnecessary waypoints."""
    path = list(path)
    made_change = True
    while made_change:
        made_change = False
        ptr = 0
        while ptr < len(path) - 2:
            if edge_cost(np.array(path[ptr]), np.array(path[ptr + 2])) < np.inf:
                path.pop(ptr + 1)
                made_change = True
            ptr += 1
    return path


class RRTNode:
    """Node in an RRT tree."""

    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def path_to_root(self):
        """Return the path from this node to the root."""
        path = [self.position]
        node = self
        while node.parent is not None:
            node = node.parent
            path.append(node.position)
        return path[::-1]


def rrt_connect(
    start: np.ndarray,
    finish: np.ndarray,
    edge_cost: Callable,
    max_iterations: int = 2000,
    step_size: float = None,
    goal_sample_rate: float = 0.1,
    callback: Callable = None,
) -> List[np.ndarray]:
    """Find a path between *start* and *finish* using bidirectional RRT-Connect.

    Parameters
    ----------
    start : np.ndarray
        Initial position.
    finish : np.ndarray
        Final position.
    edge_cost : Callable
        Function that takes two points and returns the cost of moving between them.
        If the cost is np.inf, the edge is treated as impossible.
    max_iterations : int
        Maximum number of iterations before giving up.
    step_size : float
        Maximum distance to extend a branch. If None, calculated based on start-finish distance.
    goal_sample_rate : float
        Probability of sampling the goal position directly.
    callback : Callable
        Used for debugging and visualization. Called with the current path at each iteration.

    Returns
    -------
    List[np.ndarray]
        The path from start to finish.

    Raises
    ------
    ValueError
        If no path is found after maximum iterations.
    """
    # Calculate step size if not provided
    if step_size is None:
        step_size = np.linalg.norm(finish - start) / 10
        step_size = max(step_size, 100e-6)  # Minimum step size

    # Initialize trees
    start_tree = {tuple(start): RRTNode(start)}
    goal_tree = {tuple(finish): RRTNode(finish)}

    # For alternating between trees
    trees = [start_tree, goal_tree]
    goals = [finish, start]

    # KD-trees for efficient nearest neighbor search
    from scipy.spatial import cKDTree

    for i in range(max_iterations):
        # Alternate between trees
        tree_idx = i % 2
        active_tree = trees[tree_idx]
        goal = goals[tree_idx]
        other_tree = trees[1 - tree_idx]

        # Sample random point (with bias toward goal)
        if np.random.random() < goal_sample_rate:
            random_point = goal
        else:
            # Sample with bias toward goal
            direction = goal - list(active_tree.values())[0].position
            distance = np.linalg.norm(direction)
            random_point = (
                generate_biased_sphere_points(1, distance * 1.5, direction, concentration=0.5)[0]
                + list(active_tree.values())[0].position
            )

        # Find nearest node in active tree
        positions = np.array([node.position for node in active_tree.values()])
        kdtree = cKDTree(positions)
        _, idx = kdtree.query(random_point)
        nearest_node = list(active_tree.values())[idx]

        # Extend tree toward random point
        direction = random_point - nearest_node.position
        distance = np.linalg.norm(direction)
        if distance > 0:
            direction = direction / distance
            new_position = nearest_node.position + min(step_size, distance) * direction

            # Check if the new edge is valid
            if edge_cost(nearest_node.position, new_position) < np.inf:
                # Add new node to tree
                new_node = RRTNode(new_position, nearest_node)
                nearest_node.add_child(new_node)
                active_tree[tuple(new_position)] = new_node

                # Check if we can connect to the other tree
                positions = np.array([node.position for node in other_tree.values()])
                if len(positions) > 0:
                    kdtree = cKDTree(positions)

                    # Handle both single and multiple nearest neighbor cases
                    k_neighbors = min(3, len(positions))
                    query_result = kdtree.query(new_position, k=k_neighbors)

                    # Unpack query results based on k value
                    if k_neighbors == 1:
                        distances = [query_result[0]]
                        indices = [query_result[1]]
                    else:
                        distances, indices = query_result

                    # Try to connect to closest nodes in other tree
                    for j in range(len(indices)):
                        dist = distances[j]
                        idx = indices[j]

                        if dist < step_size * 1.5:  # Only try to connect if reasonably close
                            connect_node = list(other_tree.values())[idx]
                            if edge_cost(new_position, connect_node.position) < np.inf:
                                # Found a path!
                                if tree_idx == 0:
                                    # Start tree to goal tree
                                    path = (
                                        new_node.path_to_root() + connect_node.path_to_root()[::-1]
                                    )
                                else:
                                    # Goal tree to start tree
                                    path = (
                                        connect_node.path_to_root() + new_node.path_to_root()[::-1]
                                    )

                                # Simplify the path
                                return simplify_path(path, edge_cost, callback)

                # Visualization callback
                if (
                    callback is not None and i < 10 or i % 10 == 0
                ):  # Reduce callback frequency for performance
                    # Find best connection between trees for visualization
                    best_start = None
                    best_goal = None
                    best_dist = float("inf")

                    # Sample a few nodes from each tree to check connections
                    start_samples = list(active_tree.values())
                    if len(start_samples) > 10:
                        # Use a list to avoid numpy random choice issues with custom objects
                        indices = np.random.choice(len(start_samples), 10, replace=False)
                        start_samples = [start_samples[idx] for idx in indices]

                    goal_samples = list(other_tree.values())
                    if len(goal_samples) > 10:
                        indices = np.random.choice(len(goal_samples), 10, replace=False)
                        goal_samples = [goal_samples[idx] for idx in indices]

                    for s_node in start_samples:
                        for g_node in goal_samples:
                            dist = np.linalg.norm(s_node.position - g_node.position)
                            if (
                                dist < best_dist
                                and edge_cost(s_node.position, g_node.position) < np.inf
                            ):
                                best_dist = dist
                                best_start = s_node
                                best_goal = g_node

                    if best_start is not None:
                        if tree_idx == 0:
                            vis_path = best_start.path_to_root() + best_goal.path_to_root()[::-1]
                        else:
                            vis_path = best_goal.path_to_root() + best_start.path_to_root()[::-1]
                        if callback:
                            callback(vis_path)

    raise ValueError("Pathfinding failed; no valid paths found after maximum iterations.")


def simplify_path_dp(path, edge_cost: Callable, viz_callback: Callable | None = None):
    """Simplify path using Douglas-Peucker-inspired algorithm for smoother paths."""
    if len(path) <= 3:
        return path

    # Douglas-Peucker-inspired algorithm for smoother paths
    result = [path[0]]
    i = 0
    while i < len(path) - 1:
        # Try to extend as far as possible
        for j in range(len(path) - 1, i, -1):
            if edge_cost(np.array(path[i]), np.array(path[j])) < np.inf:
                if j > i + 1:  # Skip intermediate points
                    result.append(path[j])
                    i = j
                else:
                    i += 1
                break
        else:
            # If no skip was possible, keep the next point
            i += 1
            if i < len(path):
                result.append(path[i])

    # Ensure the last point is included
    if np.any(result[-1] != path[-1]):
        result.append(path[-1])

    return result
