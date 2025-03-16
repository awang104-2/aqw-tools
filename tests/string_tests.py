def string_split_test():
    string = '42342:1,23232:2'
    parts = string.split(',')
    for part in parts:
        num, q = part.split(':')
        print(num, q)

