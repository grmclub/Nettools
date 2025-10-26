## 1. Adding Elements

**Purpose:** To insert new items into a list.

**Methods:**

*   `append()` – Adds a single element to the end of the list.
    
*   `extend()` – Adds multiple elements (from another list or iterable).
    
*   `insert()` – Inserts an element at a specific index.
    

**Example:**

numbers = \[1, 2, 3\]
numbers.append(4)       # \[1, 2, 3, 4\]
numbers.extend(\[5, 6\])  # \[1, 2, 3, 4, 5, 6\]
numbers.insert(0, 0)    # \[0, 1, 2, 3, 4, 5, 6\]

## 2. Removing Elements

**Purpose:** To delete one or more elements from a list.

**Methods:**

*   `remove()` – Deletes the first matching value.
    
*   `pop()` – Removes and returns an element by index (default is last).
    
*   `clear()` – Removes all elements from the list.
    

**Example:**

numbers = \[1, 2, 3, 4\]
numbers.remove(2)   # \[1, 3, 4\]
numbers.pop()       # \[1, 3\]
numbers.clear()     # \[\]

## 3. Searching and Counting

**Purpose:** To locate or count specific values.

**Methods:**

*   `index()` – Returns the position of the first matching value.
    
*   `count()` – Counts how many times a value appears in the list.
    

**Example:**

fruits = \["apple", "banana", "apple", "cherry"\]
fruits.index("banana")  # 1
fruits.count("apple")   # 2

## 4. Ordering and Rearranging

**Purpose:** To change how items are arranged.

**Methods:**

*   `sort()` – Sorts the list in ascending (or descending) order.
    
*   `reverse()` – Reverses the order of elements.
    

**Example:**

nums = \[5, 2, 9, 1\]
nums.sort()      # \[1, 2, 5, 9\]
nums.reverse()   # \[9, 5, 2, 1\]

## 5. Copying Lists

**Purpose:** To duplicate a list safely.

**Method:**

*   `copy()` – Creates a shallow copy of the list.
    

**Example:**

original = \[1, 2, 3\]
duplicate = original.copy()
print(duplicate)  # \[1, 2, 3\]