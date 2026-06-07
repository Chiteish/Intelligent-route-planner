from typing import Dict, List, Tuple, Any

class MinHeap:
    """
    A custom Binary Min-Heap (Priority Queue) implementation.
    Includes a position map (hash map) to track the index of each key in the heap.
    This enables O(1) lookup and O(log N) Decrease-Key operations, which is
    essential for optimizing Dijkstra's and A* search algorithms.
    """
    def __init__(self):
        # The heap stores elements as [key, priority] lists.
        # Example: self.heap = [['A', 0.0], ['B', 5.2]]
        self.heap: List[List[Any]] = []
        
        # Position map: key -> index in self.heap
        # Example: self.pos = {'A': 0, 'B': 1}
        self.pos: Dict[Any, int] = {}

    def is_empty(self) -> bool:
        """Returns True if the priority queue is empty."""
        return len(self.heap) == 0

    def contains(self, key: Any) -> bool:
        """Returns True if the key is currently in the heap."""
        return key in self.pos

    def _swap(self, i: int, j: int):
        """Swaps two elements in the heap array and updates their position mapping."""
        # Swap position indices in lookup dictionary
        key_i, key_j = self.heap[i][0], self.heap[j][0]
        self.pos[key_i] = j
        self.pos[key_j] = i
        
        # Swap actual elements in the heap array
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def _bubble_up(self, index: int):
        """Bubbles an element up the tree if its priority is less than its parent's."""
        while index > 0:
            parent = (index - 1) // 2
            # Compare priorities: if child is smaller than parent, swap
            if self.heap[index][1] < self.heap[parent][1]:
                self._swap(index, parent)
                index = parent
            else:
                break

    def _bubble_down(self, index: int):
        """Bubbles an element down the tree to maintain the min-heap invariant."""
        n = len(self.heap)
        while 2 * index + 1 < n:
            left_child = 2 * index + 1
            right_child = 2 * index + 2
            smallest = left_child

            # Find the smallest of the two children
            if right_child < n and self.heap[right_child][1] < self.heap[left_child][1]:
                smallest = right_child

            # If the smallest child is smaller than the parent, swap
            if self.heap[smallest][1] < self.heap[index][1]:
                self._swap(index, smallest)
                index = smallest
            else:
                break

    def push(self, key: Any, priority: float):
        """Inserts a new key-priority pair into the heap."""
        if key in self.pos:
            # If key already exists, update its priority (decrease key)
            self.decrease_key(key, priority)
            return

        # Add to the end of the heap array
        self.heap.append([key, priority])
        index = len(self.heap) - 1
        self.pos[key] = index
        
        # Restore heap invariant
        self._bubble_up(index)

    def pop(self) -> Tuple[Any, float]:
        """
        Extracts and returns the element with the minimum priority (min-heap root).
        Returns a tuple: (key, priority).
        """
        if self.is_empty():
            raise IndexError("Pop from an empty priority queue")

        # The root contains the minimum value
        root_key, root_priority = self.heap[0]

        # If only one element left, just pop it
        if len(self.heap) == 1:
            self.heap.pop()
            del self.pos[root_key]
            return root_key, root_priority

        # Move the last element to the root
        last_key, last_priority = self.heap.pop()
        self.heap[0] = [last_key, last_priority]
        self.pos[last_key] = 0
        del self.pos[root_key]

        # Bubble down the new root to restore heap invariant
        self._bubble_down(0)
        return root_key, root_priority

    def decrease_key(self, key: Any, new_priority: float):
        """
        Decreases the priority of an existing key to a smaller value.
        Throws ValueError if key is not found or new priority is greater.
        """
        if key not in self.pos:
            raise ValueError(f"Key '{key}' not found in the priority queue.")

        index = self.pos[key]
        old_priority = self.heap[index][1]

        if new_priority > old_priority:
            # Heap keys can only decrease in value for Dijkstra / A*
            return

        # Update priority value
        self.heap[index][1] = new_priority
        
        # Bubble up since value is smaller now
        self._bubble_up(index)
