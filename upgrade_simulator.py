import tkinter as tk
from tkinter import ttk, messagebox
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class UpgradeSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("장비 강화 시뮬레이터")
        self.root.geometry("800x600")
        
        # 스타일 설정
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('맑은 고딕', 10))
        style.configure('TButton', font=('맑은 고딕', 10))
        style.configure('TEntry', font=('맑은 고딕', 10))
        
        # 메인 프레임
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 입력 프레임
        self.input_frame = ttk.LabelFrame(self.main_frame, text="시뮬레이션 설정", padding="10")
        self.input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 시작 단계 설정
        ttk.Label(self.input_frame, text="시작 강화 단계:").grid(row=0, column=0, padx=5, pady=5)
        self.start_level = ttk.Entry(self.input_frame, width=10)
        self.start_level.grid(row=0, column=1, padx=5, pady=5)
        self.start_level.insert(0, "0")
        
        # 목표 단계 설정
        ttk.Label(self.input_frame, text="목표 강화 단계:").grid(row=0, column=2, padx=5, pady=5)
        self.target_level = ttk.Entry(self.input_frame, width=10)
        self.target_level.grid(row=0, column=3, padx=5, pady=5)
        self.target_level.insert(0, "10")
        
        # 성공 확률 설정
        ttk.Label(self.input_frame, text="성공 확률 (%):").grid(row=0, column=4, padx=5, pady=5)
        self.success_rate = ttk.Entry(self.input_frame, width=10)
        self.success_rate.grid(row=0, column=5, padx=5, pady=5)
        self.success_rate.insert(0, "50")
        
        # 시뮬레이션 횟수 설정
        ttk.Label(self.input_frame, text="시뮬레이션 횟수:").grid(row=0, column=6, padx=5, pady=5)
        self.simulation_count = ttk.Entry(self.input_frame, width=10)
        self.simulation_count.grid(row=0, column=7, padx=5, pady=5)
        self.simulation_count.insert(0, "1000")
        
        # 시작 버튼
        self.start_button = ttk.Button(self.input_frame, text="시뮬레이션 시작", command=self.run_simulation)
        self.start_button.grid(row=0, column=8, padx=5, pady=5)
        
        # 결과 프레임
        self.result_frame = ttk.LabelFrame(self.main_frame, text="시뮬레이션 결과", padding="10")
        self.result_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 결과 표시
        self.result_labels = {}
        metrics = ["평균 시도 횟수", "최소 시도 횟수", "최대 시도 횟수", "성공 확률"]
        for i, metric in enumerate(metrics):
            ttk.Label(self.result_frame, text=f"{metric}:").grid(row=i, column=0, padx=5, pady=5)
            self.result_labels[metric] = ttk.Label(self.result_frame, text="-")
            self.result_labels[metric].grid(row=i, column=1, padx=5, pady=5)
        
        # 그래프 프레임
        self.graph_frame = ttk.LabelFrame(self.main_frame, text="시도 횟수 분포", padding="10")
        self.graph_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 그래프 초기화
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 그리드 설정
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
    def run_simulation(self):
        try:
            start_level = int(self.start_level.get())
            target_level = int(self.target_level.get())
            success_rate = float(self.success_rate.get()) / 100
            count = int(self.simulation_count.get())
            
            if start_level >= target_level:
                messagebox.showerror("오류", "시작 강화 단계는 목표 강화 단계보다 낮아야 합니다.")
                return
                
            if not (0 <= success_rate <= 1):
                messagebox.showerror("오류", "성공 확률은 0%에서 100% 사이여야 합니다.")
                return
                
            attempts = []
            success_count = 0
            
            for _ in range(count):
                current_level = start_level
                attempt_count = 0
                
                while current_level < target_level:
                    attempt_count += 1
                    if random.random() < success_rate:
                        current_level += 1
                    else:
                        current_level = max(0, current_level - 1)
                
                attempts.append(attempt_count)
                if current_level == target_level:
                    success_count += 1
            
            # 결과 업데이트
            self.result_labels["평균 시도 횟수"].config(text=f"{np.mean(attempts):.2f}")
            self.result_labels["최소 시도 횟수"].config(text=f"{min(attempts)}")
            self.result_labels["최대 시도 횟수"].config(text=f"{max(attempts)}")
            self.result_labels["성공 확률"].config(text=f"{(success_count/count)*100:.2f}%")
            
            # 그래프 업데이트
            self.ax.clear()
            self.ax.hist(attempts, bins=min(50, len(set(attempts))), alpha=0.7)
            self.ax.set_xlabel("시도 횟수")
            self.ax.set_ylabel("빈도")
            self.ax.set_title("시도 횟수 분포")
            self.canvas.draw()
            
        except ValueError:
            messagebox.showerror("오류", "올바른 숫자를 입력해주세요.")

if __name__ == "__main__":
    root = tk.Tk()
    app = UpgradeSimulator(root)
    root.mainloop() 