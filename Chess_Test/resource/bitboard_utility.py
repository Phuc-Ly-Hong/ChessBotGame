def count_bits(bb):
    return bin(bb).count('1')

def pop_lsb(bb):
    """Pop and return index of least significant bit."""
    if bb == 0:
        return -1, 0
    lsb = bb & -bb
    index = (lsb).bit_length() - 1
    bb ^= lsb
    return index, bb

def get_bit(bb, index):
    return (bb >> index) & 1

def set_bit(bb, index):
    return bb | (1 << index)

def clear_bit(bb, index):
    return bb & ~(1 << index)

def shift_north(bb): return (bb << 8) & 0xFFFFFFFFFFFFFFFF
def shift_south(bb): return (bb >> 8) & 0xFFFFFFFFFFFFFFFF
def shift_east(bb):  return (bb << 1) & 0xfefefefefefefefe
def shift_west(bb):  return (bb >> 1) & 0x7f7f7f7f7f7f7f7f
def shift_northwest(bb):
    return (bb << 7) & 0x7f7f7f7f7f7f7f00

def shift_northeast(bb):
    return (bb << 9) & 0xfefefefefefefe00

def shift_southwest(bb):
    return (bb >> 9) & 0x007f7f7f7f7f7f7f

def shift_southeast(bb):
    return (bb >> 7) & 0x00fefefefefefefe
