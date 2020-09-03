import numpy as np

sample = [
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0]
]
first = [
    [1,0,0,0,0],
    [0,0,1,0,1],
    [0,0,1,0,1],
    [0,0,1,0,1],
    [0,0,1,0,1]
]

second = [
    [0,0,0,0,1],
    [0,0,0,0,3],
    [0,0,0,0,4],
    [0,2,0,0,2],
    [4,5,0,2,0]
]


answer = np.rot90(second, 1) + np.array(first)

# for k in range(5):
#     print(chr(int(''.join([str(i) for i in answer[k]]),8)))

for i in range(len(second)):
    for j in range(len(second[0])):
        sample[i][j] += first [i][j]

print(sample)
