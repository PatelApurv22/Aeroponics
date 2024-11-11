import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog, messagebox, Tk, StringVar, OptionMenu, Button, Label, Entry, Frame, Scrollbar, Canvas, Toplevel, scrolledtext
from tkcalendar import DateEntry
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import statsmodels.api as sm
from tkinter import Toplevel, scrolledtext
import threading


# Global variable for the dataframe
df = None


# Load CSV file and clean column names
def load_file():
    global df
    file_path = filedialog.askopenfilename(
        title="Select a CSV file",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )
    if file_path:
        try:
            df = pd.read_csv(file_path, encoding='ISO-8859-1')
            df.columns = df.columns.str.strip().str.replace('[^A-Za-z0-9 ]+', '', regex=True).str.replace(' ', '_')
            messagebox.showinfo("Success", "File loaded and cleaned successfully!")
            update_column_options()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")

# Update dropdown options based on dataframe columns
def update_column_options():
    if df is not None:
        columns = df.columns.tolist()
        column_var.set(columns[0])
        column_menu['menu'].delete(0, 'end')
        for col in columns:
            column_menu['menu'].add_command(label=col, command=lambda value=col: column_var.set(value))

# Filter data by date range
def filter_data():
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    if 'Timestamp' in df.columns:
        try:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
            filtered_df = df[(df['Timestamp'] >= start_date) & (df['Timestamp'] <= end_date)]
            if filtered_df.empty:
                messagebox.showinfo("Info", "No data available for the selected date range.")
            return filtered_df
        except Exception as e:
            messagebox.showerror("Error", f"Date filtering failed: {str(e)}")
    else:
        messagebox.showerror("Error", "Timestamp column not found!")

# Display column statistics
def calculate_statistics():
    selected_column = column_var.get()
    if selected_column in df.columns:
        stats = df[selected_column].describe()
        stats_window = Toplevel(root)
        stats_window.title("Statistics")
        stats_window.configure(bg="black")
        Label(stats_window, text=f"Statistics for {selected_column}", font=('Arial', 14, 'bold'), fg="white", bg="black").pack(pady=10)
        for stat, value in stats.items():
            Label(stats_window, text=f"{stat}: {value:.4f}", font=('Arial', 12), fg="lightgrey", bg="black").pack()

# Plot selected column against 'Timestamp'
def plot_data():
    selected_column = column_var.get()
    filtered_df = filter_data()
    if filtered_df is not None and selected_column in filtered_df.columns:
        fig, ax = plt.subplots()
        ax.plot(filtered_df['Timestamp'], filtered_df[selected_column], color=color_var.get(), marker=marker_var.get())
        ax.set_xlabel('Timestamp')
        ax.set_ylabel(selected_column)
        ax.legend([selected_column])

        for widget in plot_frame.winfo_children():
            widget.destroy()
        
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        save_button = Button(plot_frame, text="Save Plot", command=lambda: save_plot(fig), **btn_style)
        save_button.pack(pady=5)
    else:
        messagebox.showerror("Error", "Invalid column selected for plotting!")

# Save plot as image
def save_plot(fig):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=(("PNG files", "*.png"), ("All files", "*.*"))
    )
    if file_path:
        try:
            fig.savefig(file_path)
            messagebox.showinfo("Success", f"Plot saved as {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save plot: {str(e)}")
def aeroponics_analysis(ldf):
    # Ensure required columns exist
    if 'Index' in ldf.columns: ldf = ldf.drop(columns=['Index'])
    if 'Timestamp' in ldf.columns: ldf = ldf.drop(columns=['Timestamp'])
    
    # Fill missing values if there are any
    ldf.fillna(ldf.mean(), inplace=True)
    
    # Function to show the correlation matrix
    plt.figure(figsize=(10, 6))
    sns.heatmap(ldf.corr(), annot=True, cmap="coolwarm")
    plt.title("Correlation Matrix")
    plt.show()

    # Function to show the pairplot
    def show_pairplot():
        sns.pairplot(ldf[['Growth', 'Water', 'Surrounding', 'Humidity', 'SR04', 'Gas']])
        # Again, schedule this to run in the main thread
        root.after(0, plt.show)

    # Linear Regression: Predicting Growth based on other variables
    X = ldf[['Water', 'Surrounding', 'Humidity', 'SR04', 'Gas']]
    y = ldf['Growth']
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Initialize and train the model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Predictions and evaluation
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Mean Squared Error: {mse}")
    
    # Regression summary using statsmodels for detailed results
    X_sm = sm.add_constant(X)  # Adding a constant for statsmodels
    model_sm = sm.OLS(y, X_sm).fit()
    summary_text = model_sm.summary().as_text()
    
    # Displaying the summary in a new stats window
    def show_stats_window(summary_text):
        stats_window = Toplevel(root)
        stats_window.title("Regression Summary")
        
        # Create a scrollable text widget
        text_widget = scrolledtext.ScrolledText(stats_window, wrap="word", width=100, height=30)
        text_widget.insert("end", summary_text)
        text_widget.config(state="disabled")  # Make it read-only
        text_widget.pack(padx=10, pady=10)
        
        close_button = Button(stats_window, text="Close", command=stats_window.destroy, bg="#007acc", fg="white", font=('Arial', 10))
        close_button.pack(pady=10)

    # Start threads to display plots
    # threading.Thread(target=show_correlation_matrix).start()
    threading.Thread(show_stats_window(summary_text)).start()
    show_pairplot()
    # Show the stats window immediately
    



# Setup the Tkinter window

root = Tk()
root.title("Advanced Data Plotter")
root.geometry("1200x800")
root.configure(bg="#1e1e1e")

# Styling options
btn_style = {"font": ('Arial', 10, 'bold'), "bg": "#007acc", "fg": "white", "bd": 0, "padx": 10, "pady": 5}
lbl_style = {"font": ('Arial', 12, 'bold'), "fg": "white", "bg": "#1e1e1e"}
entry_style = {"font": ('Arial', 10), "bg": "#3B3B3B", "fg": "white", "bd": 0}

column_var, color_var, marker_var = StringVar(root), StringVar(root), StringVar(root)

# Sidebar for controls
sidebar = Frame(root, bg="#333333", padx=15, pady=15)
sidebar.pack(side="left", fill="y")

# Plot Frame
plot_frame = Frame(root, bg="#1e1e1e", padx=15, pady=15)
plot_frame.pack(side="right", fill="both", expand=True)

# Sidebar Controls
Label(sidebar, text="Controls", font=('Arial', 16, 'bold'), fg="lightgrey", bg="#333333").pack(pady=15)

# Load file button
Button(sidebar, text="Load CSV File", command=load_file, **btn_style).pack(pady=10)

# Column selection
Label(sidebar, text="Select Column to Plot:", **lbl_style).pack(pady=5)
column_menu = OptionMenu(sidebar, column_var, "")
column_menu.config(font=('Arial', 10), bg="#444444", fg="white", bd=0)
column_menu.pack(pady=10)

# Date filtering
Label(sidebar, text="Start Date:", **lbl_style).pack(pady=5)
start_date_entry = DateEntry(sidebar, selectmode='day', date_pattern='dd/mm/yyyy',**entry_style)
start_date_entry.pack(pady=5)
Label(sidebar, text="End Date:", **lbl_style).pack(pady=5)
end_date_entry = DateEntry(sidebar, selectmode='day', date_pattern='dd/mm/yyyy',**entry_style)
end_date_entry.pack(pady=5)

# Plot customization
Label(sidebar, text="Select Line Color:", **lbl_style).pack(pady=5)
color_var.set("blue")
color_menu = OptionMenu(sidebar, color_var, "blue", "red", "green", "black", "orange")
color_menu.config(font=('Arial', 10), bg="#444444", fg="white", bd=0)
color_menu.pack(pady=10)

Label(sidebar, text="Select Marker:", **lbl_style).pack(pady=5)
marker_var.set("o")
marker_menu = OptionMenu(sidebar, marker_var, "o", "x", "^", "s", "None")
marker_menu.config(font=('Arial', 10), bg="#444444", fg="white", bd=0)
marker_menu.pack(pady=10)

# Plot and Statistics buttons
Button(sidebar, text="Plot Data", command=plot_data, **btn_style).pack(pady=10)
Button(sidebar, text="Show Statistics", command=calculate_statistics, **btn_style).pack(pady=10)
# Button(sidebar, text="Analize Growth Rate", command=aeroponics_analysis(df), **btn_style).pack(pady=10)
# Button(sidebar, text="Analyze Growth Rate", command=lambda: aeroponics_analysis(df), **btn_style).pack(pady=10)

Button(sidebar, text="Analyze Growth Rate", command=lambda: aeroponics_analysis(df) if df is not None else messagebox.showerror("Error", "No data loaded!"), **btn_style).pack(pady=10)


# Start the main loop
root.mainloop()
