mat = [[1, 5, 9], [14, 20, 21], [30, 34, 43]]

x = input("a number please: ")
value = False

for i in mat:
    for j in i:
        if int(x) == j:
            value = True
            break


print(value)
            