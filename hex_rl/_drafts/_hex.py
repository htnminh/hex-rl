print(
r"""
    0   1   2   3   4

    ---------------------
0    \ X   X   .   O   . \
      \                   \
  1    \ .   X   X   O   . \
        \                   \
    2    \ X   O   O   O   . \
          \                   \
      3    \ X   .   .   .   . \
            \                   \
        4    \ .   .   .   .   . \
              ---------------------
""")

a = 15
print(f"{a:5d}")

l = [
    {(1, 1)}, {(0, 1)}
    ]
l.remove({(0, 1)})
print(l)

print((0,0) in {(0,0)})