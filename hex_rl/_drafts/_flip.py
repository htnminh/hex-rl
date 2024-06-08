import numpy as np

def flip_anti_diagonal(arr):    
    return np.rot90(np.transpose(arr), k=2)

arr = np.array([[1, 2, 3, 4, 5],
                [6, 7, 8, 9, 10], 
                [11, 12, 13, 14, 15], 
                [16, 17, 18, 19, 20], 
                [21, 22, 23, 24, 25]])

print(arr)
print()
print(flip_anti_diagonal(arr))


print(np.flip([1, 2, 3, 4, 5]))