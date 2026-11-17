import os
import tkinter as tk
from tkinter import ttk

class LineNumberCanvas(tk.Canvas):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.text_widget = None

  def attach(self, text_widget):
    self.text_widget = text_widget
    self.text_widget.configure(yscrollcommand=self.on_text_scroll)

  def on_text_scroll(self, *args):
    self.redraw()

  def redraw(self, *event):
    self.delete("all")
    if not self.text_widget:
      return

    i = self.text_widget.index("@0,0")
    while True:
      dline = self.text_widget.dlineinfo(i)
      if dline is None:
        break
      y = dline[1]
      line_num = str(i).split(".")[0]
      
      self.create_text(
          35, y + 2, 
          anchor="ne", 
          text=line_num, 
          fill="#858585",  
          font=("Consolas", 8)
      )
      i = self.text_widget.index(f"{i}+1line")

def setup_dark_styles():
  style = ttk.Style()
  style.theme_use("clam")

  style.layout(
      "Treeview.Item",
      [
          (
              "Treeitem.padding",
              {
                  "sticky": "nswe",
                  "children": [
                      ("Treeitem.indicator", {"side": "left", "sticky": ""}),
                      ("Treeitem.image", {"side": "left", "sticky": ""}),
                      ("Treeitem.text", {"side": "left", "sticky": ""}),
                  ],
              },
          )
      ],
  )

  style.configure(
      "Treeview",
      background="#1F1F1F",
      foreground="#C2C2C2",
      fieldbackground="#1F1F1F",
      rowheight=24,
      borderwidth=0,       
      relief="flat",  
      bordercolor="#1F1F1F", 
      lightcolor="#1F1F1F",   
      darkcolor="#1F1F1F",    
      focuscolor="#1F1F1F",
  )
  style.map(
      "Treeview",
      background=[("selected", "#2C2C2C")],
      foreground=[("selected", "#C2C2C2")],
      relief=[("selected", "flat"), ("active", "flat"), ("focus", "flat")],
      borderwidth=[("selected", 0), ("active", 0), ("focus", 0)],
  )

  style.configure(
      "Treeview.Heading",
      background="#2C2C2C",
      foreground="#C2C2C2",
      relief="flat",
      font=("Segoe UI", 9, "bold"),
      anchor="center",
  )
  style.map(
      "Treeview.Heading",
      background=[("active", "#2C2C2C"), ("pressed", "#2C2C2C")],
      foreground=[("active", "#C2C2C2"), ("pressed", "#C2C2C2")],
      focuscolor=[("focus", "#2C2C2C"), ("!focus", "#2C2C2C")],
  )

def enable_soft_highlight(tree, bg="#3A3A3A", fg="#FFFFFF"):
  tree.configure(selectmode="none")
  tree.tag_configure("hl", background=bg, foreground=fg)

  def apply_highlight(item):
    for old_item in tree.tag_has("hl"):
      tree.item(old_item, tags=())
    if item:
      tree.item(item, tags=("hl",))
      tree.see(item)

  def on_click(event):
    if tree.identify_region(event.x, event.y) not in ("cell", "tree"):
      return
    tree.focus_set()
    row = tree.identify_row(event.y)
    if row:
      apply_highlight(row)
    return "break"

  def on_key_down(event):
    children = tree.get_children()
    if not children:
      return
    
    current_highlighted = tree.tag_has("hl")
    current_item = current_highlighted[0] if current_highlighted else None

    if event.keysym == "Down":
      if not current_item:
        next_item = children[0]
      else:
        try:
          idx = children.index(current_item)
          next_item = children[min(idx + 1, len(children) - 1)]
        except ValueError:
          next_item = children[0]
      apply_highlight(next_item)
      return "break"

    elif event.keysym == "Up":
      if not current_item:
        next_item = children[-1]
      else:
        try:
          idx = children.index(current_item)
          next_item = children[max(idx - 1, 0)]
        except ValueError:
          next_item = children[-1]
      apply_highlight(next_item)
      return "break"

  tree.bind("<Button-1>", on_click)
  tree.bind("<KeyPress-Up>", on_key_down)
  tree.bind("<KeyPress-Down>", on_key_down)

def create_top_bar(parent, on_run_callback):
  top_bar = tk.Frame(parent, bg="#2C2C2C", height=42)
  top_bar.pack(side="top", fill="x")
  top_bar.pack_propagate(False)

  logo_img = None
  try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "..", "public", "logo.png")
    if os.path.exists(logo_path):
      raw_img = tk.PhotoImage(file=logo_path)
      logo_img = raw_img.subsample(
          max(1, raw_img.width() // 22), max(1, raw_img.height() // 22)
      )
  except Exception as e:
    print("Could not load logo image:", e)

  if logo_img:
    title_label = tk.Label(
        top_bar,
        text="  GROUP THREE LOLCODE INTERPRETER",
        image=logo_img,
        compound="left",
        bg="#2C2C2C",
        fg="#C2C2C2",
        font=("Segoe UI", 10, "bold"),
    )
    title_label.image = logo_img
  else:
    title_label = tk.Label(
        top_bar,
        text="  GROUP THREE LOLCODE INTERPRETER",
        bg="#2C2C2C",
        fg="#C2C2C2",
        font=("Segoe UI", 10, "bold"),
    )

  title_label.pack(side="left", padx=12, pady=8)

  play_canvas = tk.Canvas(
      top_bar, width=32, height=32, bg="#2C2C2C", highlightthickness=0, cursor="arrow"
  )
  play_canvas.pack(side="right", padx=15)

  play_triangle = play_canvas.create_polygon(
      10,
      8,
      10,
      24,
      24,
      16,
      outline="#C2C2C2",
      fill="#2C2C2C",
      width=1.5,
      smooth=False,
  )

  def on_enter(e):
    play_canvas.itemconfig(play_triangle, outline="#ffffff")

  def on_leave(e):
    play_canvas.itemconfig(play_triangle, outline="#C2C2C2")

  play_canvas.tag_bind(play_triangle, "<Enter>", on_enter)
  play_canvas.tag_bind(play_triangle, "<Leave>", on_leave)
  play_canvas.bind("<Button-1>", lambda e: on_run_callback())
  play_canvas.bind("<Enter>", on_enter)
  play_canvas.bind("<Leave>", on_leave)

  return top_bar