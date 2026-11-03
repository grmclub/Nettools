
## 1\. Transform / Modify (Return a changed version)

*   `capitalize()` → First letter uppercase, rest lowercase
    
*   `casefold()` → Aggressive lowercase (for comparisons)
    
*   `lower()` → All lowercase
    
*   `upper()` → All uppercase
    
*   `title()` → Each word starts with uppercase
    
*   `swapcase()` → Swap case (upper ↔ lower)
    
*   `replace(old, new)` → Replace substring with another
    
*   `removeprefix(prefix)` → Remove prefix if present
    
*   `removesuffix(suffix)` → Remove suffix if present
    
*   `strip()` → Remove whitespace (both sides)
    
*   `lstrip()` → Remove whitespace (left side)
    
*   `rstrip()` → Remove whitespace (right side)
    
*   `expandtabs(tabsize)` → Replace `\t` with spaces
    
*   `translate(map)` → Character-by-character replacement (via `str.maketrans`)
    

## 2\. Search / Find (Locate substrings)

*   `find(sub)` → First index of substring (or `-1` if not found)
    
*   `rfind(sub)` → Last index of substring (or `-1`)
    
*   `index(sub)` → Like `find()`, but raises error if not found
    
*   `rindex(sub)` → Like `rfind()`, but raises error
    
*   `count(sub)` → Count occurrences
    
*   `startswith(prefix)` → Check beginning
    
*   `endswith(suffix)` → Check ending
    

## 3\. Validation / Test (Return True/False)

*   `isalnum()` → Only alphanumeric?
    
*   `isalpha()` → Only letters?
    

*   `isascii()` → Only ASCII characters?
    
*   `isdecimal()` → Decimal digits only?
    
*   `isdigit()` → Digits only (includes superscripts, etc.)
    
*   `isnumeric()` → Numeric only (includes fractions, Roman numerals, etc.)
    
*   `isidentifier()` → Valid Python identifier?
    
*   `islower()` → All lowercase?
    
*   `isupper()` → All uppercase?
    
*   `istitle()` → Title case?
    
*   `isspace()` → Whitespace only?
    
*   `isprintable()` → Printable characters only?
    

## 4\. Format / Align (Make text pretty)

*   `center(width, fill)` → Center with padding
    
*   `ljust(width, fill)` → Left align with padding
    
*   `rjust(width, fill)` → Right align with padding
    
*   `zfill(width)` → Pad with zeros
    
*   `format(*args, **kwargs)` → Advanced string formatting
    
*   `format_map(mapping)` → Like `format()`, but takes dict directly
    

## 5\. Split / Join

*   `split(sep)` → Split into list (from left)
    
*   `rsplit(sep)` → Split into list (from right)
    
*   `splitlines()` → Split by line breaks
    
*   `partition(sep)` → Split into 3 parts: before, sep, after
    
*   `rpartition(sep)` → Like partition, but from right
    
*   `join(iterable)` → Join iterable into a single string
    

## 6\. Encode / Convert

*   `encode(encoding)` → Convert string → bytes (UTF-8 default)
    
*   `maketrans()` → Create translation table (used with `translate()`)