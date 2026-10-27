def _visit_range(start, stop, action):
    if start >= stop:
        return
    if stop - start == 1:
        action(start)
        return
    middle = (start + stop) // 2
    _visit_range(start, middle, action)
    _visit_range(middle, stop, action)


def _repeat_until(count, step):
    if count == 0:
        return False
    if count == 1:
        return step()
    middle = count // 2
    if _repeat_until(middle, step):
        return True
    return _repeat_until(count - middle, step)


def _run_until_done(step, block_size=1):
    if _repeat_until(block_size, step):
        return
    _run_until_done(step, block_size * 2)


class _QueueNode:
    def __init__(self, value):
        self.value = value
        self.next = None


class _Queue:
    def __init__(self):
        self._head = None
        self._tail = None
        self._size = 0

    def push(self, value):
        node = _QueueNode(value)
        if self._tail is None:
            self._head = node
        else:
            self._tail.next = node
        self._tail = node
        self._size += 1

    def pop(self):
        node = self._head
        self._head = node.next
        self._size -= 1
        if self._head is None:
            self._tail = None
        return node.value

    def peek(self):
        return self._head.value

    def size(self):
        return self._size

    def empty(self):
        return self._size == 0


# 1. Індекс першого унікального символу
def first_unique_char(s):
    frequencies = [0] * 26
    first_index = -1
    alphabet_start = ord("a")

    def count(index):
        frequencies[ord(s[index]) - alphabet_start] += 1

    def find(index):
        nonlocal first_index
        if first_index == -1 and frequencies[ord(s[index]) - alphabet_start] == 1:
            first_index = index

    _visit_range(0, len(s), count)
    _visit_range(0, len(s), find)
    return first_index


# 2. Стек на двох чергах
class MyStack:
    def __init__(self):
        self._main = _Queue()
        self._spare = _Queue()

    def push(self, x):
        self._spare.push(x)

        def transfer_one(_):
            self._spare.push(self._main.pop())

        _visit_range(0, self._main.size(), transfer_one)
        self._main, self._spare = self._spare, self._main

    def pop(self):
        return self._main.pop()

    def top(self):
        return self._main.peek()

    def empty(self):
        return self._main.empty()


# 3. Кількість запитів у включному проміжку [t - 3000, t]
class RecentCounter:
    def __init__(self):
        self._requests = _Queue()

    def ping(self, t):
        self._requests.push(t)
        oldest_allowed = t - 3000

        def remove_expired():
            if self._requests.empty() or self._requests.peek() >= oldest_allowed:
                return True
            self._requests.pop()
            return False

        _run_until_done(remove_expired)
        return self._requests.size()


# 4. Циклічна двостороння черга (другий номер 3 в умові)
class MyCircularDeque:
    def __init__(self, k):
        self._data = [None] * k
        self._capacity = k
        self._front = 0
        self._size = 0

    def insertFront(self, value):
        if self.isFull():
            return False
        self._front = (self._front - 1) % self._capacity
        self._data[self._front] = value
        self._size += 1
        return True

    def insertLast(self, value):
        if self.isFull():
            return False
        index = (self._front + self._size) % self._capacity
        self._data[index] = value
        self._size += 1
        return True

    def deleteFront(self):
        if self.isEmpty():
            return False
        self._data[self._front] = None
        self._front = (self._front + 1) % self._capacity
        self._size -= 1
        return True

    def deleteLast(self):
        if self.isEmpty():
            return False
        index = (self._front + self._size - 1) % self._capacity
        self._data[index] = None
        self._size -= 1
        return True

    def getFront(self):
        if self.isEmpty():
            return -1
        return self._data[self._front]

    def getRear(self):
        if self.isEmpty():
            return -1
        index = (self._front + self._size - 1) % self._capacity
        return self._data[index]

    def isEmpty(self):
        return self._size == 0

    def isFull(self):
        return self._size == self._capacity


# 5. Циклічна FIFO-черга (номер 4 в умові)
class MyCircularQueue:
    def __init__(self, k):
        self._buffer = MyCircularDeque(k)

    def Front(self):
        return self._buffer.getFront()

    def Rear(self):
        return self._buffer.getRear()

    def enQueue(self, value):
        return self._buffer.insertLast(value)

    def deQueue(self):
        return self._buffer.deleteFront()

    def isEmpty(self):
        return self._buffer.isEmpty()

    def isFull(self):
        return self._buffer.isFull()


# 6. Послідовність штампувань (номер 5 в умові)
def moves_to_stamp(stamp, target):
    size = len(target)
    width = len(stamp)
    window_count = size - width + 1
    pending = [0] * window_count
    dependents = [None] * size
    erased = [False] * size
    ready = _Queue()
    backwards_moves = []
    erased_count = 0

    def initialize(index):
        dependents[index] = []

    _visit_range(0, size, initialize)

    def inspect_window(start):
        def compare(offset):
            position = start + offset
            if target[position] != stamp[offset]:
                pending[start] += 1
                dependents[position].append(start)

        _visit_range(0, width, compare)
        if pending[start] == 0:
            ready.push(start)

    _visit_range(0, window_count, inspect_window)

    def erase_window():
        if ready.empty():
            return True
        start = ready.pop()
        changed = False

        def erase(position):
            nonlocal erased_count, changed
            if erased[position]:
                return
            erased[position] = True
            erased_count += 1
            changed = True
            listeners = dependents[position]

            def release(index):
                window = listeners[index]
                pending[window] -= 1
                if pending[window] == 0:
                    ready.push(window)

            _visit_range(0, len(listeners), release)

        _visit_range(start, start + width, erase)
        if changed:
            backwards_moves.append(start)
        return False

    _run_until_done(erase_window)
    if erased_count != size:
        return []

    moves = [0] * len(backwards_moves)

    def reverse_order(index):
        moves[index] = backwards_moves[len(backwards_moves) - 1 - index]

    _visit_range(0, len(moves), reverse_order)
    return moves


class _MonotonicQueue:
    def __init__(self, capacity):
        self._items = MyCircularDeque(capacity)

    def discard_before(self, first_index):
        def discard_one():
            if self._items.isEmpty() or self._items.getFront()[0] >= first_index:
                return True
            self._items.deleteFront()
            return False

        _run_until_done(discard_one)

    def push(self, index, value):
        def discard_weaker():
            if self._items.isEmpty() or self._items.getRear()[1] > value:
                return True
            self._items.deleteLast()
            return False

        _run_until_done(discard_weaker)
        self._items.insertLast((index, value))

    def maximum(self):
        return self._items.getFront()[1]

    def empty(self):
        return self._items.isEmpty()


# 7. Максимум ковзного вікна (номер 6 в умові)
def max_sliding_window(nums, k):
    candidates = _MonotonicQueue(k)
    result = []

    def inspect(index):
        candidates.discard_before(index - k + 1)
        candidates.push(index, nums[index])
        if index >= k - 1:
            result.append(candidates.maximum())

    _visit_range(0, len(nums), inspect)
    return result


# 8. Обмежена сума підпослідовності (номер 7 в умові)
def constrained_subset_sum(nums, k):
    candidates = _MonotonicQueue(k + 1)
    best = nums[0]

    def inspect(index):
        nonlocal best
        candidates.discard_before(index - k)
        current = nums[index]
        if not candidates.empty():
            current += candidates.maximum()
        if current > best:
            best = current
        if current > 0:
            candidates.push(index, current)

    _visit_range(0, len(nums), inspect)
    return best


if __name__ == "__main__":
    print("1. Перший унікальний символ:")
    print(first_unique_char("leopard"))
    print(first_unique_char("loveleopard"))
    print(first_unique_char("aabb"))

    print("\n2. Стек на двох чергах:")
    stack = MyStack()
    print([None, stack.push(1), stack.push(2), stack.top(), stack.pop(), stack.empty()])

    print("\n3. Кількість останніх викликів:")
    counter = RecentCounter()
    print([None, counter.ping(1), counter.ping(100), counter.ping(3001), counter.ping(3002)])

    print("\n4. Циклічна двостороння черга:")
    circular_deque = MyCircularDeque(3)
    print([
        None,
        circular_deque.insertLast(1),
        circular_deque.insertLast(2),
        circular_deque.insertFront(3),
        circular_deque.insertFront(4),
        circular_deque.getRear(),
        circular_deque.isFull(),
        circular_deque.deleteLast(),
        circular_deque.insertFront(4),
        circular_deque.getFront(),
    ])

    print("\n5. Циклічна черга:")
    circular_queue = MyCircularQueue(3)
    print([
        None,
        circular_queue.enQueue(1),
        circular_queue.enQueue(2),
        circular_queue.enQueue(3),
        circular_queue.enQueue(4),
        circular_queue.Rear(),
        circular_queue.isFull(),
        circular_queue.deQueue(),
        circular_queue.enQueue(4),
        circular_queue.Rear(),
    ])

    print("\n6. Послідовність штампувань:")
    print(moves_to_stamp("abc", "ababc"))
    print(moves_to_stamp("abca", "aabcaca"))

    print("\n7. Максимум ковзного вікна:")
    print(max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3))
    print(max_sliding_window([1], 1))

    print("\n8. Обмежена сума підпослідовності:")
    print(constrained_subset_sum([10, 2, -10, 5, 20], 2))
    print(constrained_subset_sum([-1, -2, -3], 1))
    print(constrained_subset_sum([10, -2, -10, -5, 20], 2))
