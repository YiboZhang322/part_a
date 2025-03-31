from .core import CellState, Coord, Direction, MoveAction
from .utils import render_board
import heapq

def get_red_frog_moves(board: dict[Coord, CellState], frog_pos: Coord) -> list[list[Direction]]:
    """
    获取青蛙可以移动的所有合法方向，包括普通移动和跳跃
    """

    def valid_coordinate(pos, dir):
        """ 检查坐标是否在 8x8 范围内 """
        pos_r, pos_c = pos.r, pos.c
        dir_r, dir_c = dir.r, dir.c
        return 0 <= pos_r + dir_r <= 7 and 0 <= pos_c + dir_c <= 7

    possible_moves = []

    # 可移动方向
    red_directions = [
        Direction.Down,
        Direction.DownLeft,
        Direction.DownRight,
        Direction.Left,
        Direction.Right
    ]

    # 普通移动
    for direction in red_directions:
        neighbor_pos = frog_pos + direction
        if valid_coordinate(frog_pos, direction) and neighbor_pos in board and board[neighbor_pos] == CellState.LILY_PAD:
            possible_moves.append([direction])

    # 记录已访问的跳跃目标，防止无限循环
    visited = set()

    def dfs(current_pos: Coord, path: list[Direction]):
        """ 递归寻找所有可能的跳跃路径 """
        if path:
            possible_moves.append(path.copy())

        for direction in red_directions:
            jump_over_pos = current_pos + direction
            if jump_over_pos not in board or board[jump_over_pos] != CellState.BLUE:
                continue  # 不是蓝棋，不能跳跃

            landing_pos = jump_over_pos + direction
            if valid_coordinate(jump_over_pos, direction) and landing_pos in board and board[landing_pos] == CellState.LILY_PAD:
                new_path = path + [direction]
                if landing_pos not in visited:
                    visited.add(landing_pos)
                    dfs(landing_pos, new_path)
                    visited.remove(landing_pos)

    dfs(frog_pos, [])

    return possible_moves


def search(board: dict[Coord, CellState]) -> list[MoveAction] | None:
    """
    使用 A* 搜索从起点（红青蛙）到达最底一行的最短路径

    返回：
        - 若找到路径，返回 MoveAction 的列表
        - 若无解，返回 None
    """

    print(render_board(board, ansi=True))  # 输出当前棋盘状态（可选）

    # 找到起点和目标点（最底行的 LILY_PAD）
    start_coord = None
    target_pads = []

    for coord, state in board.items():
        if state == CellState.RED:
            start_coord = coord
        if state == CellState.LILY_PAD and coord.r == 7:
            target_pads.append(coord)

    if not start_coord or not target_pads:
        return None  # 没有红青蛙，或者没有可到达的目标

    # 启发函数 h(n)（曼哈顿距离）
    def heuristic(pos: Coord) -> int:
        return 7 - pos.r  # 目标是最底行，计算行数差

    # A* 需要的优先队列（存储 (f, g, 当前坐标, 路径)）
    open_list = []
    heapq.heappush(open_list, (heuristic(start_coord), 0, start_coord, []))

    # 记录访问过的节点
    visited = set()
    visited.add(start_coord)

    while open_list:
        _, g, current_coord, path_actions = heapq.heappop(open_list)

        # 到达胜利条件：最底行的 LILY_PAD
        if current_coord in target_pads:
            return path_actions

        # 获取可行的移动
        possible_moves = get_red_frog_moves(board, current_coord)

        for move in possible_moves:
            if isinstance(move, list) and len(move) == 1:
                new_coord = current_coord + move[0]  # 普通移动
            else:
                new_coord = current_coord
                for direction in move:  # 跳跃移动
                    jumped_pos = new_coord + direction
                    new_coord = jumped_pos + direction

            if new_coord not in visited:
                visited.add(new_coord)
                new_action = MoveAction(current_coord, move)
                new_path = path_actions + [new_action]
                heapq.heappush(open_list, (g + 1 + heuristic(new_coord), g + 1, new_coord, new_path))

    return None  # 无法找到路径
