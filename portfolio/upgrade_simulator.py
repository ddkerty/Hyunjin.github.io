import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import random
import json
import os

# 강화할 아이템 클래스
class UpgradeItem:
    def __init__(self, name, item_type, level=0, broken=False):
        self.name = name  # 아이템 이름
        self.item_type = item_type  # 아이템 타입
        self.level = level  # 현재 강화 레벨
        self.broken = broken  # 손상 여부

# 강화 재료 클래스
class UpgradeMaterial:
    def __init__(self, name, applicable_types, upgrade_data):
        self.name = name  # 강화 재료 이름
        self.applicable_types = applicable_types  # 사용 가능한 아이템 타입
        self.upgrade_data = upgrade_data  # 강화 확률 및 비용 정보

# 강화 시뮬레이터 메인 클래스
class UpgradeSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("무기 강화 시뮬레이터")

        self.save_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "upgrade_data.json")
        self.item = UpgradeItem("검", 1)

        self.success_count = 0
        self.great_success_count = 0
        self.fail_count = 0
        self.damage_count = 0
        self.severe_damage_count = 0
        self.destruction_count = 0
        self.total_cost_money = 0
        self.total_cost_core = 0
        self.total_attempts = 0

        self.material = self.load_upgrade_data()

        self.create_ui()

    def create_ui(self):
        self.level_label = tk.Label(self.root, text=f"아이템 레벨: {self.item.level}")
        self.level_label.pack()

        self.upgrade_button = tk.Button(self.root, text="강화", command=self.upgrade_item)
        self.upgrade_button.pack()

        self.auto_upgrade_button = tk.Button(self.root, text="목표까지 자동 강화", command=self.auto_upgrade)
        self.auto_upgrade_button.pack()

        self.target_entry = tk.Entry(self.root)
        self.target_entry.pack()
        self.target_entry.insert(0, "목표 레벨 입력 (숫자만)")

        self.edit_button = tk.Button(self.root, text="강화 데이터 수정", command=self.edit_upgrade_data)
        self.edit_button.pack()

        self.reset_button = tk.Button(self.root, text="아이템 초기화", command=self.reset_item)
        self.reset_button.pack()

        self.result_text = tk.Text(self.root, height=15, width=60)
        self.result_text.pack()

    def reset_item(self):
        self.item = UpgradeItem("검", 1)
        self.level_label.config(text=f"아이템 레벨: {self.item.level}")
        self.result_text.insert(tk.END, "아이템이 초기화되었습니다.\n")

    def upgrade_item(self):
        if self.item.broken:
            messagebox.showwarning("경고", "아이템이 손상되어 더 이상 강화할 수 없습니다.")
            return

        current_level = self.item.level
        upgrade_info = self.material.upgrade_data.get(str(current_level + 1), None)

        if not upgrade_info:
            messagebox.showinfo("정보", "다음 레벨에 대한 강화 데이터가 없습니다.")
            return

        self.total_cost_money += upgrade_info.get("cost_money", 0)
        self.total_cost_core += upgrade_info.get("cost_core_count", 0)
        self.total_attempts += 1

        result = self.determine_upgrade_result(upgrade_info)
        self.apply_upgrade_result(result)

        self.result_text.insert(tk.END, f"강화 결과: {result}\n")
        self.result_text.see(tk.END)

        if result == "대성공":
            self.great_success_count += 1
        elif result == "성공":
            self.success_count += 1
        elif result == "실패":
            self.fail_count += 1
        elif result == "손상":
            self.damage_count += 1
        elif result == "대손상":
            self.severe_damage_count += 1
        elif result == "파괴":
            self.destruction_count += 1

    def auto_upgrade(self):
        target_input = self.target_entry.get()

        if not target_input.isdigit() or int(target_input) <= 0:
            self.result_text.insert(tk.END, "❗ 숫자만 입력하세요 (1 이상의 정수)\n")
            self.result_text.see(tk.END)
            messagebox.showerror("입력 오류", "1 이상의 숫자를 입력해 주세요.")
            return

        target_level = int(target_input)

        if str(target_level) not in self.material.upgrade_data:
            messagebox.showerror("오류", "목표 레벨이 설정된 강화 데이터를 초과했습니다.")
            return

        while self.item.level < target_level:
            self.upgrade_item()

            if self.item.broken or self.item.level == 0:
                self.result_text.insert(tk.END, "아이템이 손상되거나 파괴되었습니다. 1레벨부터 다시 시작합니다.\n")
                self.item = UpgradeItem("검", 1)

        final_results = (
            f"총 시도 횟수: {self.total_attempts}\n"
            f"성공 횟수: {self.success_count}\n"
            f"대성공 횟수: {self.great_success_count}\n"
            f"실패 횟수: {self.fail_count}\n"
            f"손상 횟수: {self.damage_count}\n"
            f"대손상 횟수: {self.severe_damage_count}\n"
            f"파괴 횟수: {self.destruction_count}\n"
            f"총 소모 금액: {self.total_cost_money}\n"
            f"총 소모 코어: {self.total_cost_core}\n"
        )

        self.result_text.insert(tk.END, "\n=== 최종 결과 ===\n" + final_results)
        self.result_text.see(tk.END)

        messagebox.showinfo("최종 결과", final_results)

    def determine_upgrade_result(self, upgrade_info):
        roll = random.random()
        success_rate = upgrade_info["success_rate"]

        if roll < success_rate:
            roll_success = random.random()
            if roll_success < upgrade_info.get("great_success_rate", 0.1):
                return "대성공"
            else:
                return "성공"
        else:
            roll_fail = random.random()
            fail_thresholds = [
                upgrade_info.get("fail_rate", 0.4),
                upgrade_info.get("fail_rate", 0.4) + upgrade_info.get("damage_rate", 0.3),
                upgrade_info.get("fail_rate", 0.4) + upgrade_info.get("damage_rate", 0.3) + upgrade_info.get("severe_damage_rate", 0.2)
            ]

            if roll_fail < fail_thresholds[0]:
                return "실패"
            elif roll_fail < fail_thresholds[1]:
                return "손상"
            elif roll_fail < fail_thresholds[2]:
                return "대손상"
            else:
                return "파괴"

    def apply_upgrade_result(self, result):
        if result == "대성공":
            self.item.level += 2
        elif result == "성공":
            self.item.level += 1
        elif result == "실패":
            pass
        elif result == "손상":
            self.item.broken = True
        elif result == "대손상":
            self.item.broken = True
            self.item.level = max(0, self.item.level - 1)
        elif result == "파괴":
            self.item = UpgradeItem(self.item.name, self.item.item_type)

        self.level_label.config(text=f"아이템 레벨: {self.item.level}")

    def edit_upgrade_data(self):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("강화 데이터 수정")

        columns = ("레벨", "성공 확률", "대성공 확률", "실패 확률", "손상 확률", "대손상 확률", "파괴 확률", "소모 금액", "코어 소모량")
        tree = ttk.Treeview(edit_window, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        for level, data in sorted(self.material.upgrade_data.items(), key=lambda x: int(x[0])):
            tree.insert("", "end", values=(level, data.get("success_rate", 0), data.get("great_success_rate", 0),
                                            data.get("fail_rate", 0), data.get("damage_rate", 0), data.get("severe_damage_rate", 0),
                                            data.get("destruction_rate", 0), data.get("cost_money", 0), data.get("cost_core_count", 0)))

        tree.pack()

        def edit_cell(event):
            selected_item = tree.identify_row(event.y)
            selected_column = tree.identify_column(event.x)

            if not selected_item or not selected_column:
                return

            col_index = int(selected_column.replace("#", "")) - 1
            x, y, width, height = tree.bbox(selected_item, selected_column)

            entry_edit = tk.Entry(edit_window)
            entry_edit.place(x=x, y=y, width=width, height=height)
            entry_edit.insert(0, tree.item(selected_item, "values")[col_index])
            entry_edit.focus()

            def save_edit(event):
                new_value = entry_edit.get()
                current_values = list(tree.item(selected_item, "values"))
                current_values[col_index] = new_value
                tree.item(selected_item, values=current_values)
                entry_edit.destroy()

            entry_edit.bind("<Return>", save_edit)
            entry_edit.bind("<FocusOut>", lambda e: entry_edit.destroy())

        tree.bind("<Double-1>", edit_cell)

        def add_level():
            new_level = simpledialog.askstring("레벨 추가", "추가할 레벨 번호를 입력하세요:")
            if new_level and new_level not in self.material.upgrade_data:
                self.material.upgrade_data[new_level] = {
                    "success_rate": 0.5,
                    "great_success_rate": 0.0,
                    "fail_rate": 0.4,
                    "damage_rate": 0.0,
                    "severe_damage_rate": 0.0,
                    "destruction_rate": 0.0,
                    "cost_money": 1000,
                    "cost_core_count": 1
                }
                tree.insert("", "end", values=(new_level, 0.5, 0.0, 0.4, 0.0, 0.0, 0.0, 1000, 1))

        def delete_level():
            selected_item = tree.selection()
            if selected_item:
                level = tree.item(selected_item, "values")[0]
                del self.material.upgrade_data[level]
                tree.delete(selected_item)

        def save_changes():
            for item in tree.get_children():
                values = tree.item(item, "values")
                level = str(values[0])
                self.material.upgrade_data[level] = {
                    "success_rate": float(values[1]),
                    "great_success_rate": float(values[2]),
                    "fail_rate": float(values[3]),
                    "damage_rate": float(values[4]),
                    "severe_damage_rate": float(values[5]),
                    "destruction_rate": float(values[6]),
                    "cost_money": int(values[7]),
                    "cost_core_count": int(values[8])
                }

            self.save_upgrade_data()
            edit_window.destroy()

        button_frame = tk.Frame(edit_window)
        button_frame.pack()

        add_button = tk.Button(button_frame, text="레벨 추가", command=add_level)
        add_button.pack(side=tk.LEFT)

        delete_button = tk.Button(button_frame, text="레벨 삭제", command=delete_level)
        delete_button.pack(side=tk.LEFT)

        save_button = tk.Button(button_frame, text="저장", command=save_changes)
        save_button.pack(side=tk.LEFT)

    def save_upgrade_data(self):
        with open(self.save_file, "w", encoding="utf-8") as f:
            json.dump(self.material.upgrade_data, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("저장 완료", "강화 데이터가 성공적으로 저장되었습니다.")

    def load_upgrade_data(self):
        default_data = {
            "1": {"success_rate": 1.0, "great_success_rate": 0.0, "fail_rate": 0.0, "damage_rate": 0.0, "severe_damage_rate": 0.0, "destruction_rate": 0.0, "cost_core_count": 1, "cost_money": 2000},
            "2": {"success_rate": 1.0, "great_success_rate": 0.0, "fail_rate": 0.0, "damage_rate": 0.0, "severe_damage_rate": 0.0, "destruction_rate": 0.0, "cost_core_count": 1, "cost_money": 2240},
            "3": {"success_rate": 1.0, "great_success_rate": 0.0, "fail_rate": 0.0, "damage_rate": 0.0, "severe_damage_rate": 0.0, "destruction_rate": 0.0, "cost_core_count": 1, "cost_money": 2509},
            "4": {"success_rate": 1.0, "great_success_rate": 0.0, "fail_rate": 0.0, "damage_rate": 0.0, "severe_damage_rate": 0.0, "destruction_rate": 0.0, "cost_core_count": 1, "cost_money": 2810},
            "5": {"success_rate": 0.51, "great_success_rate": 0.0, "fail_rate": 0.0, "damage_rate": 0.49, "severe_damage_rate": 0.0, "destruction_rate": 0.0, "cost_core_count": 1, "cost_money": 3147},
            "6": {"success_rate": 0.28, "great_success_rate": 0.0, "fail_rate": 0.0, "damage_rate": 0.72, "severe_damage_rate": 0.0, "destruction_rate": 0.0, "cost_core_count": 1, "cost_money": 13000},
            "7": {"success_rate": 0.18, "great_success_rate": 0.0, "fail_rate": 0.0, "damage_rate": 0.82, "severe_damage_rate": 0.0, "destruction_rate": 0.0, "cost_core_count": 1, "cost_money": 15600},
            "8": {"success_rate": 0.13, "great_success_rate": 0.0, "fail_rate": 0.0, "damage_rate": 0.0, "severe_damage_rate": 0.87, "destruction_rate": 0.0, "cost_core_count": 1, "cost_money": 18720},
            "9": {"success_rate": 0.10, "great_success_rate": 0.0, "fail_rate": 0.0, "damage_rate": 0.0, "severe_damage_rate": 0.90, "destruction_rate": 0.0, "cost_core_count": 1, "cost_money": 22464}
        }

        if os.path.exists(self.save_file):
            with open(self.save_file, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
            # 기본 데이터와 병합
            for level, data in default_data.items():
                if level not in saved_data:
                    saved_data[level] = data
            return UpgradeMaterial("강화석", [1, 2], saved_data)
        else:
            return UpgradeMaterial("강화석", [1, 2], default_data)

if __name__ == "__main__":
    root = tk.Tk()
    app = UpgradeSimulator(root)
    root.mainloop()
