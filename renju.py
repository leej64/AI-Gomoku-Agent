EMPTY = 0

class Renju(object):
    def __init__(self, board, board_size = 15):
        self.board = board
        self.board_size = board_size

    def is_invalid(self, x, y):
        return (x < 0 or x >= self.board_size or y < 0 or y >= self.board_size)

    def play_stone(self, x, y, stone):
        self.board[y][x] = stone

    def get_adjacent(self, direction):
        list_dx = [-1, 1, -1, 1, 0, 0, 1, -1]
        list_dy = [0, 0, -1, 1, -1, 1, -1, 1]
        return list_dx[direction], list_dy[direction]

    def get_adj_stone_count(self, x, y, stone, direction):
        x_, y_ = x, y
        cnt = 1
        for i in range(2):
            dx, dy = self.get_adjacent(direction * 2 + i)
            x, y = x_, y_
            while True:
                x, y = x + dx, y + dy
                if self.is_invalid(x, y) or self.board[y][x] != stone:
                    break
                else:
                    cnt += 1
        return cnt

    def is_gameover(self, x, y, stone):
        for i in range(4):
            cnt = self.get_adj_stone_count(x, y, stone, i)
            if cnt >= 5:
                return True
        return False

    def is_jangmok(self, x, y, stone):
        for i in range(4):
            cnt = self.get_adj_stone_count(x, y, stone, i)
            if cnt > 5:
                return True
        return False

    def is_five(self, x, y, stone):
        for i in range(4):
            cnt = self.get_adj_stone_count(x, y, stone, i)
            if cnt == 5:
                return True
        return False

    def find_empty_adj(self, x, y, stone, direction):
        dx, dy = self.get_adjacent(direction)
        while True:
            x, y = x + dx, y + dy
            if self.is_invalid(x, y) or self.board[y][x] != stone:
                break
        if not self.is_invalid(x, y) and self.board[y][x] == EMPTY:
            return x, y
        else:
            return None

    def is_four_dir(self, x, y, stone, direction):
        for i in range(2):
            pt = self.find_empty_adj(x, y, stone, direction * 2 + 1)
            if pt:
                if self.is_five_dir(pt[0], pt[1], stone, direction):
                    return True
        return False

    def is_five_dir(self, x, y, stone, direction):
        if self.get_adj_stone_count(x, y, stone, direction) == 5:
            return True
        return False

    def forbidden(self, x, y, stone):
        if self.is_five(x, y, stone):
            return False
        elif self.is_jangmok(x, y, stone):
            return True
        elif self.ssang_sam(x, y, stone) or self.ssang_sa(x, y, stone):
            return True
        return False

    def get_forbidden(self, stone):
        pt = []
        for y in range(len(self.board)):
            for x in range(len(self.board[0])):
                if self.board[y][x]:
                    continue
                if self.forbidden(x, y, stone):
                    pt.append((x, y))
        return [(y, x) for x, y in pt]

    def open_four(self, x, y, stone, direction):
        if self.is_five(x, y, stone):
            return False
        cnt = 0
        for i in range(2):
            pt = self.find_empty_adj(x, y, stone, direction * 2 + i)
            if pt:
                if self.is_five_dir(pt[0], pt[1], stone, direction):
                    cnt += 1
        if cnt == 2:
            if self.get_adj_stone_count(x, y, stone, direction) == 4:
                cnt = 1
        else:
            cnt = 0
        return cnt

    def open_three(self, x, y, stone, direction):
        for i in range(2):
            pt = self.find_empty_adj(x, y, stone, direction * 2 + i)
            if pt:
                dx, dy = pt
                self.play_stone(dx, dy, stone)
                if self.open_four(dx, dy, stone, direction) == 1:
                    if not self.forbidden(dx, dy, stone):
                        self.play_stone(dx, dy, EMPTY)
                        return True
                self.play_stone(dx, dy, EMPTY)
        return False

    def ssang_sam(self, x, y, stone):
        cnt = 0
        self.play_stone(x, y, stone)
        for i in range(4):
            if self.open_three(x, y, stone, i):
                cnt += 1
        self.play_stone(x, y, EMPTY)
        if cnt >= 2:
            return True
        return False

    def ssang_sa(self, x, y, stone):
        cnt = 0
        self.play_stone(x, y, stone)
        for i in range(4):
            if self.open_four(x, y, stone, i) == 2:
                cnt += 2
            elif self.is_four_dir(x, y, stone, i):
                cnt += 1
        self.play_stone(x, y, EMPTY)
        if cnt >= 2:
            return True
        return False