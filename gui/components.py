import os
import tkinter as tk
from tkinter import ttk

def setup_dark_styles():
  style = ttk.Style()
  style.theme_use("clam")

  style.configure("TPanedwindow", background="#2C2C2C", borderwidth=0)
  style.configure(
      "TPanedwindow.Sash",
      relief="flat",
      sashwidth=3,
      background="#2C2C2C",
      borderwidth=0,
  )

  style.configure(
      "Treeview",
      background="#1F1F1F",
      foreground="#C2C2C2",
      fieldbackground="#1F1F1F",
      rowheight=24,
      borderwidth=0,
  )
  style.map(
      "Treeview",
      background=[("selected", "#2C2C2C")],
      foreground=[("selected", "#C2C2C2")],
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
  )

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
    print("Could not load logo image", e)

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