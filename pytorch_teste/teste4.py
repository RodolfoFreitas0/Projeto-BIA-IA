import torch

a = torch.tensor([1, 2, 3])
b = torch.tensor([[1, 2], [3, 4]])

print(f"a: {a}")
print(f"b: {b}")

x = torch.tensor([1., 2., 3.])
y = torch.tensor([4., 5., 6.])

print(f"x + y: {x + y}")
print(f"x * y: {x * y}")
print(f"torch.dot(x, y): {torch.dot(x, y)}")

A = torch.tensor([[1., 2.],
                  [3., 4.]])
B = torch.tensor([[5., 6.],
                  [7., 8.]])

"""
C[0][0] = (1 * 5) + (2 * 7) = 5 + 14 = 19
C[0][1] = (1 * 6) + (2 * 8) = 6 + 16 = 22
C[1][0] = (3 * 5) + (4 * 7) = 15 + 28 = 43
C[1][1] = (3 * 6) + (4 * 8) = 18 + 32 = 50

Resultado:
[[19, 22],
 [43, 50]]
"""

C = torch.matmul(A, B)
print(f"C: {C}")