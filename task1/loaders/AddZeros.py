# Add zeros (and plus 1) before num to match Semlink sentence with Deepbank Filename
def add_zeros(num):
    s = str(int(num) + 1)
    return "0" * (3 - len(s)) + s
