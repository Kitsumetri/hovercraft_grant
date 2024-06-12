import dataclasses
import os
import json
import customtkinter as ctk

from PIL import Image
from tkinter import filedialog as fd
from CTkMessagebox import CTkMessagebox
from app_utils import Parameters
from solve_eq import solve


class LeftFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "src_images")

        self.json_logo_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "json_logo_white.png")),
                                            # black
                                            dark_image=Image.open(os.path.join(image_path, "json_logo_white.png")),
                                            size=(20, 20))

        # Кнопки
        self.load_button = ctk.CTkButton(self, text="Загрузить", font=("Roboto", 12, "bold"),
                                         command=master.load_json,
                                         image=self.json_logo_image, compound="right")
        self.load_button.pack(side=ctk.TOP)

        self.save_button = ctk.CTkButton(self, text="Сохранить", font=("Roboto", 12, "bold"),
                                         command=master.save_params_to_json,
                                         image=self.json_logo_image, compound="right")
        self.save_button.pack(pady=24)

        self.clear_button = ctk.CTkButton(self, text="Очистить все", command=master.clear_all,
                                          font=("Roboto", 12, "bold"))
        self.clear_button.pack()

        self.calculate_button = ctk.CTkButton(self, text="Расчёт", command=master.calculate,
                                              font=("Roboto", 12, "bold"))
        self.calculate_button.pack(pady=24)

        self.appearance_mode_option_menu = ctk.CTkOptionMenu(self,
                                                             values=["Light", "Dark", "System"],
                                                             command=self.change_appearance_mode_event)
        self.appearance_mode_option_menu.set("Dark")
        self.appearance_mode_option_menu.pack(side=ctk.BOTTOM)

        self.label_appearance = ctk.CTkLabel(self, text='Внешний вид: ')
        self.label_appearance.pack(pady=3, side=ctk.BOTTOM)

    @staticmethod
    def change_appearance_mode_event(new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)


class RightFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.entries = {}

        self.parameters = [("m", "Масса"), ("rho", "Плотность"),
                           ("S", "Площадь поперечного сечения"),
                           ("g", "Ускорение свободного падения"), ("n", "Коэффициент n"),
                           ("p_a", "Атмосферное давление"),
                           ("I", "Момент инерции"), ("l", "Плечо"), ("xi", "Коэффициент xi")]
        self.parabola_parameters = [("a", "Параметр a"), ("b", "Параметр b"), ("c", "Параметр c")]
        self.create_entries()

    def create_entries(self):
        row = 1
        # Создание полей ввода для основных параметров
        for i, (param_code, param_name) in enumerate(self.parameters):
            column = i % 2
            label = ctk.CTkLabel(self, text=f"{param_name}:", font=("Roboto", 12, "bold"))
            label.grid(row=row, column=column, padx=50, ipadx=80, pady=(5, 5), sticky="ew")

            entry = ctk.CTkEntry(self, placeholder_text=f"Введите {param_code}", font=("Roboto", 12, "bold"))
            entry.grid(row=row + 1, column=column, ipadx=80, ipady=6, padx=65, pady=(0, 10), sticky="w")

            self.entries[param_code] = entry

            if column == 1:
                row += 2

        row += 2

        # Добавление заголовка для параметров параболы
        parabola_label = ctk.CTkLabel(self,
                                      text="Параметры параболы {a, b, c},\nхарактеризующей объемный расход воздуха",
                                      font=("Roboto", 18, "bold", "underline"), fg_color='transparent')

        parabola_label.grid(row=row, column=0, columnspan=2, pady=(10, 5), sticky="ew")
        row += 1

        for param_code, param_name in self.parabola_parameters:
            column = self.parabola_parameters.index((param_code, param_name)) % 2
            label = ctk.CTkLabel(self, text=f"{param_name}:", font=("Roboto", 12, "bold"))
            label.grid(row=row, column=column, padx=50, ipadx=80, pady=(5, 5), sticky="ew")

            entry = ctk.CTkEntry(self, placeholder_text=f"Введите {param_code}", font=("Roboto", 12, "bold"))
            entry.grid(row=row + 1, column=column, ipadx=80, ipady=6, padx=65, pady=(0, 10), sticky="w")

            self.entries[param_code] = entry

            if column == 1:
                row += 2

        if len(self.parabola_parameters) % 2 == 1:
            self.grid_rowconfigure(row + 2, weight=1)


class CalculationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.resizable(False, False)
        ctk.set_default_color_theme('dark-blue')

        self.geometry("800x700")
        self.title("Calculation Tool")

        # Создаем фреймы
        self.left_frame = LeftFrame(self)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.right_frame = RightFrame(self)
        self.right_frame.pack(pady=10)

    def load_json(self):
        filename = fd.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not filename:
            return
        try:
            with open(filename, 'r') as file:
                data = json.load(file)

            for key, value in data.items():
                if key in self.right_frame.entries:
                    self.right_frame.entries[key].delete(0, 'end')
                    self.right_frame.entries[key].insert(0, value)
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Ошибка при чтении файла:\n{e}", icon="cancel")

    def get_params(self):
        missing_params = []
        params = {}

        for key, entry in self.right_frame.entries.items():
            value = entry.get()
            if value:
                try:
                    params[key] = float(value)
                except ValueError:
                    CTkMessagebox(title="Error",
                                  message=f"{key} должен быть число.\nПолучено '{value}' вместо этого.",
                                  icon="cancel")
                    return None
            else:
                missing_params.append(key)

        if missing_params:
            CTkMessagebox(title="Error",
                          message=f"Пропущенные параметры:\n{', '.join(missing_params)}",
                          icon="cancel")
            return None

        return Parameters(**params)

    def save_params_to_json(self):
        params = self.get_params()
        if params is None:
            return

        params_dict = dataclasses.asdict(params)
        file_path = fd.asksaveasfilename(defaultextension=".json",
                                         filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not file_path:
            return

        try:
            with open(file_path, 'w') as json_file:
                json.dump(params_dict, json_file, indent=4)
            CTkMessagebox(title="Ok", message=f"Файл успешно сохранён по пути:\n{file_path}", icon="check")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Ошибка при сохранении файла:\n{e}", icon="cancel")

    def calculate(self):
        solve(self.get_params())

    def clear_all(self):
        for entry in self.right_frame.entries.values():
            entry.delete(0, 'end')


if __name__ == "__main__":
    app = CalculationApp()
    app.mainloop()
