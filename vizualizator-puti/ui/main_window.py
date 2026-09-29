"""
Tkinter-интерфейс визуализатора.

Окно состоит из двух сменяемых экранов (паттерн, близкий к
"навигации через контейнер"):
  - MainMenuFrame — главное меню (создание/загрузка карты, выход);
  - WorkspaceFrame — рабочая область с картой, панелью инструментов
    и визуализацией работы алгоритмов.

UI не содержит логики самих алгоритмов — он только вызывает
алгоритмы через algorithms.algorithm_factory и хранит карту через
core.models.Grid, что соответствует принципу инверсии зависимостей:
ядро (core, algorithms) ничего не знает про tkinter.
"""
import random
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from algorithms.algorithm_factory import available_algorithms, build_algorithm
from core.models import Grid
from storage.json_map_repository import JsonMapRepository

CELL_SIZE = 24

COLOR_EMPTY = "#FFFFFF"
COLOR_WALL = "#2B2420"
COLOR_START = "#2E7D32"
COLOR_FINISH = "#C62828"
COLOR_VISITED = "#BBD8F5"
COLOR_PATH = "#F5C542"
COLOR_GRID_LINE = "#D8D2C4"

DEFAULT_WIDTH = 25
DEFAULT_HEIGHT = 18

MODE_NONE = "none"
MODE_SET_START = "set_start"
MODE_SET_FINISH = "set_finish"
MODE_MANUAL_WALLS = "manual_walls"


class MainMenuFrame(ttk.Frame):
    """Главное меню: создание новой карты, загрузка карты, выход."""

    def __init__(self, master, on_create, on_load, on_exit):
        super().__init__(master, padding=40)
        self._on_create = on_create
        self._on_load = on_load
        self._on_exit = on_exit
        self._build_ui()

    def _build_ui(self):
        title = ttk.Label(self, text="Визуализатор алгоритмов поиска пути", font=("Georgia", 18, "bold"))
        title.pack(pady=(0, 8))

        subtitle = ttk.Label(self, text="A* · Дейкстра · BFS", font=("Arial", 12))
        subtitle.pack(pady=(0, 30))

        ttk.Button(self, text="Создание карты", command=self._handle_create, width=30).pack(pady=6)
        ttk.Button(self, text="Загрузка карты", command=self._handle_load, width=30).pack(pady=6)
        ttk.Button(self, text="Выход", command=self._on_exit, width=30).pack(pady=6)

    def _handle_create(self):
        width = simpledialog.askinteger(
            "Создание карты", "Ширина карты (в клетках):", initialvalue=DEFAULT_WIDTH, minvalue=5, maxvalue=80
        )
        if width is None:
            return
        height = simpledialog.askinteger(
            "Создание карты", "Высота карты (в клетках):", initialvalue=DEFAULT_HEIGHT, minvalue=5, maxvalue=50
        )
        if height is None:
            return
        self._on_create(width, height)

    def _handle_load(self):
        path = simpledialog.askstring("Загрузка карты", "Путь к файлу карты (.json):")
        if not path:
            return
        self._on_load(path)


class WorkspaceFrame(ttk.Frame):
    """Рабочая область: карта, панель инструментов, визуализация."""

    def __init__(self, master, grid: Grid, on_back_to_menu):
        super().__init__(master, padding=10)
        self._on_back_to_menu = on_back_to_menu
        self._repository = JsonMapRepository()

        self._grid = grid
        self._algorithm_name = available_algorithms()[0]
        self._mode = MODE_NONE

        self._path_result = None
        self._visited_shown = []
        self._path_shown = []
        self._step_index = 0
        self._is_paused = True
        self._auto_run_job = None

        self._build_toolbar()
        self._build_canvas()
        self._build_status_bar()
        self._redraw()

    # ------------------------------------------------------------------ UI

    def _build_toolbar(self):
        bar = ttk.Frame(self)
        bar.pack(side=tk.TOP, fill=tk.X, pady=(0, 8))

        row1 = ttk.Frame(bar)
        row1.pack(side=tk.TOP, fill=tk.X, pady=2)
        row2 = ttk.Frame(bar)
        row2.pack(side=tk.TOP, fill=tk.X, pady=2)
        row3 = ttk.Frame(bar)
        row3.pack(side=tk.TOP, fill=tk.X, pady=2)

        ttk.Button(row1, text="В меню", command=self._back_to_menu).pack(side=tk.LEFT, padx=3)
        ttk.Button(row1, text="Создание карты", command=self._create_new_map).pack(side=tk.LEFT, padx=3)
        ttk.Button(row1, text="Сохранение карты", command=self._save_map).pack(side=tk.LEFT, padx=3)
        ttk.Button(row1, text="Загрузка карты", command=self._load_map).pack(side=tk.LEFT, padx=3)
        ttk.Button(row1, text="Очистка карты", command=self._clear_map).pack(side=tk.LEFT, padx=3)
        ttk.Button(row1, text="Сброс", command=self._reset_visualization).pack(side=tk.LEFT, padx=3)

        ttk.Label(row2, text="Выбор алгоритма:").pack(side=tk.LEFT, padx=(3, 4))
        self._algorithm_var = tk.StringVar(value=self._algorithm_name)
        algo_menu = ttk.OptionMenu(
            row2, self._algorithm_var, self._algorithm_name, *available_algorithms(), command=self._on_algorithm_change
        )
        algo_menu.pack(side=tk.LEFT, padx=3)
        ttk.Button(row2, text="Сравнение алгоритмов", command=self._compare_algorithms).pack(side=tk.LEFT, padx=10)

        ttk.Button(row2, text="Шаг", command=self._step).pack(side=tk.LEFT, padx=3)
        self._pause_button = ttk.Button(row2, text="Пуск", command=self._toggle_auto_run)
        self._pause_button.pack(side=tk.LEFT, padx=3)

        ttk.Button(row3, text="Установка старта", command=lambda: self._set_mode(MODE_SET_START)).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(row3, text="Установка финиша", command=lambda: self._set_mode(MODE_SET_FINISH)).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(row3, text="Установка стен", command=self._auto_walls).pack(side=tk.LEFT, padx=3)
        ttk.Button(row3, text="Установка стен вручную", command=lambda: self._set_mode(MODE_MANUAL_WALLS)).pack(
            side=tk.LEFT, padx=3
        )

        self._mode_label_var = tk.StringVar(value="Режим: обзор")
        ttk.Label(row3, textvariable=self._mode_label_var, foreground="#7A6F63").pack(side=tk.LEFT, padx=12)

    def _build_canvas(self):
        canvas_width = self._grid.width * CELL_SIZE
        canvas_height = self._grid.height * CELL_SIZE
        self._canvas = tk.Canvas(
            self, width=canvas_width, height=canvas_height, background=COLOR_EMPTY, highlightthickness=1,
            highlightbackground=COLOR_GRID_LINE,
        )
        self._canvas.pack(side=tk.TOP)
        self._canvas.bind("<Button-1>", self._on_canvas_click)
        self._canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self._canvas.bind("<Button-3>", self._on_canvas_right_click)

    def _build_status_bar(self):
        self._status_var = tk.StringVar(value="Готово")
        status = ttk.Label(self, textvariable=self._status_var, anchor="w", foreground="#5B5148")
        status.pack(side=tk.TOP, fill=tk.X, pady=(6, 0))

    # ------------------------------------------------------------ handlers

    def _back_to_menu(self):
        self._stop_auto_run()
        self._on_back_to_menu()

    def _create_new_map(self):
        width = simpledialog.askinteger(
            "Создание карты", "Ширина карты (в клетках):", initialvalue=self._grid.width, minvalue=5, maxvalue=80
        )
        if width is None:
            return
        height = simpledialog.askinteger(
            "Создание карты", "Высота карты (в клетках):", initialvalue=self._grid.height, minvalue=5, maxvalue=50
        )
        if height is None:
            return
        self._stop_auto_run()
        self._grid = Grid(width=width, height=height)
        self._reset_visualization()
        self._build_canvas_resize()
        self._update_status("Создана новая карта {}×{}".format(width, height))

    def _build_canvas_resize(self):
        self._canvas.destroy()
        self._build_canvas()

    def _set_mode(self, mode: str):
        self._mode = mode
        labels = {
            MODE_NONE: "Режим: обзор",
            MODE_SET_START: "Режим: установка старта (клик по клетке)",
            MODE_SET_FINISH: "Режим: установка финиша (клик по клетке)",
            MODE_MANUAL_WALLS: "Режим: рисование стен (клик/протяжка, ПКМ — стереть)",
        }
        self._mode_label_var.set(labels.get(mode, "Режим: обзор"))

    def _cell_at(self, event) -> "tuple":
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        return (row, col)

    def _on_canvas_click(self, event):
        pos = self._cell_at(event)
        if not self._grid.in_bounds(pos):
            return

        if self._mode == MODE_SET_START:
            self._grid.set_start(pos)
        elif self._mode == MODE_SET_FINISH:
            self._grid.set_finish(pos)
        elif self._mode == MODE_MANUAL_WALLS:
            self._grid.set_wall(pos, True)
        self._redraw()

    def _on_canvas_drag(self, event):
        if self._mode == MODE_MANUAL_WALLS:
            pos = self._cell_at(event)
            if self._grid.in_bounds(pos):
                self._grid.set_wall(pos, True)
                self._redraw()

    def _on_canvas_right_click(self, event):
        pos = self._cell_at(event)
        if self._grid.in_bounds(pos):
            self._grid.set_wall(pos, False)
            self._redraw()

    def _on_algorithm_change(self, value):
        self._algorithm_name = value
        self._reset_visualization()

    def _auto_walls(self):
        self._grid.clear_walls()
        for row in range(self._grid.height):
            for col in range(self._grid.width):
                pos = (row, col)
                if pos in (self._grid.start, self._grid.finish):
                    continue
                if random.random() < 0.25:
                    self._grid.walls.add(pos)
        self._reset_visualization()
        self._update_status("Стены расставлены автоматически")

    def _save_map(self):
        path = simpledialog.askstring("Сохранение карты", "Путь для сохранения (.json):", initialvalue="map.json")
        if not path:
            return
        try:
            self._repository.save(self._grid, path)
            self._update_status("Карта сохранена: {}".format(path))
        except OSError as exc:
            messagebox.showerror("Ошибка сохранения", str(exc))

    def _load_map(self):
        path = simpledialog.askstring("Загрузка карты", "Путь к файлу карты (.json):")
        if not path:
            return
        try:
            self._grid = self._repository.load(path)
        except (OSError, ValueError, KeyError) as exc:
            messagebox.showerror("Ошибка загрузки", str(exc))
            return
        self._reset_visualization()
        self._build_canvas_resize()
        self._update_status("Карта загружена: {}".format(path))

    def _clear_map(self):
        self._grid.clear_all()
        self._reset_visualization()
        self._update_status("Карта очищена")

    def _reset_visualization(self):
        self._stop_auto_run()
        self._path_result = None
        self._visited_shown = []
        self._path_shown = []
        self._step_index = 0
        self._is_paused = True
        self._pause_button.config(text="Пуск")
        self._redraw()
        self._update_status("Визуализация сброшена")

    # ------------------------------------------------------------- запуск

    def _ensure_result(self) -> bool:
        if self._grid.start is None or self._grid.finish is None:
            messagebox.showwarning("Нет данных", "Сначала установите старт и финиш.")
            return False
        if self._path_result is None:
            algorithm = build_algorithm(self._algorithm_name)
            self._path_result = algorithm.find_path(self._grid)
            self._visited_shown = []
            self._path_shown = []
            self._step_index = 0
        return True

    def _step(self):
        if not self._ensure_result():
            return

        result = self._path_result
        total_visited = len(result.visited_order)

        if self._step_index < total_visited:
            self._visited_shown.append(result.visited_order[self._step_index])
            self._step_index += 1
            self._redraw()
            self._update_status(
                "Шаг {}/{}: посещено клеток — {}".format(self._step_index, total_visited, len(self._visited_shown))
            )
            return

        if result.path and len(self._path_shown) < len(result.path):
            self._path_shown = list(result.path)
            self._redraw()
            self._update_status("Путь найден: {} клеток".format(result.path_length))
            self._stop_auto_run()
            return

        if not result.path:
            self._update_status("Путь не найден")
        self._stop_auto_run()

    def _toggle_auto_run(self):
        if self._auto_run_job is not None:
            self._stop_auto_run()
            return
        if not self._ensure_result():
            return
        self._is_paused = False
        self._pause_button.config(text="Пауза")
        self._auto_step()

    def _auto_step(self):
        self._step()
        result = self._path_result
        done = result is not None and self._step_index >= len(result.visited_order) and (
            not result.path or len(self._path_shown) >= len(result.path)
        )
        if done:
            self._stop_auto_run()
            return
        self._auto_run_job = self.after(15, self._auto_step)

    def _stop_auto_run(self):
        if self._auto_run_job is not None:
            self.after_cancel(self._auto_run_job)
            self._auto_run_job = None
        self._is_paused = True
        self._pause_button.config(text="Пуск")

    def _compare_algorithms(self):
        if self._grid.start is None or self._grid.finish is None:
            messagebox.showwarning("Нет данных", "Сначала установите старт и финиш.")
            return

        lines = []
        for name in available_algorithms():
            algorithm = build_algorithm(name)
            result = algorithm.find_path(self._grid)
            if result.path:
                lines.append(
                    "{}: путь {} клеток, посещено {} клеток".format(name, result.path_length, result.visited_count)
                )
            else:
                lines.append("{}: путь не найден (посещено {} клеток)".format(name, result.visited_count))

        messagebox.showinfo("Сравнение алгоритмов", "\n".join(lines))

    # -------------------------------------------------------------- отрисовка

    def _redraw(self):
        self._canvas.delete("all")
        for row in range(self._grid.height):
            for col in range(self._grid.width):
                self._draw_cell((row, col))

    def _draw_cell(self, pos):
        row, col = pos
        x0 = col * CELL_SIZE
        y0 = row * CELL_SIZE
        x1 = x0 + CELL_SIZE
        y1 = y0 + CELL_SIZE

        color = COLOR_EMPTY
        if pos in self._grid.walls:
            color = COLOR_WALL
        if pos in self._visited_shown:
            color = COLOR_VISITED
        if pos in self._path_shown:
            color = COLOR_PATH
        if pos == self._grid.start:
            color = COLOR_START
        if pos == self._grid.finish:
            color = COLOR_FINISH

        self._canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=COLOR_GRID_LINE)

    def _update_status(self, message: str):
        self._status_var.set(message)


class App(tk.Tk):
    """Главное окно приложения, переключающее меню и рабочую область."""

    def __init__(self):
        super().__init__()
        self.title("Визуализатор алгоритмов поиска пути")
        self.resizable(False, False)
        self._current_frame = None
        self._show_main_menu()

    def _clear_frame(self):
        if self._current_frame is not None:
            self._current_frame.destroy()
            self._current_frame = None

    def _show_main_menu(self):
        self._clear_frame()
        self._current_frame = MainMenuFrame(
            self, on_create=self._start_with_new_map, on_load=self._start_with_loaded_map, on_exit=self.destroy
        )
        self._current_frame.pack(fill=tk.BOTH, expand=True)

    def _start_with_new_map(self, width: int, height: int):
        grid = Grid(width=width, height=height)
        self._show_workspace(grid)

    def _start_with_loaded_map(self, path: str):
        repository = JsonMapRepository()
        try:
            grid = repository.load(path)
        except (OSError, ValueError, KeyError) as exc:
            messagebox.showerror("Ошибка загрузки", str(exc))
            return
        self._show_workspace(grid)

    def _show_workspace(self, grid: Grid):
        self._clear_frame()
        self._current_frame = WorkspaceFrame(self, grid=grid, on_back_to_menu=self._show_main_menu)
        self._current_frame.pack(fill=tk.BOTH, expand=True)


def run():
    app = App()
    app.mainloop()
