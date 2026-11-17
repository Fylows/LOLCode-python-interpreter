import os
import tkinter as tk
from tkinter import filedialog, simpledialog, ttk

os.environ["TK_SILENCE_DEPRECATION"] = "1"

from .bridge import InterpreterBridge
from .components import LineNumberCanvas, create_top_bar, setup_dark_styles
from .components import create_top_bar, setup_dark_styles, enable_soft_highlight

class LOLCodeIDE:

  def __init__(self, root):
    self.root = root
    self.root.title("GROUP THREE LOLCODE INTERPRETER")
    self.root.geometry("1200x750")
    self.root.state("zoomed")
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
    self.line_numbers.redraw()
    self.highlight_current_line()

  def request_user_input(self, prompt_text="Enter value:"):
    self.root.update()
    user_val = simpledialog.askstring("LOLCODE Input (GIMMEH)", prompt_text, parent=self.root)
    return user_val if user_val is not None else ""

  def show_partial_output(self, text):
    #print("FLUSH:", repr(text))
    self.console_output.config(state="normal")
    self.console_output.delete("1.0", tk.END)
    self.console_output.insert("1.0", text)
    self.console_output.see(tk.END)
    self.console_output.config(fg="#C2C2C2")
    self.console_output.config(state="disabled")
    self.root.update()  
    

  def highlight_current_line(self, event=None):
    self.code_editor.tag_remove("current_line", "1.0", tk.END)
    cursor_pos = self.code_editor.index("insert")
    line_num = cursor_pos.split(".")[0]
    
    start = f"{line_num}.0"
    end = f"{line_num}.end+1c"
    
    self.code_editor.tag_add("current_line", start, end)
    self.code_editor.tag_lower("current_line")

  def highlight_syntax(self, event=None):
    for tag in ["keyword", "boolean", "function", "string", "number", "comment", "identifier", "conditional"]:
      self.code_editor.tag_remove(tag, "1.0", tk.END)

    content = self.code_editor.get("1.0", "end-1c")
    highlight_tokens = self.bridge.get_highlight_tokens(content)

    for tag_category, start_pos, end_pos in highlight_tokens:
      start = f"1.0 + {start_pos} chars"
      end = f"1.0 + {end_pos} chars"
      self.code_editor.tag_add(tag_category, start, end)

    self.code_editor.edit_modified(False)
    self.highlight_current_line()

  def build_main_layout(self):
    self.body_frame = tk.Frame(self.root, bg="#2C2C2C", bd=0)
    self.body_frame.pack(fill="both", expand=True, padx=4, pady=4)

    # LEFT PANEL
    self.left_frame = tk.Frame(self.body_frame, bg="#2C2C2C", width=320, bd=0)
    self.left_frame.pack(side="left", fill="y")
    self.left_frame.pack_propagate(False)

    # Toolbar 
    self.toolbar_frame = tk.Frame(self.left_frame, bg="#2C2C2C", bd=0)
    self.toolbar_frame.pack(fill="x", padx=8, pady=(0, 8))

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
    self.open_link.bind("<Enter>", lambda e: self.open_link.config(fg="#ffffff"))
    self.open_link.bind("<Leave>", lambda e: self.open_link.config(fg="#C2C2C2"))

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
    self.exit_link.bind("<Enter>", lambda e: self.exit_link.config(fg="#ffffff"))
    self.exit_link.bind("<Leave>", lambda e: self.exit_link.config(fg="#C2C2C2"))

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
    self.lexeme_border_frame = tk.Frame(self.left_frame, bg="#4E4D4D", bd=0)
    self.lexeme_border_frame.pack(fill="both", expand=True, padx=0, pady=0)

    # Lexemes Treeview Table
    self.lexeme_tree = ttk.Treeview(
        self.lexeme_border_frame, columns=("lexeme", "classification"), show="headings", height=11
    )
    self.lexeme_tree.heading("lexeme", text="Lexeme", anchor="center")
    self.lexeme_tree.heading("classification", text="Classification", anchor="center")
    self.lexeme_tree.column("lexeme", width=130, anchor="w", stretch=True)
    self.lexeme_tree.column("classification", width=170, anchor="w", stretch=False)
    self.lexeme_tree.pack(fill="both", expand=True, padx=1, pady=1) 

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
    self.symbol_border_frame = tk.Frame(self.left_frame, bg="#4E4D4D", bd=0)
    self.symbol_border_frame.pack(fill="both", expand=True, padx=0, pady=0)

    # Symbol Table Treeview Table
    self.symbol_tree = ttk.Treeview(
        self.symbol_border_frame, columns=("identifier", "value"), show="headings", height=11
    )
    self.symbol_tree.heading("identifier", text="Identifier", anchor="center")
    self.symbol_tree.heading("value", text="Value", anchor="center")
    self.symbol_tree.column("identifier", width=130, anchor="w", stretch=True)
    self.symbol_tree.column("value", width=170, anchor="w", stretch=False)
    self.symbol_tree.pack(fill="both", expand=True, padx=1, pady=1) 

    enable_soft_highlight(self.lexeme_tree)
    enable_soft_highlight(self.symbol_tree)

    # VERTICAL DIVIDER
    self.v_divider = tk.Frame(
        self.body_frame, bg="#2C2C2C", width=6, cursor="sb_h_double_arrow"
    )
    self.v_divider.pack(side="left", fill="y", padx=2)
    self.v_divider.bind("<B1-Motion>", self.resize_sidebar)

    # RIGHT PANEL 
    self.right_container = tk.Frame(self.body_frame, bg="#2C2C2C", bd=0)
    self.right_container.pack(side="left", fill="both", expand=True)

    # Code Editor
    self.editor_frame = tk.Frame(self.right_container, bg="#1F1F1F", bd=0)
    self.editor_frame.pack(side="top", fill="x", padx=0, pady=0)
    self.editor_frame.config(height=650)
    self.editor_frame.pack_propagate(False)

    self.line_numbers = LineNumberCanvas(
        self.editor_frame, 
        width=45, 
        bg="#1F1F1F",  
        highlightthickness=0, 
        bd=0
    )
    self.line_numbers.pack(side="left", fill="y")

    # Code Editor Text Widget
    self.code_editor = tk.Text(
        self.editor_frame,
        bg="#1F1F1F",
        fg="#C2C2C2",
        insertbackground="#C2C2C2",
        font=("Monaco", 11),
        bd=0,
        highlightthickness=0,
        padx=10,
        pady=10,
    )
    self.code_editor.pack(side="left", fill="both", expand=True)
    self.line_numbers.attach(self.code_editor)

    # Bindings
    self.code_editor.bind("<<Modified>>", lambda e: (self.root.after_idle(self.line_numbers.redraw), self.highlight_syntax(), self.highlight_current_line()))
    self.code_editor.bind("<KeyRelease>", lambda e: (self.root.after_idle(self.line_numbers.redraw), self.highlight_current_line()))
    self.code_editor.bind("<Return>", lambda e: (self.root.after_idle(self.line_numbers.redraw), self.highlight_current_line()))
    self.code_editor.bind("<BackSpace>", lambda e: (self.root.after_idle(self.line_numbers.redraw), self.highlight_current_line()))
    self.code_editor.bind("<Delete>", lambda e: (self.root.after_idle(self.line_numbers.redraw), self.highlight_current_line()))
    self.code_editor.bind("<MouseWheel>", lambda e: self.root.after_idle(self.line_numbers.redraw))
    self.code_editor.bind("<Button-1>", lambda e: self.root.after_idle(self.highlight_current_line))
    for key in ["Up", "Down", "Left", "Right"]:
      self.code_editor.bind(f"<{key}>", lambda e: self.root.after_idle(self.highlight_current_line))

    # color config
    self.code_editor.tag_configure("current_line", background="#322726") 
    self.code_editor.tag_configure("keyword", foreground="#569CD6")      # Blue
    self.code_editor.tag_configure("conditional", foreground="#C586C0")  # Magenta 
    self.code_editor.tag_configure("boolean", foreground="#B5CEA8")      # Light Green
    self.code_editor.tag_configure("function", foreground="#DCDCAA")     # Yellow 
    self.code_editor.tag_configure("string", foreground="#CE9178")       # Orange
    self.code_editor.tag_configure("number", foreground="#B5CEA8")       # Light Green
    self.code_editor.tag_configure("comment", foreground="#838383")      # Gray
    self.code_editor.tag_configure("identifier", foreground="#4EC9B0")   # Cyan

    # HORIZONTAL DIVIDER 
    self.h_divider = tk.Frame(
        self.right_container, bg="#2C2C2C", height=6, cursor="sb_v_double_arrow"
    )
    self.h_divider.pack(side="top", fill="x", pady=2)
    self.h_divider.bind("<Button-1>", self.start_drag_editor)
    self.h_divider.bind("<B1-Motion>", self.resize_editor)

    # Console Output 
    self.console_frame = tk.Frame(self.right_container, bg="#2C2C2C", bd=0)
    self.console_frame.pack(side="top", fill="both", expand=True)

    self.console_output = tk.Text(
        self.console_frame,
        bg="#2C2C2C",
        font=("Consolas", 11),
        bd=0,
        highlightthickness=0,
        padx=10,
        pady=10,
    )
    self.console_output.pack(fill="both", expand=True)
    self.console_output.config(state="disabled")

  # drag and resize helper
  def resize_sidebar(self, event):
    new_width = event.x_root - self.left_frame.winfo_rootx()
    if 150 < new_width < 600:
      self.left_frame.config(width=new_width)

  def start_drag_editor(self, event):
    self._drag_start_y = event.y_root
    self._start_height = self.editor_frame.winfo_height()

  def resize_editor(self, event):
    delta = event.y_root - self._drag_start_y
    new_height = self._start_height + delta
    if 80 < new_height < 650:
      self.editor_frame.config(height=new_height)

  def open_file_dialog(self):
    file_path = filedialog.askopenfilename(
        title="Open LOLCODE File", filetypes=[("LOLCODE Files", "*.lol"), ("All Files", "*.*")]
    )
    if file_path:
      with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        self.code_editor.delete("1.0", tk.END)
        self.code_editor.insert("1.0", content)
        self.highlight_syntax()
        self.line_numbers.redraw()
        self.highlight_current_line()

        # clear console terminal when a new file is open
        self.console_output.config(state="normal")
        self.console_output.delete("1.0", tk.END)
        self.console_output.config(state="disabled")

  def quit_app(self):
    self.root.quit()
    self.root.destroy()

  def on_execute_clicked(self):
    code = self.code_editor.get("1.0", "end-1c")
    tokens, symbols, output = self.bridge.execute_code(
        code, 
        input_callback=self.request_user_input,
        output_callback=self.show_partial_output,
    )

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
    self.console_output.see(tk.END)  

    if output.startswith("Runtime Error:"):
      self.console_output.config(fg="#F14C4B") 
    else:
      self.console_output.config(fg="#C2C2C2")

    self.console_output.config(state="disabled")


if __name__ == "__main__":
  root = tk.Tk()
  app = LOLCodeIDE(root)
  root.mainloop()