import os
import tkinter as tk
from tkinter import filedialog, ttk

os.environ["TK_SILENCE_DEPRECATION"] = "1"

from .bridge import InterpreterBridge
from .components import create_top_bar, setup_dark_styles

class LOLCodeIDE:

  def __init__(self, root):
    self.root = root
    self.root.title("GROUP THREE LOLCODE INTERPRETER")
    self.root.geometry("1200x750")
    self.root.configure(bg="#2C2C2C")

    self.bridge = InterpreterBridge()
    setup_dark_styles()

    try:
      current_dir = os.path.dirname(os.path.abspath(__file__))
      logo_path = os.path.join(current_dir, "..", "public", "logo.png")
      if os.path.exists(logo_path):
        self.app_icon = tk.PhotoImage(file=logo_path)
        self.root.iconphoto(True, self.app_icon)
    except Exception as e:
      print("Could not set application icon:", e)

    create_top_bar(self.root, on_run_callback=self.on_execute_clicked)
    self.build_main_layout()

  def build_main_layout(self):
    self.main_pane = ttk.PanedWindow(self.root, orient="horizontal", style="TPanedwindow")
    self.main_pane.pack(fill="both", expand=True, padx=4, pady=4)

    # LEFT PANEL
    self.left_frame = tk.Frame(self.main_pane, bg="#2C2C2C", bd=0)
    self.main_pane.add(self.left_frame, weight=1)

    # Toolbar 
    self.toolbar_frame = tk.Frame(self.left_frame, bg="#2C2C2C")
    self.toolbar_frame.pack(fill="x", padx=8, pady=8)

    self.open_link = tk.Label(
        self.toolbar_frame,
        text="Open File",
        bg="#2C2C2C",
        fg="#C2C2C2",
        font=("Segoe UI", 10, "bold"),
        cursor="arrow",
    )
    self.open_link.pack(side="left", padx=(0, 15))
    self.open_link.bind("<Button-1>", lambda e: self.open_file_dialog())

    self.exit_link = tk.Label(
        self.toolbar_frame,
        text="Exit",
        bg="#2C2C2C",
        fg="#C2C2C2",
        font=("Segoe UI", 10, "bold"),
        cursor="arrow",
    )
    self.exit_link.pack(side="left")
    self.exit_link.bind("<Button-1>", lambda e: self.quit_app())

    # Lexemes Table Header Label
    self.lex_label = tk.Label(
        self.left_frame,
        text="Lexemes",
        bg="#2C2C2C",
        fg="#C2C2C2",
        font=("Segoe UI", 9, "bold"),
        anchor="center",
        padx=5,
    )
    self.lex_label.pack(fill="x", pady=(2, 0))

    # Lexemes Treeview Table
    self.lexeme_tree = ttk.Treeview(
        self.left_frame, columns=("lexeme", "classification"), show="headings", height=11
    )
    self.lexeme_tree.heading("lexeme", text="Lexeme", anchor="center")
    self.lexeme_tree.heading("classification", text="Classification", anchor="center")
    self.lexeme_tree.column("lexeme", width=130, anchor="w")
    self.lexeme_tree.column("classification", width=170, anchor="w")
    self.lexeme_tree.pack(fill="both", expand=True, padx=0, pady=0)

    # Symbol Table Header Label
    self.sym_label = tk.Label(
        self.left_frame,
        text="Symbol Table",
        bg="#2C2C2C",
        fg="#C2C2C2",
        font=("Segoe UI", 9, "bold"),
        anchor="center",
        padx=5,
    )
    self.sym_label.pack(fill="x", pady=(5, 0))

    # Symbol Table Treeview Table
    self.symbol_tree = ttk.Treeview(
        self.left_frame, columns=("identifier", "value"), show="headings", height=11
    )
    self.symbol_tree.heading("identifier", text="Identifier", anchor="center")
    self.symbol_tree.heading("value", text="Value", anchor="center")
    self.symbol_tree.column("identifier", width=130, anchor="w")
    self.symbol_tree.column("value", width=170, anchor="w")
    self.symbol_tree.pack(fill="both", expand=True, padx=0, pady=0)

    # RIGHT PANEL 
    self.right_pane = ttk.PanedWindow(self.main_pane, orient="vertical", style="TPanedwindow")
    self.main_pane.add(self.right_pane, weight=3)

    # Code Editor
    self.editor_frame = tk.Frame(self.right_pane, bg="#1F1F1F", bd=0)
    self.right_pane.add(self.editor_frame, weight=2)

    self.code_editor = tk.Text(
        self.editor_frame,
        bg="#1F1F1F",
        fg="#C2C2C2",
        insertbackground="#C2C2C2",
        font=("Consolas", 11),
        bd=0,
        padx=10,
        pady=10,
    )
    self.code_editor.pack(fill="both", expand=True)
    self.code_editor.insert(
        "1.0", "HAI\nI HAS A var ITZ 12\nVISIBLE \"noot noot \" var\nKTHXBYE"
    )

    # Console Output Frame
    self.console_frame = tk.Frame(self.right_pane, bg="#2C2C2C", bd=0)
    self.right_pane.add(self.console_frame, weight=1)

    self.console_output = tk.Text(
        self.console_frame,
        bg="#2C2C2C",
        fg="#4ec9b0",
        font=("Consolas", 10),
        bd=0,
        padx=10,
        pady=10,
    )
    self.console_output.pack(fill="both", expand=True)
    self.console_output.insert("1.0", "noot noot 12\n")
    self.console_output.config(state="disabled")

  def open_file_dialog(self):
    file_path = filedialog.askopenfilename(
        title="Open LOLCODE File", filetypes=[("LOLCODE Files", "*.lol"), ("All Files", "*.*")]
    )
    if file_path:
      with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        self.code_editor.delete("1.0", tk.END)
        self.code_editor.insert("1.0", content)

  def quit_app(self):
    self.root.quit()
    self.root.destroy()

  def on_execute_clicked(self):
    code = self.code_editor.get("1.0", "end-1c")
    tokens, symbols, output = self.bridge.execute_code(code)

    for row in self.lexeme_tree.get_children():
      self.lexeme_tree.delete(row)
    for row in self.symbol_tree.get_children():
      self.symbol_tree.delete(row)

    for lexeme, classification in tokens:
      self.lexeme_tree.insert("", "end", values=(lexeme, classification))

    for identifier, val in symbols:
      self.symbol_tree.insert("", "end", values=(identifier, val))

    self.console_output.config(state="normal")
    self.console_output.delete("1.0", tk.END)
    self.console_output.insert("1.0", output)
    self.console_output.config(state="disabled")


if __name__ == "__main__":
  root = tk.Tk()
  app = LOLCodeIDE(root)
  root.mainloop()