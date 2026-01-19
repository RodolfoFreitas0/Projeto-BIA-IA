import torch

def linha():
    print()
    print("#--------------------------------------#")
    print()

linha()

one_to_ten = torch.arange(1, 11, 1)
print("one_to_ten")
print(one_to_ten)

linha()

ten_zeros = torch.zeros_like(one_to_ten)
print("ten_zeros")
print(ten_zeros)

linha()

print("Tensor Datatypes")

linha()

float_32_tensor = torch.tensor([3.0, 6.0, 9.0],
                               dtype=None,
                               device=None,
                               requires_grad=False)
print("float_32_tensor")
print(float_32_tensor)
print(f"type: {float_32_tensor.dtype}")

linha()

float_16_tensor = torch.tensor([3.0, 6.0, 9.0],
                               dtype=torch.float16,
                               device=None,
                               requires_grad=False)
print("float_16_tensor")
print(float_16_tensor)
print(f"type: {float_16_tensor.dtype}")

linha()

print("Tensor Datatype Conversion")

linha()

float_16_tensor_converted = float_32_tensor.type(torch.float16)
print("float_16_tensor_converted = float_32_tensor.type(torch.float16)")
print("float_16_tensor_converted")
print(float_16_tensor_converted)
print(f"type: {float_16_tensor_converted.dtype}")

linha()

print("Tensor Atributes")

linha()

some_tensor = torch.rand(3, 4)
print(some_tensor)
print()
print(f"Datatype: {some_tensor.dtype}")
print(f"Shape: {some_tensor.shape}")
print(f"Device: {some_tensor.device}")

linha()

print("Tensor Operations")

linha()

tensor = torch.tensor([1, 2, 3])
print(f"tensor original: {tensor}")
print()

tensor = tensor + 10
print(f"tensor + 10: {tensor}")
print("Também pode usar torch.add(tensor, 10)")
print()

tensor = torch.tensor([1, 2, 3])
tensor = tensor * 10
print(f"tensor * 10: {tensor}")
print("Também pode usar torch.mul(tensor, 10)")
print()

tensor = torch.tensor([1, 2, 3])
tensor = tensor - 10
print(f"tensor - 10: {tensor}")
print(f"também pode usar torch.sub(tensor, 10)")

linha()

print("Matrix Multiplication")

print(f"Regras\n" \
f"1. As dimensões internas devem ser iguais\n" \
f"(3, 2) @ (3, 2) nao funciona\n" \
f"(2, 3) @ (3, 2) funciona\n" \
f"(3, 2) @ (2, 3) funciona\n" \
f"2. O formato resultante é igual as dimensões externas\n" \
f"(2, 3) @ (3, 2) -> (2, 2) (em relação ao formato da matriz)\n" \
f"(3, 2) @ (2, 3) -> (3, 3)"
)

linha()

tensor_mm = torch.tensor([1, 2, 3])

print(tensor_mm)
print()

print(torch.matmul(tensor_mm, tensor_mm))
print()
# OU
print(tensor_mm @ tensor_mm)
print()

linha()

print("Matrix Transpose")

linha()

tensor_B = torch.tensor([[1, 2],
                         [3, 4],
                         [5, 6]])
print("Tensor Original")
print(tensor_B)
print()

print("Tensor Transposto")
print(tensor_B.T)
print()